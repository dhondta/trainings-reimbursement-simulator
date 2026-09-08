from __future__ import annotations

import csv
import sys
from argparse import ArgumentParser
from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path


# =================================================== CONFIGURATION ====================================================
BASE_THRESHOLD = Decimal("5000.00")
REPAYMENT_MONTHS = 24
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


# ==================================================== DATA MODELS =====================================================
@dataclass(frozen=True)
class Course:
    code: str
    price: Decimal
    end_date: date


@dataclass
class Rendement:
    course: Course
    start_date: date                         # First day of the full month following the course.
    months_served: int = 0                   # Number of rendement months actually completed.
    required_months: int = REPAYMENT_MONTHS  # Always 24 months in total.
    cap_months: int = CAP_MONTHS             # Validity period of the clause for this period (art. 179, §5).
    
    @property
    def months_remaining(self) -> int:
        return max(0, self.required_months - self.months_served)
    
    @property
    def completed(self) -> bool:
        return self.months_remaining == 0
    
    @property
    def cap_date(self) -> date:
        """Date from which the clause no longer produces any effect for
        this period, regardless of how many months have been served."""
        return add_months(self.start_date, self.cap_months)
    
    def capped_at(self, at_date: date) -> bool:
        return at_date >= self.cap_date


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
    for start, end, coefficient in INDEX_VALUES:
        if at_date >= start and (end is None or at_date <= end):
            return coefficient
    raise ValueError(f"No indexation coefficient defined for {at_date.strftime('%d/%m/%Y')}")


def indexed_threshold(at_date: date) -> Decimal:
    coefficient = index_coefficient(at_date)
    return money(BASE_THRESHOLD * coefficient)


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
def build_period_status_timeline(periods: list[Rendement], as_of_date: date) -> dict[str, list[dict]]:
    """ For each period, returns the chronological list of monthly segments grouped by status: 'served' (rendement
     active that month), 'suspended' (a more recent course takes priority), or 'remaining' (months still owed, projected
     past as_of_date for lack of a longer simulation).

    A period stays 'suspended' until ALL periods more recent than it have themselves finished their 24 months of
     rendement (or until as_of_date, if that comes first, or until its own clause expires — art. 179, §5). To obtain the
     real end date of each period (and thus an untruncated, pyramid-shaped timeline), the caller must supply an
     as_of_date far enough ahead to cover the full chain of suspensions.

    Past its own cap_date, a period no longer appears among the available ones (the clause has expired) and no
     'remaining' segment is added for it: the outstanding balance is wiped out, not carried forward.

    Does not modify periods[i].months_served (local counters, as in print_timeline).
    """
    if not periods:
        return {}
    current, served = min(p.start_date for p in periods), {id(p): 0 for p in periods}
    runs: dict[int, list[dict]] = {id(p): [] for p in periods}
    def add_month(period, month_start, status):
        month_end = next_month(month_start)
        period_runs = runs[id(period)]
        if period_runs and period_runs[-1]["status"] == status and period_runs[-1]["end"] == month_start:
            period_runs[-1]["end"] = month_end
        else:
            period_runs.append({'start': month_start, 'end': month_end, 'status': status})
    while current < as_of_date:
        if available := [p for p in periods if p.start_date <= current and served[id(p)] < REPAYMENT_MONTHS \
                                               and not p.capped_at(current)]:
            available.sort(key=lambda p: p.start_date, reverse=True)
            active = available[0]
            served[id(active)] += 1
            for p in available:
                add_month(p, current, "served" if p is active else "suspended")
        current = next_month(current)
    result = {}
    for p in periods:
        period_runs = list(runs[id(p)])
        months_remaining = (0 if p.capped_at(as_of_date) else max(0, REPAYMENT_MONTHS - served[id(p)]))
        if months_remaining > 0:
            start = (period_runs[-1]["end"] if period_runs else p.start_date)
            period_runs.append({'start': start, 'end': add_months(start, months_remaining), 'status': "remaining"})
        result[p.course.code] = period_runs
    return result


def build_rendement_periods(triggering_courses: list[Course], cap_months: int = CAP_MONTHS) -> list[Rendement]:
    periods = []
    for c in triggering_courses:
        periods.append(Rendement(course=c, start_date=first_day_next_month(c.end_date), cap_months=cap_months))
    return sorted(periods, key=lambda p: p.start_date)


def calculate_reimbursement(periods: list[Rendement], departure_date: date) -> tuple[Decimal, list[dict]]:
    if not periods:
        return Decimal("0.00"), []
    # Each rendement period has 24 months of rendement STILL TO BE SERVED.
    # When a new period starts:
    #     new period = active
    #     old period = suspended
    # When the new period ends, the old one resumes with its previous counter.
    current = min(p.start_date for p in periods)
    while current < departure_date:
        # Courses whose rendement has started, are still owed, and whose clause has not expired (art. 179, §5).
        available = [p for p in periods if p.start_date <= current and not p.completed and not p.capped_at(current)]
        if available:  # The most recent course takes priority. It suspends the older periods.
            available.sort(key=lambda p: p.start_date, reverse=True)
            active = available[0]
            active.months_served += 1
        current = next_month(current)
    # Financial calculation
    details, total = [], Decimal("0.00")
    for period in periods:
        # Once the clause's validity period has elapsed, the obligation lapses: nothing more is owed for this course,
        #  even if the 24 months have not been served. The number of months thus forgiven is exposed explicitly
        #  (months_forgiven) so the total stays auditable: a zero balance because the service is complete can be
        #  distinguished from a zero balance because it was forgiven under art. 179, §5.
        capped = period.capped_at(departure_date)
        uncapped_remaining = period.months_remaining
        remaining = 0 if capped else uncapped_remaining
        months_forgiven = uncapped_remaining if capped else 0
        reimbursement = money(period.course.price * Decimal(remaining) / Decimal(REPAYMENT_MONTHS))
        total += reimbursement
        details.append({
            "course":           period.course.code,
            "course_end":       period.course.end_date,
            "rendement_start":  period.start_date,
            "cost":             period.course.price,
            "months_served":    period.months_served,
            "months_remaining": remaining,
            "reimbursement":    reimbursement,
            "capped":           capped,
            "months_forgiven":  months_forgiven,
        })
    return money(total), details


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
                courses.append(Course(code=code, price=price, end_date=parse_date(row["End Date"])))
            except Exception as exc:
                raise ValueError(f"error at line {line_number}: {exc}") from exc
    if not courses:
        raise ValueError("input CSV file has no data")
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
        print(f"{course.code:8} {course.end_date.strftime('%d/%m/%Y')}  cumul = {row['cumulative_cost']:>10.2f} €  "
            f"threshold = {row['threshold']:>10.2f} €  {status}")


