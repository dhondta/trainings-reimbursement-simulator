# Web dashboard

`src/dash_app.py` serves an interactive dashboard on <http://127.0.0.1:8050>:

```bash
python3 src/dash_app.py --local    # single user, no sign-in
python3 src/dash_app.py            # multi-user, with sign-in (see Deployment)
```

`--local` skips sign-in entirely, for running the app on your own machine. Without it, users sign in so that their
course lists stay private - see [Deployment](deployment.md) for the sign-in methods and their configuration.

The `--cap-mode` option of the [command-line tool](command-line.md) is available too (as the initial value of the
cap mode selector, see below), as well as its `--cap-years`, `--min-rate`, `--max-rate` and `--postpone-remainder`
options, to visualize the mechanisms described in [Beyond the law](beyond-the-law.md):

```bash
python3 src/dash_app.py --local --cap-years 10 --min-rate 250
```

`--debug` enables Flask's debug mode (hot reload and server-side tracebacks). `--update-index-values`
[updates the indexation table](input-files.md#updating-the-table) from Statbel's data when the app starts, then on the
first day of every month at midnight while it runs.

## Features

- **Course table** - editable and kept sorted by end date: add or delete rows, import a CSV in the
  [course list format](input-files.md#course-list), or export the current table to a CSV in the same format. A row
  with a non-activity start date is a [period of non-activity](law.md#non-activity-6). Prices and dates are reformatted as they are entered (e.g. `4.174,85 €` → `4174.85`, `2024-11-07` → `07/11/24`).
- **Presets** - every CSV of `src/` that complies with the course list format (such as `example.csv`), plus the user's
  own uploads, is offered in the preset dropdown. Any other CSV, such as `index_values.csv`, is ignored.
- **Cap mode selector** - next to the departure date, how the
  [maximum total rendement period](law.md#maximum-total-rendement-period-5) applies: per bunch of cumulated periods
  (the default) or per rendement period.
  Changing it updates the charts, the explanation, the slider range and the PDF report at once, for this visitor only.
- **Departure date slider** - over every month from the start of the first rendement period (to look back at past
  departure dates) up to the date the whole course list is fully resolved; it starts on next month.
- **Charts** - a bar chart of the degressive amount owed per course (with a fixed y-axis, so bars visibly shrink as the
  slider moves forward) and a Gantt-style chart of each rendement period's served, suspended and remaining months.
  Periods of non-activity are shown in orange on that chart, on a row of their own with their exact dates, and on the
  months of the rendement periods they suspend. By default, the chart is cut off where the rendement periods really
  end, under the [maximum total rendement period](law.md#maximum-total-rendement-period-5): a period forgiven sooner
  stays suspended on the chart up to there, as it would have been behind the more recent ones, hatched from the date
  it is forgiven ("Suspended, forgiven") - which depends on the cap mode selected. The "Full schedule"
  switch above the chart shows instead the rendement periods as they would have been without that maximum: the months
  forgiven are shown in light grey, with the amount forgiven, where they would have been served, i.e. after the months
  the period would still have been suspended behind the more recent ones. The PDF report follows the switch.
- **Key figures** - cards for the total owed, the rendement period (start and end dates) and the current month's
  rendement rate.
- **Explanation panel** - restates the [criteria of the law](law.md#rules) with the actual numbers of the simulation,
  and calls out any option [beyond the law](beyond-the-law.md) in use. For the maximum total rendement period, it
  explains the cap mode selected with the figures it is counted on at the departure date (months of rendement served
  in the current bunch and when it reaches 15 years, or the periods that reached 15 years and the next one to do so)
  and, if different, the amount the other cap mode would give.
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
