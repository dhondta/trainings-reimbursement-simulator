from __future__ import annotations

import csv
import sys
from argparse import ArgumentParser
from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP
from fractions import Fraction
from pathlib import Path


# =================================================== CONFIGURATION ====================================================
BASE_THRESHOLD = Decimal("5000.00")
REPAYMENT_MONTHS = 24
# Optional minimum rendement rate, in € per month of service (NOT part of the law, which always spreads the degression
#  over REPAYMENT_MONTHS, i.e. price / 24 per month): when set, each month served pays off at least this amount of the
#  course's price, so that a cheap triggering course no longer ties the employee down for the full 24 months. Like
#  BASE_THRESHOLD, it is a base amount, indexed with the coefficient applicable in the month being served - so the rate
#  rises with the index during a rendement period. None (the default) keeps the behavior prescribed by the current law.
MIN_RENDEMENT_RATE: Decimal | None = None
# Optional maximum rendement rate, in € per month of service (NOT part of the law either): when set, each month served
#  pays off at most this amount of the course's price, so that an expensive triggering course ties the employee down for
#  longer than 24 months. Indexed like MIN_RENDEMENT_RATE, and must be strictly greater than it when both are set. None
#  (the default) keeps the behavior prescribed by the current law.
MAX_RENDEMENT_RATE: Decimal | None = None
# Optional postponement of a small remainder, in € (NOT part of the law either): when the last month of a rendement
#  period would only pay off less than this amount, the remainder is merged into the previous month instead, so that the
#  period ends one month earlier rather than tying the employee down for a full month over a small amount. That month
#  may then exceed the maximum rendement rate, if any. Like BASE_THRESHOLD, it is a base amount, indexed with the
#  coefficient applicable in the month concerned. None (the default) keeps the behavior prescribed by the current law.
POSTPONE_REMAINDER: Decimal | None = None
# Maximum validity period of a rendement period (art. 179, §5): once this delay has elapsed since the period started,
#  the clause no longer produces any effect — the reimbursement obligation for this course lapses, even if the 24 months
#  of rendement have not been served.
CAP_YEARS = 15
CAP_MONTHS = CAP_YEARS * 12
# Indexation coefficients used for the threshold, one row per period ("Start Date", "Index Value"): each period ends the
#  day before the next one starts, and the last one is open-ended. Append a row to this CSV when a new index applies.
# Source: https://bosa.belgium.be/fr/themes/travailler-dans-la-fonction-publique/remuneration-et-avantages/traitement/indexation-0
INDEX_VALUES_CSV = Path(__file__).parent / "index_values.csv"
REQUIRED_INDEX_COLUMNS = {"Start Date", "Index Value"}
REQUIRED_COLUMNS = {"Course", "Price", "End Date"}
# Optional column grouping courses into bundles: the courses sharing a same non-empty value count as a single course
#  (see bundle_courses), with a single rendement period.
BUNDLE_COLUMN = "Bundle"


# ==================================================== DATA MODELS =====================================================
@dataclass(frozen=True)
class Course:
    code: str
    price: Decimal
    end_date: date
    bundle: str = ""                         # Name of the bundle this course belongs to, if any (see bundle_courses).
    members: tuple[str, ...] = ()            # For a bundle, the codes of the courses it groups.
    
    @property
    def label(self) -> str:
        """ The course code, followed for a bundle by the codes of the courses it groups. """
        return f"{self.code} ({' + '.join(self.members)})" if self.members else self.code


