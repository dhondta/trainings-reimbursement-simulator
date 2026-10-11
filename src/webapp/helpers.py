"""Course-table parsing, preset/session-file helpers, and reusable Dash UI/chart-support snippets - the pieces of
business logic that aren't specific to any one callback or to authentication."""
from __future__ import annotations

import csv
import io
from datetime import date, timedelta
from decimal import Decimal, InvalidOperation
from fractions import Fraction
from pathlib import Path

from dash import html

from simulator import BUNDLE_COLUMN, CAP_MODES, CAP_YEARS as LAW_CAP_YEARS, Course, Inactivity, REPAYMENT_MONTHS, \
                      START_DATE_COLUMN, add_months, build_period_status_timeline, build_rendement_periods, \
                      bundle_courses, rendement_end_date, index_period, indexed_max_rate, indexed_min_rate, \
                      calculate_reimbursement, fraction_to_money, indexed_postpone_remainder, money, parse_date, \
                      parse_decimal, schedule_rendement

from . import config
from .auth import session_dir
from .strings import STRINGS


def law_links(text: str, lang: str) -> list:
    """ text, with the mentions of laws as hyperlinks to their official reference (see config.law_segments). """
    return [html.A(segment, href=url, target="_blank", className="text-reset") if url else segment
            for segment, url in config.law_segments(text, lang)]


def date_at(index: int) -> date:
    return add_months(config.SLIDER_START, index)


def detail_status(detail: dict) -> str | None:
    """ The status of a course's amount at the departure date (see calculate_reimbursement's details): "remaining" if
     still owed (even if part of it was forgiven), "expired" if forgiven beyond the maximum total rendement period
     (art. 179, §5), "served" if fully paid off by rendement, or None if the course was not yet taken. """
    if not detail["taken"]:
        return None
    if detail["reimbursement"] > 0:
        return "remaining"
    return "expired" if detail["months_forgiven"] > 0 else "served"


def explanation_items(t: dict, courses, triggering_courses, details: list[dict], timeline_by_course: dict,
                      departure_date: date, total: Decimal, inactivity: list[Inactivity] = (),
                      cap_mode: str | None = None, periods: list | None = None) -> list[str]:
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
        *_cap_mode_items(t, triggering_courses, details, departure_date, total, inactivity, chosen_cap_mode(cap_mode),
                         periods),
    ]
    # Months of non-activity (art. 179, §6) that actually suspended a rendement period, over the whole schedule.
    inactive_months = {run_month for runs in timeline_by_course.values() for run in runs if run["status"] == "inactive"
                       for run_month in _months(run["start"], run["end"])}
    if inactive_months:
        items.append(t["explanation_inactivity"].format(months=len(inactive_months),
                                                        labels=", ".join(dict.fromkeys(i.label for i in inactivity))))
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


def _cap_mode_items(t: dict, triggering_courses, details: list[dict], departure_date: date, total: Decimal,
                    inactivity: list[Inactivity], cap_mode: str, periods: list | None) -> list[str]:
    """ How the maximum total rendement period applies as of the cap mode chosen (art. 179, §5), with the figures it
     is counted on at the departure date: the months of rendement served in the current bunch of periods and when it
     reaches the maximum ("bunch"), or the periods that reached it and the next one to do so ("period"). Followed by
     the amount the other cap mode would give, if different. """
    if periods is None:
        periods = rendement_periods(triggering_courses, inactivity, cap_mode)
    cap_months, date_str, when = config.CAP_YEARS * 12, departure_date.strftime("%d/%m/%y"), ""
    if cap_mode == "bunch":
        bunch, current, reached = 0, 0, None
        # Up to the departure date at least, for the bunch in progress then (none, past the last period).
        until = max(timeline_horizon(periods), add_months(departure_date, 1)) if periods else None
        for month, available, active, _amount in (schedule_rendement(periods, until) if periods else ()):
            if not available:
                bunch = 0  # The bunch is over.
            if active is not None:
                bunch += 1
            if month < departure_date:
                current = bunch
            if reached is None and bunch >= cap_months:
                reached = add_months(month, 1)
        if reached is not None:
            key = "explanation_mode_reached" if reached <= departure_date else "explanation_mode_will_reach"
            when = t[key].format(years=config.CAP_YEARS, when=reached.strftime("%d/%m/%y"))
        items = [t["explanation_mode_bunch"].format(years=config.CAP_YEARS, bunch=current, date=date_str,
                                                    reached=when)]
    else:
        caps = sorted((p.capped_from, p.course.code) for p in periods if p.capped_from is not None)
        n_reached = sum(1 for capped_from, _code in caps if capped_from <= departure_date)
        upcoming = [(capped_from, code) for capped_from, code in caps if capped_from > departure_date]
        if upcoming:
            when = t["explanation_mode_next"].format(code=upcoming[0][1], when=upcoming[0][0].strftime("%d/%m/%y"))
        items = [t["explanation_mode_period"].format(years=config.CAP_YEARS, n_reached=n_reached, date=date_str,
                                                     next=when)]
    if triggering_courses:
        other = next(mode for mode in CAP_MODES if mode != cap_mode)
        other_total, _details = calculate_reimbursement(rendement_periods(triggering_courses, inactivity, other),
                                                        departure_date)
        if other_total != total:
            items.append(t["explanation_mode_compare"].format(other=t["cap_mode_options"][other],
                                                              total=f"{other_total:.2f}", date=date_str,
                                                              current=f"{total:.2f}"))
    return items


