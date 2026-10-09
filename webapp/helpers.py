"""Course-table parsing, preset/session-file helpers, and reusable Dash UI/chart-support snippets - the pieces of
business logic that aren't specific to any one callback or to authentication."""
from __future__ import annotations

import csv
import io
from datetime import date, timedelta
from decimal import Decimal, InvalidOperation
from pathlib import Path

from dash import html

from simulator import CAP_YEARS as LAW_CAP_YEARS, Course, REPAYMENT_MONTHS, add_months, build_period_status_timeline, \
                      build_rendement_periods, index_period, indexed_max_rate, indexed_min_rate, \
                      indexed_postpone_remainder, money, parse_date, parse_decimal

from . import config
from .auth import session_dir
from .strings import STRINGS


def date_at(index: int) -> date:
    return add_months(config.SLIDER_START, index)


def detail_status(detail: dict) -> str | None:
    """ The status of a course's amount at the departure date (see calculate_reimbursement's details): "remaining" if
     still owed, "expired" if forgiven once the clause expired (art. 179, §5), "served" if fully paid off by rendement,
     or None if the course was not yet taken. """
    if not detail["taken"]:
        return None
    if detail["months_forgiven"] > 0:
        return "expired"
    return "remaining" if detail["reimbursement"] > 0 else "served"


def explanation_items(t: dict, courses, triggering_courses, details: list[dict], timeline_by_course: dict,
                      departure_date: date, total: Decimal) -> list[str]:
    """ How the four criteria of the law concretely apply to a simulation, with the actual numbers behind the departure
     date, plus a note for each setting departing from the law (see the --cap-years / --min-rate / --max-rate /
     --postpone-remainder CLI flags). Shared by
     the dashboard's explanation panel and the PDF report. """
    departure_str = departure_date.strftime("%d/%m/%y")
    n_owing = sum(1 for d in details if d["months_remaining"] > 0)
    n_active = sum(1 for d in details if status_at_date(timeline_by_course[d["course"]], departure_date) == "served")
    capped_rows = [d for d in details if d["months_forgiven"] > 0]
    if capped_rows:
        forgiven_amount = money(sum((d["amount_forgiven"] for d in capped_rows), Decimal("0.00")))
        cap_explanation = t["explanation_cap_some"].format(n_capped=len(capped_rows), amount=f"{forgiven_amount:.2f}",
                                                           years=config.CAP_YEARS)
    else:
        cap_explanation = t["explanation_cap_none"].format(years=config.CAP_YEARS)
    items = [
        t["explanation_threshold"].format(n_triggering=len(triggering_courses), n_total=len(courses),
                                          codes=", ".join(c.code for c in triggering_courses)),
        t["explanation_rendement"].format(date=departure_str, n_owing=n_owing, total=f"{total:.2f}"),
        t["explanation_priority"].format(date=departure_str, n_active=n_active, n_suspended=len(details) - n_active),
        cap_explanation,
    ]
    if config.CAP_YEARS != LAW_CAP_YEARS:
        items.append(t["explanation_cap_custom"].format(years=config.CAP_YEARS, law_years=LAW_CAP_YEARS))
    if config.MIN_RENDEMENT_RATE is not None:
        index_since, _index_until, index_value = index_period(departure_date)
        items.append(t["explanation_min_rate"].format(
            index=index_value, index_since=index_since.strftime("%d/%m/%y"),
            rate=f"{config.MIN_RENDEMENT_RATE:.2f}",
            rate_now=f"{indexed_min_rate(departure_date, config.MIN_RENDEMENT_RATE):.2f}",
            n_shortened=sum(1 for d in details if d["required_months"] < REPAYMENT_MONTHS),
        ))
    if config.MAX_RENDEMENT_RATE is not None:
        index_since, _index_until, index_value = index_period(departure_date)
        items.append(t["explanation_max_rate"].format(
            index=index_value, index_since=index_since.strftime("%d/%m/%y"),
            rate=f"{config.MAX_RENDEMENT_RATE:.2f}",
            rate_now=f"{indexed_max_rate(departure_date, config.MAX_RENDEMENT_RATE):.2f}",
            n_lengthened=sum(1 for d in details if d["required_months"] > REPAYMENT_MONTHS),
        ))
    if config.POSTPONE_REMAINDER is not None:
        items.append(t["explanation_postpone_remainder"].format(
            amount=f"{config.POSTPONE_REMAINDER:.2f}",
            amount_now=f"{indexed_postpone_remainder(departure_date, config.POSTPONE_REMAINDER):.2f}",
        ))
    return items


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


def icon_label(icon: str, text: str) -> list:
    """ Button content: a Bootstrap icon (e.g. "upload" for bi-upload) followed by its label. """
    return [html.I(className=f"bi bi-{icon} me-2"), text]


def info_card(label: str, message: str) -> list:
    return [html.Div(label, className="fw-semibold text-secondary mb-2"), html.Div(message, className="text-muted")]