@dataclass
class Rendement:
    """ A rendement period, accounted as a balance: the course's price, paid off month after month of service at the
     rate given by monthly_rate (price / 24 as of the law, so exactly 24 months). Amounts are kept as exact fractions,
     so that 24 × price / 24 adds up to the price to the cent. """
    course: Course
    start_date: date                         # First day of the full month following the course.
    months_served: int = 0                   # Number of rendement months actually completed.
    served: Fraction = Fraction(0)           # Part of the price already paid off by these months of rendement.
    cap_months: int = CAP_MONTHS             # Validity period of the clause for this period (art. 179, §5).
    min_rate: Decimal | None = None          # Base (non-indexed) minimum rendement rate, if any.
    max_rate: Decimal | None = None          # Base (non-indexed) maximum rendement rate, if any.
    postpone_remainder: Decimal | None = None  # Base (non-indexed) remainder below which a last month is merged
                                               #  into the previous one, if any.
    
    @property
    def balance(self) -> Fraction:
        return max(Fraction(0), Fraction(self.course.price) - self.served)
    
    @property
    def completed(self) -> bool:
        return self.balance == 0
    
    @property
    def cap_date(self) -> date:
        """Date from which the clause no longer produces any effect for
        this period, regardless of how many months have been served."""
        return add_months(self.start_date, self.cap_months)
    
    def capped_at(self, at_date: date) -> bool:
        return at_date >= self.cap_date
    
    def monthly_rate(self, month: date) -> Fraction:
        """ Part of the price paid off by one month of rendement served in the given month: price / 24 as of the law,
         raised to the minimum rendement rate and lowered to the maximum rendement rate indexed at that month, if any. """
        rate = Fraction(self.course.price) / REPAYMENT_MONTHS
        if self.min_rate is not None:
            rate = max(rate, Fraction(indexed_min_rate(month, self.min_rate)))
        if self.max_rate is not None:
            rate = min(rate, Fraction(indexed_max_rate(month, self.max_rate)))
        return rate
    
    def amount_due(self, balance: Fraction, month: date) -> Fraction:
        """ Part of the given balance paid off by one month of rendement served in the given month: the monthly rate,
         or the whole balance if it is lower - or if what would be left afterwards is a small remainder (see
         is_small_remainder; it is then merged into this month). """
        rate = self.monthly_rate(month)
        if self.is_small_remainder(balance - rate, month):
            return balance
        return min(balance, rate)
    
    def is_small_remainder(self, amount: Fraction, month: date) -> bool:
        """ Whether a last month paying off the given amount in the given month is to be merged into the previous month
         served (postpone_remainder set and amount below it, indexed at that month). """
        return self.postpone_remainder is not None \
               and amount < Fraction(indexed_postpone_remainder(month, self.postpone_remainder))
    
    def months_to_clear(self, balance: Fraction, from_month: date) -> int:
        """ Number of consecutive months of rendement, starting from from_month, needed to pay off the given balance.
         Months past the last known index use its coefficient (the last indexation period is open-ended). """
        months, month, amount = 0, from_month, Fraction(0)
        while balance > 0:
            amount = self.amount_due(balance, month)
            balance -= amount
            months, month = months + 1, next_month(month)
        # A small last month (e.g. once the index has risen) is merged into the previous one.
        if months > 1 and self.is_small_remainder(amount, add_months(month, -1)):
            months -= 1
        return months


# ====================================================== HELPERS =======================================================
def add_months(d: date, months: int) -> date:
    """ Adds calendar months to a date. """
    year = d.year + (d.month - 1 + months) // 12
    month = (d.month - 1 + months) % 12 + 1
    next_month = date(year + 1, 1, 1) if month == 12 else date(year, month + 1, 1)
    return date(year, month, min(d.day, (next_month - timedelta(days=1)).day))


def first_day_next_month(d: date) -> date:
    """ First day of the full month following the end of the course. """
    if d.month == 12:
        return date(d.year + 1, 1, 1)
    return date(d.year, d.month + 1, 1)


def index_coefficient(at_date: date) -> Decimal:
    return index_period(at_date)[2]


def index_period(at_date: date) -> tuple[date, date | None, Decimal]:
    """ The indexation period (start, end or None if open-ended, coefficient) applicable at at_date. """
    for start, end, coefficient in INDEX_VALUES:
        if at_date >= start and (end is None or at_date <= end):
            return start, end, coefficient
    raise ValueError(f"No indexation coefficient defined for {at_date.strftime('%d/%m/%Y')}")


def indexed_threshold(at_date: date) -> Decimal:
    coefficient = index_coefficient(at_date)
    return money(BASE_THRESHOLD * coefficient)


def indexed_min_rate(at_date: date, min_rate: Decimal | None = MIN_RENDEMENT_RATE) -> Decimal | None:
    """ The minimum rendement rate (a base amount, like BASE_THRESHOLD) indexed with the coefficient applicable at
     at_date, or None if no minimum rate is set. """
    if min_rate is None:
        return None
    if min_rate <= 0:
        raise ValueError("minimum rendement rate must be strictly positive")
    return money(min_rate * index_coefficient(at_date))


