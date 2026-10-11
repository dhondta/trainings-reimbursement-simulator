""" Automatic update of the indexation table (--update-index-values): once when the app starts, then on the first day
of every month at midnight (server local time), the new indexations are appended to index_values.csv from Statbel's
smoothed health index (see simulator.update_index_values), and the table in use is reloaded in place, so that the
running app applies them without a restart. """
from __future__ import annotations

import threading
from datetime import datetime, timedelta

from simulator import INDEX_VALUES_CSV, add_months, update_index_values

# The wait before the next run is split into steps of at most this duration, the time left being computed anew after
#  each of them, so that a change of the system clock (daylight saving time, suspend, NTP) does not shift the run.
MAX_WAIT = timedelta(hours=1)
# When the update fails (e.g. Statbel unreachable), it is retried this often, at most this many times, then given up
#  until the next month.
RETRY_DELAY = timedelta(hours=1)
RETRIES = 23

_started = threading.Lock()
_stop = threading.Event()


def next_run(now: datetime) -> datetime:
    """ The first day of the month following now's, at midnight. """
    return datetime.combine(add_months(now.date().replace(day=1), 1), datetime.min.time())


def _log(message: str):
    print(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] {message}", flush=True)


def _wait_until(moment: datetime) -> bool:
    """ Waits until moment, returning False if the scheduler was stopped in the meantime. """
    while (left := moment - datetime.now()) > timedelta(0):
        if _stop.wait(min(left, MAX_WAIT).total_seconds()):
            return False
    return True


def _update() -> bool:
    try:
        new_rows = update_index_values()
    except Exception as exc:
        _log(f"Update of {INDEX_VALUES_CSV.name} failed: {exc}")
        return False
    _log(f"Update of {INDEX_VALUES_CSV.name}: {len(new_rows)} new indexation(s)")
    return True


def _update_with_retries(moment: datetime) -> bool:
    """ Updates at moment (already reached), retrying after a failure; returns False if the scheduler was stopped. """
    for attempt in range(RETRIES + 1):
        if _update() or attempt == RETRIES:
            return True
        if not _wait_until(moment + RETRY_DELAY * (attempt + 1)):
            return False
    return True


def _run():
    if not _update_with_retries(datetime.now()):
        return
    while _wait_until(moment := next_run(datetime.now())):
        if not _update_with_retries(moment):
            return


def start_monthly_index_update() -> bool:
    """ Starts the update in a background thread, once per process (later calls do nothing): at once, then monthly.
     Returns whether it was started by this call. """
    if not _started.acquire(blocking=False):
        return False
    threading.Thread(target=_run, name="monthly-index-update", daemon=True).start()
    _log(f"Update of {INDEX_VALUES_CSV.name} started, then monthly - next on "
         f"{next_run(datetime.now()):%d/%m/%Y at %H:%M}")
    return True