def print_reimbursement_details(details: list[dict]) -> None:
    print("\nDETAILS OF THE REIMBURSEMENT" + "=" * 120)
    print(header := f"{'Course':8} {'Fin':12} {'Start':12} {'Cost':12} {'Served':8} {'Remaining':8} " \
                    f"{'Reimbursement':16} {'Status':16}")
    print("-" * len(header))
    for row in details:
        status = f"CAPPED (-{row['months_forgiven']}m)" if row["months_forgiven"] > 0 else ("CAPPED" if row["capped"] else "")
        print(f"{row['course']:8} {row['course_end'].strftime('%d/%m/%Y'):12} "
              f"{row['rendement_start'].strftime('%d/%m/%Y'):12} {row['cost']:>10.2f} € {row['months_served']:>7} "
              f"{row['months_remaining']:>7} {row['reimbursement']:>14.2f} € {status:16}")
    forgiven_rows = [row for row in details if row["months_forgiven"] > 0]
    if forgiven_rows:
        forgiven_amount = money(sum((row["cost"] * Decimal(row["months_forgiven"]) / Decimal(REPAYMENT_MONTHS) \
                                     for row in forgiven_rows), Decimal("0.00")))
        print(f"\n{len(forgiven_rows)} capped period(s) (expired, as of Art. 179 §5) : "
              f"{forgiven_amount:.2f}€ off, not accounted in the total.")


def print_timeline(periods: list[Rendement], departure_date: date) -> None:
    print("\nTIMELINE OF RENDEMENT" + "=" * 120)
    current = min(p.start_date for p in periods)
    # Local copy of the counters, so as not to modify the actual results.
    served = {id(p): 0 for p in periods}
    while current < departure_date:
        if available := [p for p in periods if p.start_date <= current and served[id(p)] < REPAYMENT_MONTHS \
                                               and not p.capped_at(current)]:
            available.sort(key=lambda p: p.start_date, reverse=True)
            active = available[0]
            served[id(active)] += 1
            print(f"{current.strftime('%m/%Y')} : {active.course.code}")
        else:
            print(f"{current.strftime('%m/%Y')} : no active rendement")
        current = next_month(current)


def simulate(courses: list[Course], departure_date: date, verbose: bool = True, cap_months: int = CAP_MONTHS) -> Decimal:
    triggering_courses, audit = determine_triggering_courses(courses)
    periods = build_rendement_periods(triggering_courses, cap_months=cap_months)
    total, details = calculate_reimbursement(periods, departure_date)
    if verbose:
        print("\n" + "=" * 120)
        print(f"SIMULATION - start at {departure_date.strftime('%d/%m/%Y')}")
        print("=" * 120)
        print(f"Indexed threshold at this date : {indexed_threshold(departure_date):.2f}€")
        print_triggering_courses(audit)
        print_reimbursement_details(details)
        print("\n" + "=" * 120)
        print(f"TOTAL TO REIMBURSE : {total:.2f}€")
        print("=" * 120)
    return total


# ======================================================== MAIN ========================================================
def main() -> int:
    parser = ArgumentParser(description=("Trainings reimbursement simulator"))
    parser.add_argument("csv", type=Path, help="CSV with headers: Course, Price, End Date")
    parser.add_argument("--departure", type=parse_date, action="append", help="start date DD/MM/YY ; can be repeated")
    parser.add_argument("--timeline", action="store_true", help="include reimbursement timeline")
    parser.add_argument("--cap-years", type=int, default=CAP_YEARS, help="maximum validity of a reimbursement period ; "
                                                                         f"{CAP_YEARS} years as of art. 179, §5")
    args = parser.parse_args()
    cap_months = args.cap_years * 12
    try:
        courses = load_courses(args.csv)
    except Exception as exc:
        print(f"ERROR : {exc}", file=sys.stderr)
        return 1
    departure_dates = args.departure or [date(date.today().year + i, 1, 1) for i in range(1, 5)]
    print("\nSIMULATOR OF REIMBURSEMENT - ARTICLE 179")
    print("=" * 120)
    print(f"File: {args.csv}")
    print(f"Number of trainings: {len(courses)}")
    for departure_date in departure_dates:
        simulate(courses, departure_date, cap_months=cap_months)
    if args.timeline:  # optional timeline
        triggering_courses, _ = determine_triggering_courses(courses)
        periods = build_rendement_periods(triggering_courses, cap_months=cap_months)
        if periods:
            print(f"\nTIMELINE UNTIL {max(departure_dates).strftime('%d/%m/%Y')}")
            print_timeline(periods, max(departure_dates))
    return 0


if __name__ == "__main__":
    sys.exit(main())

