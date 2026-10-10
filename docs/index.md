<p align="center"><img src="pages/img/banner.png"></p>

# Training Reimbursement Simulator

A simulator for the Belgian training-reimbursement clause (*clause d'écolage* / *opleidingsbeding*), as set by
**Art. 179 of the law of 31/07/2013**.

Given a list of trainings, it determines which ones trigger a reimbursement obligation, and simulates the degressive
amount an employee would owe if they left the company on a given date.

It comes in two flavors, sharing the same simulation logic:

- **`simulator.py`** - a command-line tool that prints a full report for one or more departure dates.
- **`dash_app.py`** - an interactive web dashboard (built with [Plotly Dash](https://dash.plotly.com/)) with charts,
  a slider over departure dates, CSV upload/export, PDF reports and sign-in so several people can each keep their own
  course lists.

> **Not legal advice** - The simulator models the law as described in these pages. The indexation table and the
> validity cap are configurable and should be checked against the applicable text before relying on the results for
> anything official.

## Contents

The simulator serves two purposes, documented separately:

1. **[The law of 31/07/2013, Art. 179](pages/law.md)** - how the current law is modeled, with a worked example and how
   to simulate a situation strictly as of the law (the default behavior).
2. **[Beyond the law](pages/beyond-the-law.md)** - the optional mechanisms that the law does not provide (minimum and
   maximum rendement rates, postponed remainder, other validity cap), to assess their effect as a basis for an
   amendment proposal.

Reference:

- [Input files](pages/input-files.md) - the CSV format of course lists and the indexation table.
- [Command line](pages/command-line.md) - every option of `simulator.py`.
- [Web dashboard](pages/dashboard.md) - the features of `dash_app.py`.
- [Deployment](pages/deployment.md) - sign-in methods, sessions, environment variables and production server.
- [Development](pages/development.md) - project layout and continuous integration.

## Quick start

```bash
git clone https://github.com/dhondta/trainings-reimbursement-simulator
cd trainings-reimbursement-simulator
pip install -r requirements.txt
python3 src/simulator.py src/example.csv
python3 src/dash_app.py --local    # then open http://127.0.0.1:8050
```

Python 3.10+ is required.
