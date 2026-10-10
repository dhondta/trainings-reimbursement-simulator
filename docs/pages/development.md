# Development

## Project layout

| File | Purpose |
|---|---|
| `src/simulator.py` | Core simulation logic (threshold test, rendement periods, degressive reimbursement, timeline) and command-line tool. |
| `src/index_values.csv` | [Indexation coefficients](input-files.md#indexation-table) applied to the €5,000 threshold. |
| `src/example.csv` | Example [course list](input-files.md#course-list), also offered as a preset in the dashboard. |
| `src/webapp/` | The web dashboard package, built on top of `simulator.py`: `config.py` (settings and environment variables), `strings.py` (translations), `helpers.py` (course, preset and chart-support logic), `auth.py` (the five sign-in methods), `report.py` (PDF report), `instance.py`/`layout.py`/`callbacks.py`/`server.py` (the Dash app itself), `cli.py` (its command line). |
| `src/dash_app.py` | Entry point of the dashboard - `python3 src/dash_app.py ...` delegates to `webapp`. |
| `src/wsgi.py` | Entry point for [production servers](deployment.md#production-server). |
| `docs/` | This documentation. |

Dependencies: [Dash](https://pypi.org/project/dash/) (pulling in Flask and Plotly),
[Dash Bootstrap Components](https://pypi.org/project/dash-bootstrap-components/) (Bootswatch *Flatly* theme and
Bootstrap Icons, loaded from a CDN - see `THEME` in `src/webapp/config.py`) and
[ReportLab](https://pypi.org/project/reportlab/) (PDF reports).

## Continuous integration

The [build workflow](https://github.com/dhondta/trainings-reimbursement-simulator/actions/workflows/project-build.yml)
runs on every push and pull request to `main`:

- **Lint** - `flake8` on Python 3.10 to 3.13.
- **Simulator scenarios** - `simulator.py` is run on several course lists and options, at departure dates computed
  from the day of the run. Each simulation must succeed, and the totals must satisfy the properties of the
  [mechanisms beyond the law](beyond-the-law.md#comparing-with-the-law) (e.g. a minimum rate never increases the amount
  owed). Invalid inputs must be rejected with the expected exit code.
- **Dashboard startup** - `dash_app.py --local` must start and serve its page, layout and callbacks without error.
