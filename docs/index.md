<p align="center"><img src="pages/img/banner.png"></p>

# Training Reimbursement Simulator

A simulator for the rendement periods (*périodes de rendement* / *rendementsperiodes*) of Belgian military personnel,
and the reimbursement of training costs they imply, as set by **Art. 179 of the [law of 28/02/2007](https://www.ejustice.just.fgov.be/cgi_loi/change_lg.pl?language=fr&la=F&table_name=loi&cn=2007022835)** on their status
(as replaced by the [law of 31/07/2013](https://www.ejustice.just.fgov.be/cgi_loi/change_lg.pl?language=fr&la=F&table_name=loi&cn=2013073104) - see [Legal basis](pages/legal-basis.md)).

Given a list of trainings, it determines which ones trigger a reimbursement obligation, and simulates the degressive
amount a military member would owe if they left the Armed Forces on a given date.

It comes in two flavors, sharing the same simulation logic:

- **`simulator.py`** - a command-line tool that prints a full report for one or more departure dates.
- **`dash_app.py`** - an interactive web dashboard (built with [Plotly Dash](https://dash.plotly.com/)) with charts,
  a slider over departure dates, CSV upload/export, PDF reports and sign-in so several people can each keep their own
  course lists.

> **Not legal advice** - The simulator models the law as described in these pages. The indexation table and the
> maximum total rendement period are configurable and should be checked against the applicable text before relying on
> the results for anything official.

## Contents

The simulator serves two purposes, documented separately:

1. **[The law: Art. 179](pages/law.md)** - how the current law is modeled, with a worked example and how
   to simulate a situation strictly as of the law (the default behavior).
2. **[Beyond the law](pages/beyond-the-law.md)** - the optional mechanisms that the law does not provide (minimum and
   maximum rendement rates, postponed remainder, other maximum total rendement period), to assess their effect as a
   basis for an amendment proposal.

Reference:

- [Legal basis](pages/legal-basis.md) - the texts implemented, their history since 2000 and the open questions.
- [Input files](pages/input-files.md) - the CSV format of course lists and the indexation table.
- [Command line](pages/command-line.md) - every option of `simulator.py`.
- [Web dashboard](pages/dashboard.md) - the features of `dash_app.py`.
- [Deployment](pages/deployment.md) - sign-in methods, sessions, environment variables and production server.
- [Security](pages/security.md) - the OWASP Top 10 risks and how they are addressed, and dependency monitoring with Snyk.
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