def load_preset_rows(name: str, presets: dict[str, Path]) -> list[dict]:
    path, rows = presets[name], []
    with path.open("r", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            if len(rows) >= config.MAX_COURSES:
                break
            rows.append({'Course': row["Course"].strip(), 'Price': row["Price"].strip(),
                         'End Date': row["End Date"].strip()})
    return sort_rows_by_date(normalize_rows(rows))


def rows_to_csv(rows: list[dict]) -> str:
    """Serialize Dash table rows back to the CSV format accepted on upload (Course, Price, End Date), skipping fully
     blank rows. Values are exported as typed, so the file round-trips through load_courses unchanged."""
    buffer = io.StringIO()
    writer = csv.writer(buffer, lineterminator="\n")
    writer.writerow(config.COURSE_COLUMNS)
    for row in rows[:config.MAX_COURSES]:
        values = [(row.get(col) or "").strip() for col in config.COURSE_COLUMNS]
        if any(values):
            writer.writerow(values)
    return buffer.getvalue()


def normalize_rows(rows: list[dict]) -> list[dict]:
    """ Course-table rows with their values in the table's canonical format: prices with two decimals and a dot (e.g.
     "4.174,85 €" -> "4174.85"), dates as DD/MM/YY (e.g. "2024-11-07" -> "07/11/24"). A value that can't be parsed is
     left as typed, so that rows_to_courses still reports it. """
    def normalize(value, parse, fmt):
        try:
            return fmt(parse(value)) if (value or "").strip() else value
        except (ValueError, ArithmeticError):
            return value
    return [{**row,
             'Price': normalize(row.get("Price"), parse_decimal, lambda v: f"{money(v):.2f}"),
             'End Date': normalize(row.get("End Date"), parse_date, lambda d: d.strftime("%d/%m/%y"))}
            for row in rows]


def presets_for_session() -> dict[str, Path]:
    """Bundled presets combined with this user's own uploaded CSVs (if they are signed in). A same-named upload shadows
     a bundled preset for that user only - the bundled file on disk is never touched."""
    presets = dict(config.BUNDLED_PRESETS)
    d = session_dir()
    if d is None:
        return presets
    for f in d.iterdir():
        if config.is_course_csv(f):
            presets[f.name] = f
    return presets


def rendement_periods(triggering_courses: list[Course]) -> list:
    """ The triggering courses' rendement periods, built with the app-wide validity cap, minimum/maximum rendement
     rates and postponement of small remainders. """
    return build_rendement_periods(triggering_courses, cap_months=config.CAP_YEARS * 12,
                                   min_rate=config.MIN_RENDEMENT_RATE, max_rate=config.MAX_RENDEMENT_RATE,
                                   postpone_remainder=config.POSTPONE_REMAINDER)


def rows_to_courses(rows: list[dict], lang: str = config.DEFAULT_LANG) -> tuple[list[Course], list[str]]:
    """Parse Dash table rows into Course objects, collecting per-row errors. Only the first MAX_COURSES rows are
     considered, whatever the client sent (the table data can be forged), with an error reporting the truncation."""
    t, courses, errors = STRINGS[lang], [], []
    if len(rows) > config.MAX_COURSES:
        errors.append(t["too_many_courses"].format(max=config.MAX_COURSES))
        rows = rows[:config.MAX_COURSES]
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
                raise ValueError(t["err_negative_price"])
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


def slider_marks(min_months: int, max_months: int) -> dict:
    """ One mark per year, on January, labeled with the year only (the exact selected date is shown above the slider).
     Falls back to marking the range's start if it spans no January at all. """
    marks = {i: date_at(i).strftime("%Y") for i in range(min_months, max_months + 1) if date_at(i).month == 1}
    return marks or {min_months: date_at(min_months).strftime("%Y")}


def slider_min_months(periods) -> int:
    """ The (zero or negative) slider index of the earliest rendement period's start, so that the departure date can be
     set back in time to the very beginning of the rendement periods; index 0 (next month) stays the default. """
    if not periods:
        return 0
    earliest_start = min(p.start_date for p in periods)
    return min(0, (earliest_start.year - config.SLIDER_START.year) * 12
                  + (earliest_start.month - config.SLIDER_START.month))


def slider_max_months(periods) -> int:
    final_date = final_rendement_date(periods)
    if final_date is None or final_date <= config.SLIDER_START:
        return config.FALLBACK_SLIDER_MONTHS
    return (final_date.year - config.SLIDER_START.year) * 12 + (final_date.month - config.SLIDER_START.month)


def sort_rows_by_date(rows: list[dict]) -> list[dict]:
    """ Course-table rows sorted by ascending end date. The sort is stable (same-date rows keep their order), and rows
     whose date is empty or not (yet) valid - e.g. a freshly added row - stay at the bottom, in their current order. """
    def key(row):
        try:
            return 0, parse_date(row.get("End Date") or "")
        except ValueError:
            return 1, date.min
    return sorted(rows, key=key)


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


def value_card(label: str, value: str | list, *extra: object, font_size: str = "28px") -> list:
    return [html.Div(label, className="fw-semibold text-secondary mb-2"),
            html.Div(value, className="fw-bold text-primary text-nowrap", style={"fontSize": font_size}), *extra]

