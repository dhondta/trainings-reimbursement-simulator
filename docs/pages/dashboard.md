# Web dashboard

`src/dash_app.py` serves an interactive dashboard on <http://127.0.0.1:8050>:

```bash
python3 src/dash_app.py --local    # single user, no sign-in
python3 src/dash_app.py            # multi-user, with sign-in (see Deployment)
```

`--local` skips sign-in entirely, for running the app on your own machine. Without it, users sign in so that their
course lists stay private - see [Deployment](deployment.md) for the sign-in methods and their configuration.

The `--cap-years`, `--min-rate`, `--max-rate` and `--postpone-remainder` options of the
[command-line tool](command-line.md) are available too, to visualize the mechanisms described in
[Beyond the law](beyond-the-law.md):

```bash
python3 src/dash_app.py --local --cap-years 10 --min-rate 250
```

`--debug` enables Flask's debug mode (hot reload and server-side tracebacks).

## Features

- **Course table** - editable and kept sorted by end date: add or delete rows, import a CSV in the
  [course list format](input-files.md#course-list), or export the current table to a CSV in the same format. Prices
  and dates are reformatted as they are entered (e.g. `4.174,85 €` → `4174.85`, `2024-11-07` → `07/11/24`).
- **Presets** - every CSV of `src/` that complies with the course list format (such as `example.csv`), plus the user's
  own uploads, is offered in the preset dropdown. Any other CSV, such as `index_values.csv`, is ignored.
- **Departure date slider** - over every month from the start of the first rendement period (to look back at past
  departure dates) up to the date the whole course list is fully resolved; it starts on next month.
- **Charts** - a bar chart of the degressive amount owed per course (with a fixed y-axis, so bars visibly shrink as the
  slider moves forward) and a Gantt-style chart of each rendement period's served, suspended and remaining months.
- **Key figures** - cards for the total owed, the rendement period (start and end dates) and the current month's
  rendement rate.
- **Explanation panel** - restates the [criteria of the law](law.md#rules) with the actual numbers of the simulation,
  and calls out any option [beyond the law](beyond-the-law.md) in use.
- **PDF report** - the reimbursement plan for the selected departure date (key figures, threshold test, amount owed per
  course, both charts and the explanation panel), in the current language.
- **Languages** - English, French and Dutch (selector in the top-right corner).

## Limits

| Limit | Value |
|---|---|
| Courses per table | 50 |
| Size of an imported CSV | 2 KB |
| Uploaded CSVs kept per user | 10 (presets of `src/` excluded) |
| Delay between two PDF exports by a same user | 1 minute |

These are set in `src/webapp/config.py`.
