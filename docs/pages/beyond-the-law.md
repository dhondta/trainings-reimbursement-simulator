# Beyond the law

The simulator offers mechanisms that **Art. 179 of the law of 31/07/2013 does not provide**. They are all **off by
default**, and serve to assess the effect of possible amendments of the law on concrete course lists before proposing
them.

| Mechanism | Command-line option | Environment variable | As of the law |
|---|---|---|---|
| [Minimum rendement rate](#minimum-rendement-rate) | `--min-rate R` | `MIN_RENDEMENT_RATE` | none: `price / 24` per month |
| [Maximum rendement rate](#maximum-rendement-rate) | `--max-rate M` | `MAX_RENDEMENT_RATE` | none: `price / 24` per month |
| [Postponed remainder](#postponed-remainder) | `--postpone-remainder P` | `POSTPONE_REMAINDER` | none |
| [Other validity cap](#other-validity-cap) | `--cap-years N` | `CAP_YEARS` | 15 years (§5) |

The options are the same for [`simulator.py`](command-line.md) and [`dash_app.py`](dashboard.md); the environment
variables apply to the web dashboard only (e.g. when served through `wsgi.py`), the command-line options taking
precedence. In the dashboard, every mechanism in use is called out with a "Beyond the law" notice in the explanation
panel.

All amounts (`R`, `M` and `P`) are **base amounts, indexed like the €5,000 threshold** with the coefficient applicable
in the month being served (see [Indexation table](input-files.md#indexation-table)). For instance, `R` = 250 € gives
552 €/month with the 2.2080 coefficient. The amounts thus rise with the index, even during a rendement period.

## Minimum rendement rate

**Issue addressed** - As of the law, every triggering course is paid off over 24 months, whatever its price. A cheap
triggering course thus ties the employee down for two full years at a low monthly rate.

**Mechanism** - Each month served pays off at least `R × index`:

```
paid off per month = max(price / 24, R × index)
```

The reimbursement is the part of the price not yet paid off, and the period ends when the price is fully paid off, its
last month settling the remainder. The rendement period of cheaper courses is thus shortened, and their degression sped
up; courses with `price / 24 ≥ R × index` are unaffected.

```bash
python3 src/simulator.py my-courses.csv --min-rate 250
```

## Maximum rendement rate

**Issue addressed** - The counterpart of the minimum rate: as of the law, an expensive course is paid off at a high
monthly rate, over 24 months as well.

**Mechanism** - Each month served pays off at most `M × index`:

```
paid off per month = min(max(price / 24, R × index), M × index)
```

The rendement period of more expensive courses is thus lengthened beyond 24 months, and their degression slowed down.
When both are set, `M` must be strictly greater than `R`.

```bash
python3 src/simulator.py my-courses.csv --min-rate 250 --max-rate 500
```

## Postponed remainder

**Issue addressed** - With a minimum or maximum rate, the last month of a rendement period only settles what remains of
the price, which may be a small amount keeping the employee bound for a whole extra month.

**Mechanism** - When the last month of a period would pay off less than `P × index`, that remainder is merged into the
previous month served, which then pays off its rate plus the remainder (possibly above `M × index`). The period thus
ends one month earlier, even when a more recent period was served in between.

```bash
python3 src/simulator.py my-courses.csv --min-rate 250 --postpone-remainder 100
```

## Other validity cap

**Issue addressed** - §5 sets the validity of a rendement period's clause to 15 years from its start; another duration
can be simulated, e.g. to assess a shorter one.

**Mechanism** - The clause of a rendement period stops producing any effect after `N` years instead of 15, the
remaining balance being forgiven.

```bash
python3 src/simulator.py my-courses.csv --cap-years 10
```

## Comparing with the law

Running the same course list with and without an option shows its effect. For instance, with
[the worked example](law.md#worked-example) of `src/example.csv` and a departure on 01/06/2026:

| Simulation | Command-line options | Total to reimburse |
|---|---|---|
| As of the law | *(none)* | 11,267.12 € |
| Minimum rate of 250 €/month | `--min-rate 250` | 8,685.44 € |
| Maximum rate of 150 €/month | `--max-rate 150` | 12,505.82 € |
| Validity cap of 1 year | `--cap-years 1` | 0.00 € |

Whatever the departure date, a minimum rate, a postponed remainder or a shorter validity cap never increase the amount
owed, while a maximum rate never decreases it. The [continuous integration](development.md#continuous-integration)
checks these properties on every change.

In the web dashboard, start the app with the options to compare, and move the departure date slider to see how the
rendement periods and the amounts owed evolve over time:

```bash
python3 src/dash_app.py --local --min-rate 250 --max-rate 500 --postpone-remainder 100
```