def _months(start: date, end: date) -> list[date]:
    """ The 1st of every month from start (a 1st of the month) up to (excluding) end. """
    months = []
    while start < end:
        months.append(start)
        start = add_months(start, 1)
    return months


def final_rendement_completion_day(periods) -> date | None:
    """ The actual last day of rendement: the last calendar day of the final served month, since that month must be
     completed in full - not the 1st of the following month (final_rendement_date's exclusive boundary, used for slider
     sizing)."""
    boundary = final_rendement_date(periods)
    return boundary - timedelta(days=1) if boundary else None


def final_rendement_date(periods) -> date | None:
    """ The 1st of the month following the last served month, i.e. the exclusive boundary at which every period has
     completed its rendement (reimbursement is exactly 0 from this date on) - following the full suspension
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
                         'End Date': row["End Date"].strip(), 'Bundle': (row.get(BUNDLE_COLUMN) or "").strip(),
                         'Start Date': (row.get(START_DATE_COLUMN) or "").strip()})
    return sort_rows_by_date(normalize_rows(rows))


def rows_to_csv(rows: list[dict]) -> str:
    """Serialize Dash table rows back to the CSV format accepted on upload (Course, Price, End Date, Bundle, Start
     Date), skipping fully blank rows. Values are exported as typed, so the file round-trips through load_courses
     unchanged."""
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
             'End Date': normalize(row.get("End Date"), parse_date, lambda d: d.strftime("%d/%m/%y")),
             'Start Date': normalize(row.get("Start Date"), parse_date, lambda d: d.strftime("%d/%m/%y"))}
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


def chosen_cap_mode(cap_mode: str | None) -> str:
    """ The cap mode chosen in the dashboard (art. 179, §5), or the app-wide one (--cap-mode) if none or not a valid one
     (the value comes from the browser). """
    return cap_mode if cap_mode in CAP_MODES else config.CAP_MODE


def rendement_periods(triggering_courses: list[Course], inactivity: list[Inactivity] = (),
                      cap_mode: str | None = None) -> list:
    """ The triggering courses' rendement periods, built with the app-wide maximum total rendement period,
     minimum/maximum rendement rates and postponement of small remainders, and suspended by the given periods of
     non-activity. cap_mode is the one chosen in the dashboard, the app-wide one (--cap-mode) by default. """
    return build_rendement_periods(triggering_courses, cap_months=config.CAP_YEARS * 12,
                                   cap_mode=chosen_cap_mode(cap_mode),
                                   min_rate=config.MIN_RENDEMENT_RATE, max_rate=config.MAX_RENDEMENT_RATE,
                                   postpone_remainder=config.POSTPONE_REMAINDER, inactivity=inactivity)


def rows_to_courses(rows: list[dict], lang: str = config.DEFAULT_LANG) \
        -> tuple[list[Course], list[Inactivity], list[str]]:
    """Parse Dash table rows into Course objects and periods of non-activity (rows with a Start Date), collecting
     per-row errors, then merge the bundled courses (see simulator.bundle_courses). Only the first MAX_COURSES rows are
     considered, whatever the client sent (the table data can be forged), with an error reporting the truncation. A
     bundle named like a course outside of it is reported, and its rows are left out."""
    t, courses, inactivity, errors = STRINGS[lang], [], [], []
    if len(rows) > config.MAX_COURSES:
        errors.append(t["too_many_courses"].format(max=config.MAX_COURSES))
        rows = rows[:config.MAX_COURSES]
    for i, row in enumerate(rows, start=1):
        code = (row.get("Course") or "").strip()
        price_raw = (row.get("Price") or "").strip()
        date_raw = (row.get("End Date") or "").strip()
        bundle = (row.get("Bundle") or "").strip()
        start_raw = (row.get("Start Date") or "").strip()
        if not code and not price_raw and not date_raw and not bundle and not start_raw:
            continue
        if start_raw:
            label = code or t["inactivity_default"]
            if price_raw or bundle:
                errors.append(t["err_inactivity_fields"].format(i=i, code=label))
                continue
            try:
                start_date, end_date = parse_date(start_raw), parse_date(date_raw)
            except ValueError as exc:
                errors.append(t["err_invalid_date"].format(i=i, code=label, exc=exc))
                continue
            if end_date < start_date:
                errors.append(t["err_inactivity_dates"].format(i=i, code=label))
                continue
            inactivity.append(Inactivity(label=label, start_date=start_date, end_date=end_date))
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
        courses.append(Course(code=code, price=price, end_date=end_date, bundle=bundle))
    unbundled_codes = {c.code for c in courses if not c.bundle}
    if clashes := sorted({c.bundle for c in courses if c.bundle in unbundled_codes}):
        errors.append(t["err_bundle_name"].format(names=", ".join(clashes)))
        courses = [c for c in courses if c.bundle not in clashes]
    return bundle_courses(courses), sorted(inactivity, key=lambda i: i.start_date), errors


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


def with_forgiven_runs(periods, timeline_by_course: dict[str, list[dict]]) -> dict[str, list[dict]]:
    """ For display only, the runs of timeline_by_course (the full schedule, see timeline_horizon), each period
     followed by the months forgiven under the maximum total rendement period (art. 179, §5) where they would have
     been served, had they not been forgiven: as "expired" runs (with the amount forgiven), after the months it would
     still have been suspended, as "lapsed" runs (suspended, but already forgiven). These are taken from the same
     schedule without any maximum, which serves the same months until each period's real end, as only the months to be
     served last are forgiven. The bar of a period thus keeps the length it would have had, its real end being where
     its own runs stop. """
    if not periods:
        return dict(timeline_by_course)
    unlimited = build_rendement_periods([p.course for p in periods], cap_months=10 ** 6, cap_mode="bunch",
                                        min_rate=periods[0].min_rate, max_rate=periods[0].max_rate,
                                        postpone_remainder=periods[0].postpone_remainder,
                                        inactivity=periods[0].inactivity)
    unlimited_timeline = build_period_status_timeline(unlimited, timeline_horizon(unlimited))
    served = {id(p): Fraction(0) for p in periods}
    for _month, _available, active, amount in schedule_rendement(periods, timeline_horizon(periods)):
        if active is not None:
            served[id(active)] += amount
    result = {}
    for p in periods:
        runs = [dict(run) for run in timeline_by_course.get(p.course.code, [])]
        forgiven = Fraction(0)
        if p.capped_from is not None:  # The remaining balance is forgiven.
            forgiven = max(Fraction(0), Fraction(p.course.price) - served[id(p)])
        if forgiven > 0:
            real_end, amount = (runs[-1]["end"] if runs else p.start_date), fraction_to_money(forgiven)
            for run in unlimited_timeline.get(p.course.code, []):
                if run["end"] <= real_end:
                    continue
                run = {**run, "start": max(run["start"], real_end)}
                if run["status"] in ("served", "remaining"):
                    run.update(status="expired", amount=amount)
                else:
                    run.update(status="lapsed")
                if runs and runs[-1]["status"] == run["status"] and runs[-1]["end"] == run["start"]:
                    runs[-1]["end"] = run["end"]
                else:
                    runs.append(run)
        result[p.course.code] = runs
    return result


def cut_off_runs(periods, timeline_by_course: dict[str, list[dict]]) -> dict[str, list[dict]]:
    """ For display only, the full schedule of with_forgiven_runs cut off where the rendement periods really end (the
     last month of rendement owed, with the maximum total rendement period - art. 179, §5): a period forgiven sooner
     thus shows the months it would still have been suspended up to there, instead of seemingly ending early. """
    cut_off = max((run["end"] for runs in timeline_by_course.values() for run in runs), default=None)
    if cut_off is None:
        return dict(timeline_by_course)
    return {code: [{**run, "end": min(run["end"], cut_off)} for run in runs if run["start"] < cut_off]
            for code, runs in with_forgiven_runs(periods, timeline_by_course).items()}


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
    """ The status ("served", "suspended" or "inactive") of a period's raw timeline at a specific date. Falls back to
     the last known run's status once at_date is past everything computed, or "suspended" if the period has not
     started yet."""
    for run in runs:
        if run["start"] <= at_date < run["end"]:
            return run["status"]
    if runs and at_date >= runs[-1]["end"]:
        return runs[-1]["status"]
    return "suspended"


def inactivity_runs(inactivity) -> dict[str, list[dict]]:
    """ The periods of non-activity (art. 179, §6) as rows of the rendement periods' timeline, one per label, with their
     exact dates (the end date included) - whereas the rendement periods show the whole months they suspend. """
    runs: dict[str, list[dict]] = {}
    for period in inactivity:
        runs.setdefault(period.label, []).append({"start": period.start_date,
                                                  "end": period.end_date + timedelta(days=1), "status": "inactive"})
    return runs


def timeline_horizon(periods) -> date:
    """ A date far enough in the future that every period has fully unwound its chain of suspensions and completed its
     rendement - i.e. the true end of the suspension "pyramid", not an arbitrary cutoff at the selected departure date.
    Taken from the full schedule (see simulator.rendement_end_date), as periods may last longer than 24 months (e.g.
     with a maximum rendement rate), and at least past every period's start, as a period starting once the maximum total
     rendement period is reached (art. 179, §5) is forgiven at once, without any month served. """
    if not periods:
        return date.today()
    return max([rendement_end_date(periods) or date.min] + [add_months(p.start_date, 1) for p in periods])


def value_card(label: str, value: str | list, *extra: object, font_size: str = "28px") -> list:
    return [html.Div(label, className="fw-semibold text-secondary mb-2"),
            html.Div(value, className="fw-bold text-primary text-nowrap", style={"fontSize": font_size}), *extra]