def indexed_max_rate(at_date: date, max_rate: Decimal | None = MAX_RENDEMENT_RATE) -> Decimal | None:
    """ The maximum rendement rate (a base amount, like BASE_THRESHOLD) indexed with the coefficient applicable at
     at_date, or None if no maximum rate is set. """
    if max_rate is None:
        return None
    if max_rate <= 0:
        raise ValueError("maximum rendement rate must be strictly positive")
    return money(max_rate * index_coefficient(at_date))


def indexed_postpone_remainder(at_date: date, remainder: Decimal | None = POSTPONE_REMAINDER) -> Decimal | None:
    """ The remainder below which a last month is merged into the previous one (a base amount, like BASE_THRESHOLD)
     indexed with the coefficient applicable at at_date, or None if no such remainder is set. """
    if remainder is None:
        return None
    if remainder <= 0:
        raise ValueError("remainder to postpone must be strictly positive")
    return money(remainder * index_coefficient(at_date))


def fraction_to_decimal(value: Fraction) -> Decimal:
    return Decimal(value.numerator) / Decimal(value.denominator)


def fraction_to_money(value: Fraction) -> Decimal:
    return money(fraction_to_decimal(value))


def validate_rates(min_rate: Decimal | None, max_rate: Decimal | None) -> None:
    """ Checks the optional minimum and maximum rendement rates: each strictly positive, and the maximum strictly
     greater than the minimum when both are set. Raises ValueError otherwise. """
    if min_rate is not None and min_rate <= 0:
        raise ValueError("minimum rendement rate must be strictly positive")
    if max_rate is not None and max_rate <= 0:
        raise ValueError("maximum rendement rate must be strictly positive")
    if min_rate is not None and max_rate is not None and max_rate <= min_rate:
        raise ValueError(f"maximum rendement rate ({max_rate}) must be strictly greater than the minimum rendement "
                         f"rate ({min_rate})")


