<p align="center"><img src="https://github.com/dhondta/trainings-reimbursement-simulator/raw/main/docs/pages/img/banner.png"></p>
<h1 align="center">Training Reimbursement Simulator - Law of 31/07/13 Art. 179</h1>
<h3 align="center">A simulator for the Belgian training-reimbursement clause (*clause d'écolage* / *opleidingsbeding*, Art. 179 of the law of 31/07/2013).</h3>

[![Read The Docs](https://readthedocs.org/projects/python-malsearch/badge/?version=latest)](https://python-malsearch.readthedocs.io/en/latest/?badge=latest)
[![Build Status](https://github.com/dhondta/trainings-reimbursement-simulator/actions/workflows/project-build.yml/badge.svg)](https://github.com/dhondta/trainings-reimbursement-simulator/actions/workflows/project-build.yml)
[![Known Vulnerabilities](https://snyk.io/test/github/dhondta/trainings-reimbursement-simulator/badge.svg?targetFile=requirements.txt)](https://snyk.io/test/github/dhondta/trainings-reimbursement-simulator?targetFile=requirements.txt)

Given a list of trainings, it determines which ones trigger a reimbursement obligation, and
simulates the degressive amount an employee would owe if they left the company on a given date.

Two ways to use it:

- **`simulator.py`** - a command-line tool that prints a full report for one or more departure dates.
- **`dash_app.py`** - an interactive web dashboard (built with [Plotly Dash](https://dash.plotly.com/)) with charts, a slider over departure dates, CSV upload/export, and simple email-based sign-in so several people can each keep their own course lists.

## How the rule is modeled

- **Threshold**: a training triggers the obligation only if the cumulative cost of trainings completed within the trailing 24 months exceeds an indexed threshold (base €5,000, indexed since 2013 - see
  [`index_values.csv`](#indexation-table)).
- **Bundles** *(optional)*: courses sharing a same `Bundle` value in the [CSV](#csv-format) count as a single course, named after the bundle: its price is the sum of theirs and its end date the latest of theirs. It goes through the threshold test as one course and, if it triggers, gets a single rendement period starting after its last course.
- **Rendement period**: once triggered, the employee owes 24 months of service ("rendement") after that training. Leaving before it's complete means reimbursing `price × months still owed / 24`.
- **Priority / suspension**: when several trainings' rendement periods overlap, only the most recently triggered one accrues service each month - older ones are suspended until it is fully served.
- **Cap (Art. 179, §5)**: a rendement period's clause stops producing any effect 15 years after it started, regardless of how much of it was actually served - the remaining balance is forgiven, not carried forward.
- **Minimum rendement rate** *(optional, not part of the law)*: off by default. The law pays off `price / 24` per month of rendement; when a minimum rate `R` €/month is set, each month served pays off `max(price / 24, R × index)` instead, where `index` is the coefficient applicable in that month (like the €5,000 threshold, `R` is a base amount, e.g. 250 € gives 552 €/month with the 2.2080 coefficient). The reimbursement is the price not yet paid off, and the period ends when it is fully paid off (its last month settling the remainder) - so a cheap triggering course no longer ties the employee down for two full years at a low monthly rate, and the rate rises with the index during a period.
- **Maximum rendement rate** *(optional, not part of the law)*: off by default. The counterpart of the minimum rate: when a maximum rate `M` €/month is set, each month served pays off at most `M × index`, i.e. `min(max(price / 24, R × index), M × index)` - so an expensive triggering course takes longer than two years to pay off. `M` must be strictly greater than `R` when both are set.
- **Postponed remainder** *(optional, not part of the law)*: off by default. When a remainder `P` € is set and the last month of a period would only pay off less than `P × index` (a base amount indexed like `R` and `M`), that remainder is merged into the previous month served (which then pays off its rate plus the remainder, possibly above `M × index`), so the period ends one month earlier - even when a more recent period was served in between.

None of this is legal advice; the indexation table and the 15-year cap are configurable (see below) and should be checked against the applicable text before relying on this for anything official.

## Requirements

- Python 3.10+
- [Dash](https://pypi.org/project/dash/) (pulls in Flask and Plotly)
- [Dash Bootstrap Components](https://pypi.org/project/dash-bootstrap-components/) for the web dashboard's look (Bootswatch *Flatly* theme and Bootstrap Icons, loaded from a CDN - see `THEME` in `webapp/config.py`)

```bash
pip install -r requirements.txt
```

## Files

| File | Purpose |
|---|---|
| `index_values.csv` | Indexation coefficients applied to the €5,000 threshold - see [Indexation table](#indexation-table). |
| `simulator.py` | Core simulation logic (threshold test, rendement periods, degressive reimbursement, timeline) and CLI. |
| `webapp/` | The interactive web dashboard package, built on top of `simulator.py`: `config.py` (settings/env vars), `strings.py` (i18n), `helpers.py` (course/preset/chart-support logic), `auth.py` (the five sign-in methods), `instance.py`/`layout.py`/`callbacks.py`/`server.py` (the Dash app itself), `cli.py` (the `--local`/`--auth`/`--debug` CLI). |
| `dash_app.py` | Thin compatibility entry point - `python3 dash_app.py ...` delegates to `webapp`. |
| `wsgi.py` | WSGI entry point for production servers, e.g. `gunicorn --workers 1 --threads 4 -b 0.0.0.0:8050 wsgi:server`. |

## CSV format

Both the CLI and the web app expect a CSV with these headers:

```csv
Course,Price,End Date
A,4321.85,10/08/2013
B,5123.40,26/11/2014
```

An optional `Bundle` column groups courses into a single rendement period (see
[How the rule is modeled](#how-the-rule-is-modeled)):

```csv
Course,Price,End Date,Bundle
A,4321.85,10/08/2013,
B,5123.40,26/11/2014,GIAC
C,4980.00,15/02/2015,GIAC
```

- `Course`: any identifier (course code, name, …).
- `Price`: accepts `.` or `,` as decimal separator, thousand separators, and an optional `€` sign.
- `End Date`: `DD/MM/YYYY`, `DD/MM/YY`, `DD-MM-YYYY`, or `YYYY-MM-DD`.
- `Bundle` *(optional)*: any name, shared by the courses to group, and left empty for the others. It may not be named like a course outside of it.

### Indexation table

The threshold's indexation coefficients live in `index_values.csv`, read by both the CLI and the web app:

```csv
Start Date,Index Value
01/03/2026,2.1647
01/09/2026,2.2080
```

- `Start Date`: first day a coefficient applies (same date formats as above). Each period ends the day before the next one starts, and the last one stays in effect until a newer row is added - so a new index is a one-line append. Rows may be in any order; a duplicate start date is rejected.
- `Index Value`: the coefficient applied to the €5,000 base (same number formats as `Price`).

Source for the coefficients:
[BOSA - indexation](https://bosa.belgium.be/fr/themes/travailler-dans-la-fonction-publique/remuneration-et-avantages/traitement/indexation-0).
Restart the web app after editing the file, since it's read once at startup.

## Command-line usage

```bash
python3 simulator.py formations_me.csv
```

By default it reports the situation on Jan 1st of each of the next four years. Useful flags:

```bash
# One or more explicit departure dates (repeatable)
python3 simulator.py my-formations.csv --departure 01/06/2027 --departure 01/01/2030

# Also print the month-by-month active/suspended timeline
python3 simulator.py my-formations.csv --timeline

# Override the 15-year validity cap (Art. 179, §5), in years
python3 simulator.py my-formations.csv --cap-years 10

# Enforce a minimum rendement rate of 250 €/month base, indexed (not part of the law: shortens cheaper courses' periods)
python3 simulator.py my-formations.csv --min-rate 250

# Cap the rendement rate at 500 €/month base, indexed (not part of the law: lengthens pricier courses' periods)
python3 simulator.py my-formations.csv --min-rate 250 --max-rate 500

# Merge a period's last month into the previous one when it would pay off less than 100 € base, indexed
python3 simulator.py my-formations.csv --min-rate 250 --postpone-remainder 100
```

## Web dashboard

```bash
python3 dash_app.py
```

Then open <http://127.0.0.1:8050>. Run it with `--local` to skip sign-in entirely, for single-user local use:

```bash
python3 dash_app.py --local
```

The same `--cap-years`, `--min-rate`, `--max-rate` and `--postpone-remainder` options as the command-line tool are available, so their effect can be visualized too (they can also be set through the `CAP_YEARS` / `MIN_RENDEMENT_RATE` / `MAX_RENDEMENT_RATE` / `POSTPONE_REMAINDER` environment variables, e.g. under `wsgi.py`); any value departing from the law is called out in the dashboard's explanation panel:

```bash
python3 dash_app.py --local --cap-years 10 --min-rate 250
```

Features:

- Editable course table, kept sorted by end date (add/delete rows, or import a CSV), and export of the current table back to a CSV in the same format as for import. Prices and dates are reformatted as they're entered (e.g. `4.174,85 €` → `4174.85`, `2024-11-07` → `07/11/24`).
- Presets: every CSV in the repo root (plus the user's own uploads) that complies with the [CSV format](#csv-format) is offered in the preset dropdown; any other CSV, such as `index_values.csv`, is ignored.
- A slider over every month from the start of the first rendement period (to look back at past departure dates) up to the actual date the whole course list becomes fully resolved; it starts on next month. A course is only owed once it has been completed, i.e. for departure dates after its end date.
- A vertical bar chart of the degressive amount owed per course (fixed y-axis, so bars visibly shrink as you move the slider forward), a horizontal Gantt-style chart of each rendement period's served/suspended/remaining history, and cards for the total owed, the rendement period (start and end dates), and the current month's rendement rate.
- A dynamic explanation panel that restates the four criteria above with the actual numbers for the current simulation.
- A PDF report of the reimbursement plan for the selected departure date (key figures, threshold test, amount owed per course, both charts and the explanation panel), in the current UI language.
- English, French and Dutch UI (selector in the top-right).

### Sign-in and sessions

The dashboard requires signing in, so that uploaded CSVs stay private per person. A signed-in user's uploads are saved under `sessions/<key>/`, where `<key>` is `SHA256(identity + salt)` - the identity itself (email or username) is never written to disk, only its salted hash.

Choose the sign-in method with `--auth` (default: `otp-smtp`):

```bash
python3 dash_app.py --auth otp-smtp     # emailed one-time code, sent via SMTP (the default)
python3 dash_app.py --auth otp-http     # same code, sent via SendGrid's HTTP API instead
python3 dash_app.py --auth password     # username/password, via a login form
python3 dash_app.py --auth basic        # same username/password, via a shared HTTP Basic prompt
python3 dash_app.py --auth oauth-google # delegates to Google sign-in
```

- **`otp-smtp`** - an 8-digit code is emailed via SMTP if configured (see below); otherwise it's printed to the server console, so the app is fully usable for local testing without any email setup.
- **`otp-http`** - identical flow, but the code is sent through SendGrid's HTTP API instead of opening a raw SMTP socket. Useful on hosts that block outbound SMTP ports (e.g. PythonAnywhere's free/lower tiers).
- **`password`** and **`basic`** - check a username/password against `AUTH_USERS` (below); `password` shows a login form inside the app, `basic` instead gates every request behind one shared browser-native HTTP Basic prompt (so there's no real "sign out" in that mode - browsers cache Basic credentials until closed). Generate a hash for `AUTH_USERS` with:
  ```bash
  python3 dash_app.py --hash-password 'your-password-here'
  ```
- **`oauth-google`** - sign-in is delegated to Google; requires an OAuth 2.0 client registered in [Google Cloud Console](https://console.cloud.google.com/) with `GOOGLE_REDIRECT_URI` (below) added as an authorized redirect URI, e.g. `https://<your-host>/auth/google/callback`.

Pass `--local` to skip sign-in entirely - the main view loads directly and any upload is saved to the application's folder. Use this only when you're the sole user (e.g. running the app on your own machine), since it removes the per-person isolation described above, and it takes priority over `--auth`:

```bash
python3 dash_app.py --local
```

### Configuration (environment variables)

All optional - the app works out of the box without any of them (falling back to console-logged OTPs under the default `--auth otp-smtp`).

| Variable | Default | Purpose |
|---|---|---|
| `SMTP_HOST` | *(unset)* | SMTP server used to email the OTP (`--auth otp-smtp`). Without it, codes are printed to the console instead. |
| `SMTP_PORT` | `587` | SMTP port (STARTTLS). |
| `SMTP_USERNAME` | *(unset)* | SMTP login - for most providers this must be the **full email address**, not a label. |
| `SMTP_PASSWORD` | *(unset)* | SMTP password (e.g. a Gmail App Password, entered **without spaces**). |
| `SMTP_FROM` | `SMTP_USERNAME` | `From:` address on the OTP email, for both `otp-smtp` and `otp-http`. |
| `SENDGRID_API_KEY` | *(unset)* | SendGrid API key used to send the OTP over HTTPS (`--auth otp-http`). Without it, codes are printed to the console instead. |
| `AUTH_USERS` | *(unset)* | `user1=hash1,user2=hash2` credential list for `--auth password` / `--auth basic` (hashes from `--hash-password`). |
| `GOOGLE_CLIENT_ID` | *(unset)* | OAuth 2.0 client ID for `--auth oauth-google`. |
| `GOOGLE_CLIENT_SECRET` | *(unset)* | OAuth 2.0 client secret for `--auth oauth-google`. |
| `GOOGLE_REDIRECT_URI` | *(unset)* | Must exactly match the redirect URI registered in Google Cloud Console, e.g. `https://<host>/auth/google/callback`. |
| `CAP_YEARS` | `15` | Validity cap of a rendement period, in years (Art. 179, §5). Overridden by `--cap-years`. |
| `MIN_RENDEMENT_RATE` | *(unset)* | Minimum rendement rate in €/month, as a base amount indexed like the threshold (see [How the rule is modeled](#how-the-rule-is-modeled)). Unset keeps the law's 24-month periods. Overridden by `--min-rate`. |
| `MAX_RENDEMENT_RATE` | *(unset)* | Maximum rendement rate in €/month, indexed like `MIN_RENDEMENT_RATE` and strictly greater than it when both are set. Unset keeps the law's 24-month periods. Overridden by `--max-rate`. |
| `POSTPONE_REMAINDER` | *(unset)* | Remainder in €, as a base amount indexed like the threshold, below which a period's last month is merged into the previous one. Unset keeps the law's behavior. Overridden by `--postpone-remainder`. |
| `SESSION_SALT` | auto-generated, persisted to `.session_salt` | Salt used to hash identities into session keys. |
| `FLASK_SECRET_KEY` | auto-generated, persisted to `.flask_secret` | Signs the session cookie. |

`SESSION_SALT` and `FLASK_SECRET_KEY` are generated once on first run and written to local dotfiles so that sessions and uploaded files survive app restarts - set them explicitly (e.g. via your deployment's secret manager) if you'd rather not rely on files on disk.
