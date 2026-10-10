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

| Column | Format |
|---|---|
| `Course` | Any identifier (course code, name, …). |
| `Price` | `.` or `,` as decimal separator, thousand separators and an optional `€` sign are accepted. |
| `End Date` | `DD/MM/YYYY`, `DD/MM/YY`, `DD-MM-YYYY` or `YYYY-MM-DD`. |
| `Bundle` *(optional)* | Any name, shared by the courses to group, and left empty for the others. It may not be named like a course outside of it. |

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
[BOSA - indexation](https://bosa.belgium.be/fr/themes/travailler-dans-la-fonction-publique/remuneration-et-avantages/traitement/indexation-0).

The web dashboard reads the file once at startup: restart it after editing the file.
