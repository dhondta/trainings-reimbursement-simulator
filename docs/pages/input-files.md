# Input files

## Course list

Both the command-line tool and the web dashboard take the list of courses as a CSV with these headers:

```csv
Course,Price,End Date
A,4321.85,10/08/2013
B,5123.40,26/11/2014
```

An optional `Bundle` column groups courses into a single training (see [Bundles](law.md#bundles)):

```csv
Course,Price,End Date,Bundle
A,4321.85,10/08/2013,
B,5123.40,26/11/2014,GIAC
C,4980.00,15/02/2015,GIAC
```

An optional `Start Date` column adds periods of non-activity (see [Non-activity](law.md#non-activity-6) for what counts
as such): a row with
a start date, an end date and no price is such a period, the `Course` column giving it an optional label:

```csv
Course,Price,End Date,Start Date
SEC504,8856.88,07/11/2024,
FOR508,9379.60,07/02/2025,
Career interruption,,10/05/2025,15/03/2025
```

| Column | Format |
|---|---|
| `Course` | Any identifier (course code, name, …). |
| `Price` | `.` or `,` as decimal separator, thousand separators and an optional `€` sign are accepted. |
| `End Date` | `DD/MM/YYYY`, `DD/MM/YY`, `DD-MM-YYYY` or `YYYY-MM-DD`. |
| `Bundle` *(optional)* | Any name, shared by the courses to group, and left empty for the others. It may not be named like a course outside of it. |
| `Start Date` *(optional)* | For a period of non-activity only (same formats as `End Date`): its first day, its last day being in `End Date`. Such a row has no `Price` nor `Bundle`. |

`src/example.csv` is a ready-to-use example.

## Indexation table

The indexation coefficients applied to the €5,000 threshold (and to the base amounts of
[Beyond the law](beyond-the-law.md)) live in `src/index_values.csv`, read by both the command-line tool and the web
dashboard:

```csv
Start Date,Index Value
01/03/2026,2.1647
01/09/2026,2.2080
```

| Column | Format |
|---|---|
| `Start Date` | First day a coefficient applies (same date formats as above). Each period ends the day before the next one starts, and the last one stays in effect until a newer row is added - so a new index is a one-line append. Rows may be in any order; a duplicate start date is rejected. |
| `Index Value` | The coefficient applied to the €5,000 base (same number formats as `Price`). |

Source for the coefficients:
[BOSA - indexation](https://bosa.belgium.be/fr/themes/travailler-dans-la-fonction-publique/remuneration-et-avantages/traitement/indexation-0)
(the table starts with the coefficient 1.4859 applicable since 01/10/2008, so as to cover the trainings ending from
04/06/2009 on - see [Threshold](law.md#threshold)).

**Legal basis** - Art. 184/1 of the [law of 28/02/2007](https://www.ejustice.just.fgov.be/cgi_loi/change_lg.pl?language=fr&la=F&table_name=loi&cn=2007022835) (inserted by the [law of 31/07/2013](https://www.ejustice.just.fgov.be/cgi_loi/change_lg.pl?language=fr&la=F&table_name=loi&cn=2013073104)) links the amounts of the law,
such as the €5,000 of Art. 179, §1, 5°, to the pivot index 138.01 and adapts them as of the
[law of 01/03/1977](https://www.ejustice.just.fgov.be/cgi_loi/change_lg.pl?language=fr&la=F&table_name=loi&cn=1977030102):
each time the smoothed health index reaches the pivot index of rank `n` (each pivot index being the previous one × 1.02,
rounded to 2 decimals - Art. 2), the amounts are multiplied by the coefficient `1.02ⁿ`, rounded to 4 decimals (Art. 4),
from the third month after (Art. 6, 3°, since 01/07/2025 - the delay was shorter before). These are the coefficients of the
public sector published by BOSA, e.g. `1.02⁴⁰` = 2.2080.

### Updating the table

As the BOSA page cannot be downloaded by scripts, the new rows are derived from [Statbel's be.STAT data](https://bestat.statbel.fgov.be/bestat/)
instead, validated, then appended to `src/index_values.csv` by the `--update-index-values` option of both tools:

```bash
python3 src/simulator.py --update-index-values                    # update only
python3 src/simulator.py --update-index-values my-courses.csv     # update, then simulate
python3 src/dash_app.py --local --update-index-values             # start the dashboard, updating now and monthly
```

The delay between the pivot index being reached and the adaptation is `INDEXATION_DELAY_MONTHS` in
`src/simulator.py` (3 months, as of the [law of 01/03/1977](https://www.ejustice.just.fgov.be/cgi_loi/change_lg.pl?language=fr&la=F&table_name=loi&cn=1977030102), Art. 6, 3°).

Statbel's data only covers the last 13 months, so update the table at least once a year. The update stops with an
error, leaving the file unchanged, when the data does not cover every month since the last row, or when Statbel switches
to a new base year (`INDEX_REFERENCE` in `src/simulator.py` must then be updated). Check the new rows against the BOSA
page.

With `--update-index-values` (or the `UPDATE_INDEX_VALUES` environment variable set to `1`, `true` or `yes`, e.g.
under `wsgi.py`), the web dashboard updates the table in the background when it starts, then **on the first day of
every month at midnight** (server local time) while it runs, and applies the new rows at once, without a restart. When
an update fails (e.g. Statbel is unreachable), it is retried every hour, up to 23 times, then at the next monthly
update; each attempt is logged on the server console, and the dashboard keeps running with the table as it was.

Otherwise, the web dashboard reads the file once at startup: restart it after editing the file by hand.
