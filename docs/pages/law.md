# The law of 31/07/2013, Art. 179

This page describes how the simulator models the training-reimbursement clause as it currently stands. This is the
default behavior of both [`simulator.py`](command-line.md) and [`dash_app.py`](dashboard.md): as long as none of the
options described in [Beyond the law](beyond-the-law.md) is set, the results follow the rules below.

## Rules

### Threshold

A training triggers the obligation only if the **cumulative cost of the trainings completed within the trailing 24
months** (the training itself included) exceeds an **indexed threshold**: a base amount of **€5,000**, multiplied by the
indexation coefficient applicable at the end date of the training (see [Indexation table](input-files.md#indexation-table)).
For instance, with the coefficient 2.2080 applicable since 01/09/2026, the threshold is €11,040.00.

### Rendement period

Once triggered, the employee owes **24 months of service** ("rendement") after that training. The period starts on the
first day of the month following the end date of the training.

Leaving before the period is complete means reimbursing a **degressive amount**:

```
reimbursement = price × months still owed / 24
```

A course is only owed once it has been completed, i.e. for departure dates after its end date.

### Priority and suspension

When several rendement periods overlap, **only the most recently triggered one accrues service each month**. Older
ones are suspended until it is fully served, then resume where they stopped.

### Validity cap (§5)

A rendement period's clause **stops producing any effect 15 years after it started**, regardless of how much of it was
actually served. The remaining balance is forgiven, not carried forward.

### Bundles

Several courses can be declared as a single training, e.g. the courses of a same certification track, by giving them
the same `Bundle` value in the [course list](input-files.md#course-list). The bundle is then treated as one course,
named after the bundle: its price is the sum of theirs and its end date the latest of theirs. It goes through the
threshold test as one course and, if it triggers, gets a single rendement period starting after its last course.

## Worked example

With [`src/example.csv`](https://github.com/dhondta/trainings-reimbursement-simulator/blob/main/src/example.csv):

```csv
Course,Price,End Date
SEC401,1725.00,25/04/24
SEC504,8856.88,07/11/24
FOR508,9379.60,07/02/25
SEC599,9140.12,19/09/26
```

and a departure on 01/06/2026:

```bash
python3 src/simulator.py src/example.csv --departure 01/06/2026
```

```
TRAININGS & THRESHOLD TEST
SEC401   25/04/2024  cumul =    1725.00 €  threshold =   10199.50 €  DOES NOT TRIGGER
SEC504   07/11/2024  cumul =   10581.88 €  threshold =   10403.50 €  TRIGGERS
FOR508   07/02/2025  cumul =   19961.48 €  threshold =   10403.50 €  TRIGGERS
SEC599   19/09/2026  cumul =   27376.60 €  threshold =   11040.00 €  TRIGGERS

DETAILS OF THE REIMBURSEMENT
Course   Fin          Start        Cost         Required Served   Remaining Reimbursement    Status
-------------------------------------------------------------------------------------------------------------
SEC504   07/11/2024   01/12/2024      8856.88 €       24       3      21        7749.77 €
FOR508   07/02/2025   01/03/2025      9379.60 €       24      15       9        3517.35 €
SEC599   19/09/2026   01/10/2026      9140.12 €        0       0       0           0.00 € NOT YET TAKEN

TOTAL TO REIMBURSE : 11267.12€
```

- **SEC401** alone stays below the threshold, so it never triggers.
- **SEC504** brings the 24-month cumulative cost above the threshold: its period starts on 01/12/2024.
- **FOR508** triggers too: its period starts on 01/03/2025 and takes priority, so SEC504 is suspended after only 3
  months served. By 01/06/2026, FOR508 has been served for 15 months: 9 are still owed (9379.60 × 9 / 24 = 3517.35 €)
  and SEC504 still owes 21 (8856.88 × 21 / 24 = 7749.77 €).
- **SEC599** ends after the departure date, so it is not owed yet.

## Simulating a situation as of the law

Command line - one or more departure dates, and optionally the month-by-month timeline of active and suspended periods:

```bash
python3 src/simulator.py my-courses.csv --departure 01/06/2027 --departure 01/01/2030 --timeline
```

Without `--departure`, the situation is reported on January 1st of each of the next four years.

Web dashboard - start it without any of the options of [Beyond the law](beyond-the-law.md):

```bash
python3 src/dash_app.py --local
```

The explanation panel then restates the four criteria above with the actual numbers of the simulation, and the PDF
report lists them as the rules applied. Whenever an option departing from the law is set, the panel calls it out with a
"Beyond the law" notice.
