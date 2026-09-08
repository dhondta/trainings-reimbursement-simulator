"""Course-table parsing, preset/session-file helpers, and reusable Dash UI/chart-support snippets - the pieces of
business logic that aren't specific to any one callback or to authentication."""
from __future__ import annotations

import csv
from datetime import date, timedelta
from decimal import InvalidOperation
from pathlib import Path

from dash import html

from simulator import Course, REPAYMENT_MONTHS, add_months, build_period_status_timeline, parse_date, parse_decimal

from . import config
from .auth import session_dir
from .strings import STRINGS


def date_at(index: int) -> date:
    return add_months(config.SLIDER_START, index)


def final_rendement_completion_day(periods) -> date | None:
    """ The actual last day of rendement: the last calendar day of the final served month, since that month must be
     completed in full - not the 1st of the following month (final_rendement_date's exclusive boundary, used for slider
     sizing)."""
    boundary = final_rendement_date(periods)
    return boundary - timedelta(days=1) if boundary else None


def final_rendement_date(periods) -> date | None:
    """ The 1st of the month following the last served month, i.e. the exclusive boundary at which every period has
     completed its 24 months of rendement (reimbursement is exactly 0 from this date on) - following the full suspension
     pyramid to its end.
    Used to size the slider's range; see final_rendement_completion_day for the inclusive, human-facing date."""
    if not periods:
        return
    timeline = build_period_status_timeline(periods, timeline_horizon(periods))
    ends = [runs[-1]["end"] for runs in timeline.values() if runs]
    return max(ends) if ends else None


def info_card(label: str, message: str) -> list:
    return [html.Div(label, style={"fontWeight": "bold", "marginBottom": "8px"}),
            html.Div(message, style={"color": "#777"})]


def load_preset_rows(name: str, presets: dict[str, Path]) -> list[dict]:
    path, rows = presets[name], []
    with path.open("r", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            rows.append({'Course': row["Course"].strip(), 'Price': row["Price"].strip(),
                         'End Date': row["End Date"].strip()})
    return rows


def presets_for_session() -> dict[str, Path]:
    """Bundled presets combined with this user's own uploaded CSVs (if they are signed in). A same-named upload shadows
     a bundled preset for that user only - the bundled file on disk is never touched."""
    presets = dict(config.BUNDLED_PRESETS)
    d = session_dir()
    if d is None:
        return presets
    for f in d.iterdir():
        if f.suffix == ".csv":
            presets[f.name] = f
    return presets


def rows_to_courses(rows: list[dict], lang: str = config.DEFAULT_LANG) -> tuple[list[Course], list[str]]:
    """Parse Dash table rows into Course objects, collecting per-row errors."""
    t, courses, errors = STRINGS[lang], [], []
    for i, row in enumerate(rows, start=1):
        code = (row.get("Course") or "").strip()
        price_raw = (row.get("Price") or "").strip()
        date_raw = (row.get("End Date") or "").strip()
        if not code and not price_raw and not date_raw:
            continue
        if not code:
            errors.append(t["err_missing_code"].format(i=i))
            continue
        try:
            price = parse_decimal(price_raw)
            if price < 0:
                raise ValueError("le prix ne peut pas être négatif")
        except (InvalidOperation, ValueError) as exc:
            errors.append(t["err_invalid_price"].format(i=i, code=code, exc=exc))
            continue
        try:
            end_date = parse_date(date_raw)
        except ValueError as exc:
            errors.append(t["err_invalid_date"].format(i=i, code=code, exc=exc))
            continue
        courses.append(Course(code=code, price=price, end_date=end_date))
    return sorted(courses, key=lambda c: c.end_date), errors


def slider_marks(max_months: int) -> dict:
    marks = {}
    for i in range(max_months + 1):
        d = date_at(i)
        if d.month == 1 or i == 0 or i == max_months:
            marks[i] = d.strftime("%Y")
    return marks


def slider_max_months(periods) -> int:
    final_date = final_rendement_date(periods)
    if final_date is None or final_date <= config.SLIDER_START:
        return config.FALLBACK_SLIDER_MONTHS
    return (final_date.year - config.SLIDER_START.year) * 12 + (final_date.month - config.SLIDER_START.month)


def split_at_departure(runs: list[dict], departure_date: date) -> list[dict]:
    """ Recolor, for display only, the portion of every non-suspended ("served") run that falls on or after
     departure_date as "remaining": that time was projected to be served in the full pyramid, but hasn't actually
     happened yet as of the chosen departure date, so it is still owed. Suspended runs are left untouched regardless of
     timing. """
    result = []
    for run in runs:
        if run["status"] != "served" or run["end"] <= departure_date:
            result.append(run)
            continue
        if run["start"] >= departure_date:
            result.append({**run, "status": "remaining"})
            continue
        result.append({"start": run["start"], "end": departure_date, "status": "served"})
        result.append({"start": departure_date, "end": run["end"], "status": "remaining"})
    return result


def status_at_date(runs: list[dict], at_date: date) -> str:
    """ The status ("served" or "suspended") that applies to a period's raw timeline at a specific date. Falls back to
     the last known run's status once at_date is past everything computed, or "suspended" if the period has not
     started yet."""
    for run in runs:
        if run["start"] <= at_date < run["end"]:
            return run["status"]
    if runs and at_date >= runs[-1]["end"]:
        return runs[-1]["status"]
    return "suspended"


def timeline_horizon(periods) -> date:
    """ A date far enough in the future that every period is guaranteed to have fully unwound its chain of suspensions
     and completed its 24 months of rendement - i.e. the true end of the suspension "pyramid", not an arbitrary cutoff
     at the selected departure date.
    Worst case, periods complete strictly one after another (each one suspended until every more recent one is done), so
     len(periods) * 24 months from the earliest start date is always enough. """
    if not periods:
        return date.today()
    earliest_start = min(p.start_date for p in periods)
    return add_months(earliest_start, len(periods) * REPAYMENT_MONTHS + 1)


def value_card(label: str, value: str, *extra: object) -> list:
    return [html.Div(label, style={"fontWeight": "bold", "marginBottom": "8px"}),
            html.Div(value, style={"fontSize": "28px", "fontWeight": "bold", "color": "#2E86AB"}), *extra]

