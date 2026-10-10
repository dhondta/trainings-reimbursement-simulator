# Command line

`src/simulator.py` prints, for one or more departure dates, the threshold test of every course, the details of the
reimbursement per course and the total to reimburse.

```bash
python3 src/simulator.py my-courses.csv [options]
```

`my-courses.csv` follows the [course list format](input-files.md#course-list).

## Options

| Option | Purpose |
|---|---|
| `--departure DATE` | Departure date (same formats as the `End Date` of the course list); can be repeated. By default, January 1st of each of the next four years. |
| `--timeline` | Also print the month-by-month timeline of active and suspended rendement periods, until the latest departure date. |
| `--cap-years N` | Validity cap of a rendement period, in years - [beyond the law](beyond-the-law.md#other-validity-cap) when other than 15. |
| `--min-rate R` | Minimum rendement rate, in €/month - [beyond the law](beyond-the-law.md#minimum-rendement-rate). |
| `--max-rate M` | Maximum rendement rate, in €/month - [beyond the law](beyond-the-law.md#maximum-rendement-rate). |
| `--postpone-remainder P` | Remainder below which a period's last month is merged into the previous one, in € - [beyond the law](beyond-the-law.md#postponed-remainder). |

The tool exits with code 1 when the course list cannot be loaded (missing file, missing columns, invalid values), and
with code 2 on invalid options.

## Examples

```bash
# As of the law, on two departure dates, with the timeline
python3 src/simulator.py my-courses.csv --departure 01/06/2027 --departure 01/01/2030 --timeline

# With a minimum rendement rate of 250 €/month base (beyond the law)
python3 src/simulator.py my-courses.csv --min-rate 250
```

See [The law](law.md#worked-example) for a commented output.
