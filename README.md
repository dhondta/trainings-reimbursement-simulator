<p align="center"><img src="https://github.com/dhondta/trainings-reimbursement-simulator/raw/main/docs/pages/img/banner.png"></p>
<h1 align="center">Training Reimbursement Simulator</h1>
<h3 align="center">A simulator for Art. 179 of the Belgian <a href="https://www.ejustice.just.fgov.be/cgi_loi/change_lg.pl?language=fr&amp;la=F&amp;table_name=loi&amp;cn=2007022835">law of 28/02/2007</a> on the status of military personnel (as replaced by the <a href="https://www.ejustice.just.fgov.be/cgi_loi/change_lg.pl?language=fr&amp;la=F&amp;table_name=loi&amp;cn=2013073104">law of 31/07/2013</a>), about the rendement periods and the reimbursement of training costs.</h3>

[![Read The Docs](https://readthedocs.org/projects/trainings-reimbursement-simulator/badge/?version=latest)](https://trainings-reimbursement-simulator.readthedocs.io/en/latest/?badge=latest)
[![Build Status](https://github.com/dhondta/trainings-reimbursement-simulator/actions/workflows/project-build.yml/badge.svg)](https://github.com/dhondta/trainings-reimbursement-simulator/actions/workflows/project-build.yml)
[![Known Vulnerabilities](https://snyk.io/test/github/dhondta/trainings-reimbursement-simulator/badge.svg?targetFile=requirements.txt)](https://snyk.io/test/github/dhondta/trainings-reimbursement-simulator?targetFile=requirements.txt)

Given a list of trainings, it determines which ones trigger a reimbursement obligation, and simulates the degressive amount a military member would owe if they left the Armed Forces on a given date. See the [documentation](https://trainings-reimbursement-simulator.readthedocs.io/en/latest/?badge=latest) for the rules of the law, the options beyond it, and all the details.

## Setup

Python 3.10+ is required.

```bash
$ git clone https://github.com/dhondta/trainings-reimbursement-simulator
$ cd trainings-reimbursement-simulator
$ pip install -r requirements.txt
```

## Usage

Command line, printing a report for one or more departure dates (see the [course list format](https://trainings-reimbursement-simulator.readthedocs.io/en/latest/pages/input-files/#course-list)):

```bash
python3 src/simulator.py src/example.csv --departure 01/06/2027
```

Web dashboard, on <http://127.0.0.1:8050> (`--local` skips sign-in, for single-user use - see
[Deployment](https://trainings-reimbursement-simulator.readthedocs.io/en/latest/pages/deployment/) otherwise):

```bash
$ cd src
$ python3 dash_app.py --local
```