def money(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def next_month(d: date) -> date:
    """ Returns the first day of the following month. """
    if d.month == 12:
        return date(d.year + 1, 1, 1)
    return date(d.year, d.month + 1, 1)


def parse_date(s: str) -> date:
    s = s.strip()
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%d/%m/%y"):
        try:
            from datetime import datetime
            return datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    raise ValueError(f"Unrecognized date format: {s!r} (use YYYY-MM-DD, DD/MM/YYYY, DD-MM-YYYY or DD/MM/YY)")


def parse_decimal(value: str) -> Decimal:
    """ Accepts in particular: 4174.85 | 4174,85 | 4.174,85 | 4,174.85 as well as values containing the € symbol. """
    value = value.strip()
    if not value:
        raise ValueError("empty value")
    value = value.replace("€", "").replace(" ", "")
    if "." in value and "," in value:
        if value.rfind(",") > value.rfind("."):  # European format: 4.174,85
            value = value.replace(".", "").replace(",", ".")
        else:  # Anglo-Saxon format: 4,174.85
            value = value.replace(",", "")
    elif "," in value:
        value = value.replace(",", ".")
    return Decimal(value)


# ===================================================== MAIN LOGIC =====================================================
def active_rendement(periods: list[Rendement], month: date) -> tuple[Rendement, Decimal] | None:
    """ The period actively accruing rendement in the given month (in the full pyramid), with the amount of its price
     paid off that month, or None if no period is being served. """
    for current, _available, active, amount in schedule_rendement(periods, next_month(month)):
        if current == month and active is not None:
            return active, fraction_to_money(amount)
    return None


def schedule_rendement(periods: list[Rendement], until: date):
    """ Month by month from the first period's start up to (excluding) until, yields (month, available, active, amount):
     the periods available that month (started, not yet paid off, clause not expired - art. 179, §5), most recent
     first, the active one among them (the most recent: it suspends the older ones; None if none is available) and the
     part of its price paid off that month. Works on local balances: the periods themselves are not modified. """
    if not periods:
        return
    yield from _schedule_months(periods, until, _postponed_remainders(periods))


def _postponed_remainders(periods: list[Rendement]) -> dict[int, set[date]]:
    """ For the periods with postpone_remainder, the months in which they must pay off their whole balance, so that a
     small last month is merged into the previous month served - even when a more recent period was served in between
     (the remainder, deferred until it completes, may then fall below a postpone_remainder raised by the index
     meanwhile).
     Found by simulating the whole schedule until every period ends, then forcing each small last month into the
     previous one and simulating again, until no small last month is left (each pass forces at least one more merge,
     each one shortening a period, so this terminates). """
    forced: dict[int, set[date]] = {id(p): set() for p in periods}
    if not any(p.postpone_remainder is not None for p in periods):
        return forced
    while True:
        payments: dict[int, list[tuple[date, Fraction]]] = {id(p): [] for p in periods}
        served = {id(p): Fraction(0) for p in periods}
        for current, _available, active, amount in _schedule_months(periods, None, forced):
            if active is not None:
                payments[id(active)].append((current, amount))
                served[id(active)] += amount
        changed = False
        for p in periods:
            months = payments[id(p)]
            # Only a period actually completed by its last month (not one cut short by its cap) has a remainder to merge.
            if len(months) < 2 or served[id(p)] < Fraction(p.course.price):
                continue
            (previous_month, _), (last_month, last_amount) = months[-2], months[-1]
            if p.is_small_remainder(last_amount, last_month):
                forced[id(p)].add(previous_month)
                changed = True
        if not changed:
            return forced


def _schedule_months(periods: list[Rendement], until: date | None, forced: dict[int, set[date]]):
    """ See schedule_rendement; with until None, runs until no period is left to be served. forced gives, per period,
     the months in which it pays off its whole balance (see _postponed_remainders). """
    current = min(p.start_date for p in periods)
    served = {id(p): Fraction(0) for p in periods}
    last_start = max(p.start_date for p in periods)
    while until is None or current < until:
        available = [p for p in periods if p.start_date <= current and served[id(p)] < Fraction(p.course.price) \
                                           and not p.capped_at(current)]
        if until is None and not available and current > last_start:
            return
        available.sort(key=lambda p: p.start_date, reverse=True)
        active, amount = (available[0] if available else None), Fraction(0)
        if active is not None:
            balance = Fraction(active.course.price) - served[id(active)]
            amount = balance if current in forced[id(active)] else active.amount_due(balance, current)
            served[id(active)] += amount
        yield current, available, active, amount
        current = next_month(current)


def build_period_status_timeline(periods: list[Rendement], as_of_date: date) -> dict[str, list[dict]]:
    """ For each period, returns the chronological list of monthly segments grouped by status: 'served' (rendement
     active that month), 'suspended' (a more recent course takes priority), or 'remaining' (months still owed, projected
     past as_of_date for lack of a longer simulation).

    A period stays 'suspended' until ALL periods more recent than it have themselves paid off their price in rendement
     (or until as_of_date, if that comes first, or until its own clause expires — art. 179, §5). To obtain the real end
     date of each period (and thus an untruncated, pyramid-shaped timeline), the caller must supply an as_of_date far
     enough ahead to cover the full chain of suspensions.

    Past its own cap_date, a period no longer appears among the available ones (the clause has expired) and no
     'remaining' segment is added for it: the outstanding balance is wiped out, not carried forward.

    Does not modify the periods (local counters, see schedule_rendement).
    """
    if not periods:
        return {}
    runs: dict[int, list[dict]] = {id(p): [] for p in periods}
    served = {id(p): Fraction(0) for p in periods}
    def add_month(period, month_start, status):
        month_end = next_month(month_start)
        period_runs = runs[id(period)]
        if period_runs and period_runs[-1]["status"] == status and period_runs[-1]["end"] == month_start:
            period_runs[-1]["end"] = month_end
        else:
            period_runs.append({'start': month_start, 'end': month_end, 'status': status})
    for current, available, active, amount in schedule_rendement(periods, as_of_date):
        if active is not None:
            served[id(active)] += amount
        for p in available:
            add_month(p, current, "served" if p is active else "suspended")
    result = {}
    for p in periods:
        period_runs = list(runs[id(p)])
        if not p.capped_at(as_of_date):
            start = (period_runs[-1]["end"] if period_runs else p.start_date)
            balance = max(Fraction(0), Fraction(p.course.price) - served[id(p)])
            if months_remaining := p.months_to_clear(balance, start):
                period_runs.append({'start': start, 'end': add_months(start, months_remaining), 'status': "remaining"})
        result[p.course.code] = period_runs
    return result


def build_rendement_periods(triggering_courses: list[Course], cap_months: int = CAP_MONTHS,
                            min_rate: Decimal | None = MIN_RENDEMENT_RATE,
                            max_rate: Decimal | None = MAX_RENDEMENT_RATE,
                            postpone_remainder: Decimal | None = POSTPONE_REMAINDER) -> list[Rendement]:
    validate_rates(min_rate, max_rate)
    if postpone_remainder is not None and postpone_remainder <= 0:
        raise ValueError("remainder to postpone must be strictly positive")
    periods = []
    for c in triggering_courses:
        periods.append(Rendement(course=c, start_date=first_day_next_month(c.end_date), cap_months=cap_months,
                                 min_rate=min_rate, max_rate=max_rate, postpone_remainder=postpone_remainder))
    return sorted(periods, key=lambda p: p.start_date)


def calculate_reimbursement(periods: list[Rendement], departure_date: date) -> tuple[Decimal, list[dict]]:
    if not periods:
        return Decimal("0.00"), []
    # Each rendement period has its price STILL TO BE PAID OFF in months of rendement.
    # When a new period starts:
    #     new period = active
    #     old period = suspended
    # When the new period ends, the old one resumes with its previous balance.
    for _current, _available, active, amount in schedule_rendement(periods, departure_date):
        if active is not None:
            active.months_served += 1
            active.served += amount
    # Financial calculation
    details, total = [], Decimal("0.00")
    for period in periods:
        # Once the clause's validity period has elapsed, the obligation lapses: nothing more is owed for this course,
        #  even if its price has not been fully paid off. The amount (and projected months) thus forgiven are exposed
        #  explicitly (amount_forgiven, months_forgiven) so the total stays auditable: a zero balance because the
        #  service is complete can be distinguished from a zero balance because it was forgiven under art. 179, §5.
        # A course not yet completed at the departure date (e.g. a departure date in the past, before a later course)
        #  was never followed, so it cannot be owed.
        taken = period.course.end_date < departure_date
        capped = period.capped_at(departure_date)
        balance = fraction_to_money(period.balance)
        # Months still owed, projected from the departure date on (at the rate(s) of the months to come).
        uncapped_remaining = period.months_to_clear(period.balance, departure_date) if taken else 0
        remaining = 0 if capped else uncapped_remaining
        reimbursement = Decimal("0.00") if capped or not taken else balance
        total += reimbursement
        details.append({
            "course":           period.course.code,
            "course_end":       period.course.end_date,
            "rendement_start":  period.start_date,
            "cost":             period.course.price,
            "required_months":  period.months_served + uncapped_remaining,
            "monthly_rate":     None if period.completed else fraction_to_money(period.monthly_rate(departure_date)),
            "min_rate":         period.min_rate,
            "max_rate":         period.max_rate,
            "months_served":    period.months_served,
            "months_remaining": remaining,
            "reimbursement":    reimbursement,
            "taken":            taken,
            "capped":           capped,
            "months_forgiven":  uncapped_remaining if capped else 0,
            # Unrounded, so that a sum of forgiven amounts is only rounded once.
            "amount_forgiven":  fraction_to_decimal(period.balance) if capped else Decimal("0"),
        })
    return money(total), details


def bundle_courses(courses: list[Course]) -> list[Course]:
    """ Merges the courses sharing a same bundle into a single course, named after the bundle: its price is the sum of
     theirs and its end date the latest of theirs, so that it is tested against the threshold as one course and, if it
     triggers, gets a single rendement period starting after its last course. Courses without a bundle are kept as is.
     Raises ValueError if a bundle is named like a course outside of it (both would then be indistinguishable). """
    groups: dict[str, list[Course]] = {}
    result = []
    for course in courses:
        if course.bundle:
            groups.setdefault(course.bundle, []).append(course)
        else:
            result.append(course)
    if clashes := sorted(set(groups) & {c.code for c in result}):
        raise ValueError(f"bundle(s) named like a course outside of them: {', '.join(clashes)}")
    for name, members in groups.items():
        result.append(Course(code=name, price=sum((c.price for c in members), Decimal("0.00")),
                             end_date=max(c.end_date for c in members), members=tuple(c.code for c in members)))
    return sorted(result, key=lambda c: c.end_date)


def determine_triggering_courses(courses: list[Course]) -> tuple[list[Course], list[dict]]:
    audit, triggering = [], []
    for course in courses:
        if course.end_date < date(2013, 9, 30):  # Effective date of application of the law of reference.
            continue
        window = [c for c in courses if add_months(course.end_date, -24) <= c.end_date <= course.end_date]
        cumulative_cost = sum((c.price for c in window), Decimal("0.00"))
        threshold = indexed_threshold(course.end_date)
        exceeds = (cumulative_cost > threshold)
        audit.append({
            "course":          course,
            "window_start":    add_months(course.end_date, -24),
            "window_end":      course.end_date,
            "cumulative_cost": money(cumulative_cost),
            "threshold":       threshold,
            "exceeds":         exceeds,
            "window_courses":  window,
        })
        if exceeds:
            triggering.append(course)
    return triggering, audit


def load_courses(csv_path: Path) -> list[Course]:
    """ The courses of a CSV file, as listed (with their bundle, if any, from the optional BUNDLE_COLUMN): pass them
     through bundle_courses before simulating. """
    if not csv_path.exists():
        raise FileNotFoundError(f"file not found: {csv_path}")
    courses = []
    with csv_path.open("r", encoding="utf-8-sig", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        if reader.fieldnames is None:
            raise ValueError("input CSV file has no header")
        if missing := (REQUIRED_COLUMNS - set(reader.fieldnames)):
            raise ValueError(f"missing columns: {', '.join(sorted(missing))}")
        for line_number, row in enumerate(reader, start=2):
            try:
                if not (code := row["Course"].strip()):
                    raise ValueError("empty course")
                if (price := parse_decimal(row["Price"])) < 0:
                    raise ValueError("price cannot be negative")
                courses.append(Course(code=code, price=price, end_date=parse_date(row["End Date"]),
                                      bundle=(row.get(BUNDLE_COLUMN) or "").strip()))
            except Exception as exc:
                raise ValueError(f"error at line {line_number}: {exc}") from exc
    if not courses:
        raise ValueError("input CSV file has no data")
    bundle_courses(courses)  # Validates the bundles.
    return sorted(courses, key=lambda c: c.end_date)


def load_index_values(csv_path: Path) -> list[tuple[date, date | None, Decimal]]:
    """ Reads the indexation CSV into (start, end, coefficient) periods, sorted by start date: each period's end is
     deduced as the day before the next period's start, and the last period has no end (None). """
    if not csv_path.exists():
        raise FileNotFoundError(f"indexation file not found: {csv_path}")
    starts = {}
    with csv_path.open("r", encoding="utf-8-sig", newline="") as csv_file:
        reader = csv.DictReader(csv_file)
        if reader.fieldnames is None:
            raise ValueError(f"indexation CSV file has no header: {csv_path}")
        if missing := (REQUIRED_INDEX_COLUMNS - set(reader.fieldnames)):
            raise ValueError(f"missing columns in {csv_path}: {', '.join(sorted(missing))}")
        for line_number, row in enumerate(reader, start=2):
            try:
                start = parse_date(row["Start Date"])
                if (coefficient := parse_decimal(row["Index Value"])) <= 0:
                    raise ValueError("index value must be positive")
                if start in starts:
                    raise ValueError(f"duplicate start date {start.strftime('%d/%m/%Y')}")
                starts[start] = coefficient
            except Exception as exc:
                raise ValueError(f"error in {csv_path} at line {line_number}: {exc}") from exc
    if not starts:
        raise ValueError(f"indexation CSV file has no data: {csv_path}")
    ordered = sorted(starts.items())
    ends = [next_start - timedelta(days=1) for next_start, _ in ordered[1:]] + [None]
    return [(start, end, coefficient) for (start, coefficient), end in zip(ordered, ends)]
INDEX_VALUES = load_index_values(INDEX_VALUES_CSV)


def print_triggering_courses(audit: list[dict]) -> None:
    print("\nTRAININGS & THRESHOLD TEST" + "=" * 120)
    for row in audit:
        course = row["course"]
        status = "TRIGGERS" if row["exceeds"] else "DOES NOT TRIGGER"
        print(f"{course.label:8} {course.end_date.strftime('%d/%m/%Y')}  cumul = {row['cumulative_cost']:>10.2f} €  "
            f"threshold = {row['threshold']:>10.2f} €  {status}")


def print_reimbursement_details(details: list[dict]) -> None:
    print("\nDETAILS OF THE REIMBURSEMENT" + "=" * 120)
    with_rate = any(row["min_rate"] is not None or row["max_rate"] is not None for row in details)
    print(header := f"{'Course':8} {'Fin':12} {'Start':12} {'Cost':12} {'Required':8} {'Served':8} {'Remaining':8} " \
                    f"{'Reimbursement':16} {'Status':16}" + (" Rate (this month)" if with_rate else ""))
    print("-" * len(header))
    for row in details:
        status = f"CAPPED (-{row['months_forgiven']}m)" if row["months_forgiven"] > 0 else \
                 ("CAPPED" if row["capped"] else "" if row["taken"] else "NOT YET TAKEN")
        print(f"{row['course']:8} {row['course_end'].strftime('%d/%m/%Y'):12} "
              f"{row['rendement_start'].strftime('%d/%m/%Y'):12} {row['cost']:>10.2f} € {row['required_months']:>8} "
              f"{row['months_served']:>7} "
              f"{row['months_remaining']:>7} {row['reimbursement']:>14.2f} € {status:16}"
              + (f" {row['monthly_rate']:>10.2f} €/month" if with_rate and row["monthly_rate"] is not None \
                 else ""))
    forgiven_rows = [row for row in details if row["months_forgiven"] > 0]
    if forgiven_rows:
        forgiven_amount = money(sum((row["amount_forgiven"] for row in forgiven_rows), Decimal("0.00")))
        print(f"\n{len(forgiven_rows)} capped period(s) (expired, as of Art. 179 §5) : "
              f"{forgiven_amount:.2f}€ off, not accounted in the total.")


def print_timeline(periods: list[Rendement], departure_date: date) -> None:
    print("\nTIMELINE OF RENDEMENT" + "=" * 120)
    with_rate = any(p.min_rate is not None or p.max_rate is not None for p in periods)
    # Local balances (see schedule_rendement), so as not to modify the actual results.
    for current, _available, active, amount in schedule_rendement(periods, departure_date):
        if active is not None:
            print(f"{current.strftime('%m/%Y')} : {active.course.code}"
                  + (f" ({fraction_to_money(amount):.2f}€)" if with_rate else ""))
        else:
            print(f"{current.strftime('%m/%Y')} : no active rendement")


def simulate(courses: list[Course], departure_date: date, verbose: bool = True, cap_months: int = CAP_MONTHS,
             min_rate: Decimal | None = MIN_RENDEMENT_RATE, max_rate: Decimal | None = MAX_RENDEMENT_RATE,
             postpone_remainder: Decimal | None = POSTPONE_REMAINDER) -> Decimal:
    triggering_courses, audit = determine_triggering_courses(courses)
    periods = build_rendement_periods(triggering_courses, cap_months=cap_months, min_rate=min_rate,
                                      max_rate=max_rate, postpone_remainder=postpone_remainder)
    total, details = calculate_reimbursement(periods, departure_date)
    if verbose:
        print("\n" + "=" * 120)
        print(f"SIMULATION - start at {departure_date.strftime('%d/%m/%Y')}")
        print("=" * 120)
        print(f"Indexed threshold at this date : {indexed_threshold(departure_date):.2f}€")
        if min_rate is not None:
            print(f"Indexed minimum rendement rate at this date : "
                  f"{indexed_min_rate(departure_date, min_rate):.2f}€/month")
        if max_rate is not None:
            print(f"Indexed maximum rendement rate at this date : "
                  f"{indexed_max_rate(departure_date, max_rate):.2f}€/month")
        if postpone_remainder is not None:
            print(f"Indexed remainder to postpone at this date : "
                  f"{indexed_postpone_remainder(departure_date, postpone_remainder):.2f}€")
        print_triggering_courses(audit)
        print_reimbursement_details(details)
        print("\n" + "=" * 120)
        print(f"TOTAL TO REIMBURSE : {total:.2f}€")
        print("=" * 120)
    return total


# ======================================================== MAIN ========================================================
def main() -> int:
    parser = ArgumentParser(description=("Trainings reimbursement simulator"))
    parser.add_argument("csv", type=Path, help="CSV with headers: Course, Price, End Date (and optionally Bundle, to "
                                               "group courses sharing a same value into a single rendement period)")
    parser.add_argument("--departure", type=parse_date, action="append", help="start date DD/MM/YY ; can be repeated")
    parser.add_argument("--timeline", action="store_true", help="include reimbursement timeline")
    parser.add_argument("--cap-years", type=int, default=CAP_YEARS, help="maximum validity of a reimbursement period ; "
                                                                         f"{CAP_YEARS} years as of art. 179, §5")
    parser.add_argument("--min-rate", type=parse_decimal, default=MIN_RENDEMENT_RATE,
                        help="minimum rendement rate in € per month, shortening the rendement period of cheaper "
                             "courses ; base amount, indexed like the threshold with the coefficient of each month "
                             f"served (not as of the law, which always spreads it over {REPAYMENT_MONTHS} months)")
    parser.add_argument("--max-rate", type=parse_decimal, default=MAX_RENDEMENT_RATE,
                        help="maximum rendement rate in € per month, lengthening the rendement period of more "
                             "expensive courses ; base amount, indexed like --min-rate, and strictly greater than it "
                             f"(not as of the law, which always spreads it over {REPAYMENT_MONTHS} months)")
    parser.add_argument("--postpone-remainder", type=parse_decimal, default=POSTPONE_REMAINDER,
                        help="amount in € below which the last month of a rendement period is merged into the previous "
                             "one, ending the period one month earlier ; base amount, indexed like --min-rate and "
                             "--max-rate (not as of the law)")
    args = parser.parse_args()
    cap_months = args.cap_years * 12
    if args.min_rate is not None and args.min_rate <= 0:
        parser.error("--min-rate must be strictly positive")
    if args.max_rate is not None and args.max_rate <= 0:
        parser.error("--max-rate must be strictly positive")
    if args.min_rate is not None and args.max_rate is not None and args.max_rate <= args.min_rate:
        parser.error("--max-rate must be strictly greater than --min-rate")
    if args.postpone_remainder is not None and args.postpone_remainder <= 0:
        parser.error("--postpone-remainder must be strictly positive")
    try:
        listed_courses = load_courses(args.csv)
        courses = bundle_courses(listed_courses)
    except Exception as exc:
        print(f"ERROR : {exc}", file=sys.stderr)
        return 1
    departure_dates = args.departure or [date(date.today().year + i, 1, 1) for i in range(1, 5)]
    print("\nSIMULATOR OF REIMBURSEMENT - ARTICLE 179")
    print("=" * 120)
    print(f"File: {args.csv}")
    print(f"Number of trainings: {len(listed_courses)}")
    for bundle in (c for c in courses if c.members):
        print(f"Bundle: {bundle.label} - {bundle.price:.2f}€, ending {bundle.end_date.strftime('%d/%m/%Y')}")
    if args.min_rate is not None:
        print(f"Minimum rendement rate: {args.min_rate:.2f}€/month base, indexed with the coefficient of each month "
              f"served (today: {indexed_min_rate(date.today(), args.min_rate):.2f}€/month) - not as of the law: "
              "shorter periods for cheaper courses")
    if args.max_rate is not None:
        print(f"Maximum rendement rate: {args.max_rate:.2f}€/month base, indexed with the coefficient of each month "
              f"served (today: {indexed_max_rate(date.today(), args.max_rate):.2f}€/month) - not as of the law: "
              "longer periods for more expensive courses")
    if args.postpone_remainder is not None:
        print(f"Remainder to postpone: {args.postpone_remainder:.2f}€ base, indexed with the coefficient of each month "
              f"served (today: {indexed_postpone_remainder(date.today(), args.postpone_remainder):.2f}€) - not as of "
              "the law: a smaller last month is merged into the previous one")
    for departure_date in departure_dates:
        simulate(courses, departure_date, cap_months=cap_months, min_rate=args.min_rate, max_rate=args.max_rate,
                 postpone_remainder=args.postpone_remainder)
    if args.timeline:  # optional timeline
        triggering_courses, _ = determine_triggering_courses(courses)
        periods = build_rendement_periods(triggering_courses, cap_months=cap_months, min_rate=args.min_rate,
                                          max_rate=args.max_rate, postpone_remainder=args.postpone_remainder)
        if periods:
            print(f"\nTIMELINE UNTIL {max(departure_dates).strftime('%d/%m/%Y')}")
            print_timeline(periods, max(departure_dates))
    return 0


if __name__ == "__main__":
    sys.exit(main())

