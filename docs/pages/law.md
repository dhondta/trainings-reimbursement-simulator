# The law: Art. 179

This page describes how the simulator models Art. 179 of the [law of 28/02/2007](https://www.ejustice.just.fgov.be/cgi_loi/change_lg.pl?language=fr&la=F&table_name=loi&cn=2007022835) on the status of military personnel,
as replaced by the [law of 31/07/2013](https://www.ejustice.just.fgov.be/cgi_loi/change_lg.pl?language=fr&la=F&table_name=loi&cn=2013073104), for the trainings of its §1, 5°: any training followed at the expense of Defence
by a career military member or an auxiliary officer. The texts, their history and the open questions are detailed in
[Legal basis](legal-basis.md).

This is the default behavior of both [`simulator.py`](command-line.md) and [`dash_app.py`](dashboard.md): as long as
none of the options described in [Beyond the law](beyond-the-law.md) is set, the results follow the rules below.

## Rules

### Threshold

A training triggers the obligation only if the **cumulative cost of the trainings completed within the trailing 24
months** (the training itself included) exceeds an **indexed threshold**: a base amount of **€5,000**, multiplied by the
indexation coefficient applicable at the end date of the training (see [Indexation table](input-files.md#indexation-table)).
For instance, with the coefficient 2.2080 applicable since 01/09/2026, the threshold is €11,040.00.

The rule applies to the trainings ending **from 04/06/2009 on**, when it was introduced in the [law of 16/03/2000](https://www.ejustice.just.fgov.be/cgi_loi/change_lg.pl?language=fr&la=F&table_name=loi&cn=2000031635) (it was
taken over unchanged in the [law of 28/02/2007](https://www.ejustice.just.fgov.be/cgi_loi/change_lg.pl?language=fr&la=F&table_name=loi&cn=2007022835) on 31/12/2013). Earlier trainings never trigger the obligation, but
still count in the cumulative cost of the next ones.

The minimum is to be fixed by the King, without being lower than €5,000: as no royal decree fixing it was found, the
simulator uses €5,000.

### Rendement period

Once triggered, the military member owes **24 months of service** ("rendement") after that training. The period starts on the
first day of the month following the end date of the training.

Leaving before the period is complete, by resignation or dismissal ex officio for a career military member
(Art. 180, al. 3), or by termination of the engagement at their request or for disciplinary reasons, moral or
professional unfitness for an auxiliary officer (Art. 181, al. 4 - see
[Who is concerned](legal-basis.md#who-is-concerned)), means reimbursing a **degressive amount**:

```
reimbursement = price × months still owed / 24
```

A course is only owed once it has been completed, i.e. for departure dates after its end date.

### Priority and suspension

When several rendement periods overlap, **only the most recently triggered one accrues service each month**. Older
ones are suspended until it is fully served, then resume where they stopped.

### Maximum total rendement period (§5)

> The rendement periods corresponding to various trainings are cumulated. The total rendement period may not exceed
> fifteen years.

(Unofficial translation - see [Legal basis](legal-basis.md) for the texts.)

The rendement periods of the various trainings are **cumulated**, and the total cannot exceed **15 years**. The
explanatory memorandum of the [law of 31/07/2013](https://www.ejustice.just.fgov.be/cgi_loi/change_lg.pl?language=fr&la=F&table_name=loi&cn=2013073104) confirms that this limit applies to the cumulation of several trainings
(a single training being limited by §2), so that trainings do not lead to "the obligation to perform more than
fifteen years of active service" (see [Legal basis](legal-basis.md#maximum-total-rendement-period)). As months of
[non-activity](#non-activity-6) are not rendement, they do not count towards the 15 years.

The text does not say how the 15 years are measured. The simulator offers two readings, with the `--cap-mode` option,
or with the cap mode selector of the [web dashboard](dashboard.md) (whose initial value is set by `--cap-mode` or the
`CAP_MODE` environment variable):

- **`bunch`** (default) - per **bunch of cumulated periods**: the rendement periods served one after the other,
  without interruption, form a bunch, whose months of rendement served are counted. Once they reach 15 years, the
  remaining balance of every period of the bunch is forgiven. A training followed afterwards starts a new bunch.
- **`period`** - per **rendement period**: each period is limited on its own, its remaining balance being forgiven 15
  years after it started, counting the months it was suspended behind more recent periods.

A bunch reaches 15 years no later than its oldest period, so `bunch` never gives a higher amount than `period`.

For instance, 10 trainings of €12,000 ending every 6 months from 15/01/2014 on, each starting a 24-month period, add
up to 240 months of rendement, served one after the other without interruption from 01/02/2014 on:

| Departure | `bunch` | `period` |
|---|---|---|
| 01/12/2020 | 79,000 € | 79,000 € |
| 01/03/2029 | 0 € - the bunch reached 15 years on 01/02/2029, so the remaining balance of its 4 oldest periods is forgiven | 20,500 € - only the oldest period, started on 01/02/2014, is forgiven |
| 01/01/2030 | 0 € | 6,500 € - the second period was forgiven on 01/08/2029, the third one will be on 01/02/2030 |

### Non-activity (§6)

The rendement period in progress is **suspended while the military member is in non-activity**, a position defined by
Art. 189 of the [law of 28/02/2007](https://www.ejustice.just.fgov.be/cgi_loi/change_lg.pl?language=fr&la=F&table_name=loi&cn=2007022835): temporary withdrawal of employment (e.g. by career
interruption, for family reasons, for health reasons, for personal convenience or as a disciplinary measure), illegal
absence, serving a custodial sentence, ex officio political leave, or some criminal convictions. Other absences, such as
annual leave, are not non-activity. Periods of non-activity are added to the [course list](input-files.md#course-list)
as rows with a start date, an end date and no price. As rendement is counted in whole months (§4), **every month a period of non-activity touches, even partly, is not
served**: for instance, a non-activity from 15/03/2025 to 10/05/2025 suspends March, April and May 2025. The rendement
periods then end as many months later.

With the [worked example](#worked-example) and this non-activity, FOR508 has only served 12 months by 01/06/2026
instead of 15, which raises the total to reimburse from 11,267.12 € to 12,439.57 €.

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
