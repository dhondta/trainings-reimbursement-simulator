""" WSGI entry point for running the dashboard under a production server, e.g.:

    gunicorn --workers 1 --threads 4 --bind 0.0.0.0:8050 wsgi:server

Keep --workers to 1: sign-in state for the otp-smtp/otp-http/oauth-google methods (PENDING_OTPS /
PENDING_OAUTH_STATES in webapp/config.py) is held in an in-memory dict per process, so a request handled
by one worker wouldn't see state set by another. --auth password and --auth basic are stateless per
request and unaffected. Use --threads for concurrency instead of extra worker processes.
"""
import os

from webapp import config
from webapp.server import app as _dash_app

# Mirrors the --local/--auth CLI flags (see webapp/cli.py) for parity when not launching via
# `python3 dash_app.py`.
config.LOCAL_MODE = os.environ.get("APP_LOCAL_MODE", "").lower() in ("1", "true", "yes")
config.AUTH_METHOD = os.environ.get("APP_AUTH_METHOD", config.AUTH_METHOD)

application = server = _dash_app.server  # some WSGI hosts (mod_wsgi, uWSGI) look for this name by default

