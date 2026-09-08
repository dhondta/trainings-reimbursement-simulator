"""App-wide constants and environment-driven configuration, shared by every other module in this package.

LOCAL_MODE and AUTH_METHOD are the two settings the CLI (see cli.py) and wsgi.py mutate after this module has
already been imported - every other module reads them as `config.LOCAL_MODE` / `config.AUTH_METHOD` (not via
`from .config import LOCAL_MODE`) so they see the current value instead of a stale copy taken at import time.
"""
from __future__ import annotations

import os
import re
import secrets
from datetime import date, datetime, timedelta
from pathlib import Path

from simulator import INDEX_VALUES_CSV, add_months

HERE = Path(__file__).parent.parent  # repo root: webapp/ lives one level below it


def _persisted_secret(env_var: str, filename: str) -> str:
    """ Uses the value from the environment if given; otherwise generates one on first run and persists it to disk, so
     the salt/cookie-signing key (and thus every session key and folder derived from it) stays stable across app
     restarts instead of orphaning previously uploaded files."""
    value = os.environ.get(env_var)
    if value:
        return value
    path = HERE / filename
    if path.exists():
        return path.read_text().strip()
    value = secrets.token_hex(32)
    path.write_text(value)
    return value


def _parse_auth_users(raw: str) -> dict[str, str]:
    """ Parses AUTH_USERS ("user1=hash1,user2=hash2", where each hash comes from generate_password_hash - see the
     --hash-password CLI flag) into a dict. Shared by --auth password and --auth basic, which differ only in how the
     browser presents the credentials, not in how they're checked."""
    users = {}
    for entry in raw.split(","):
        username, _, pwhash = entry.strip().partition("=")
        if username and pwhash:
            users[username] = pwhash
    return users


CARD_STYLE = {'border': "1px solid #ddd", 'borderRadius': "8px", 'padding': "16px", 'textAlign': "center",
              'backgroundColor': "#fafafa"}
DEFAULT_LANG = "en"
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
EMPTY_ROW = {"Course": "", "Price": "", "End Date": ""}
FALLBACK_SLIDER_MONTHS = 60  # used when there is no valid period to size the range on
LANGUAGE_OPTIONS = [{"label": "EN", "value": "en"}, {"label": "FR", "value": "fr"}, {"label": "NL", "value": "nl"}]
# When True (set via the --local CLI flag), the sign-in/OTP flow is skipped entirely and every visitor shares a single
#  "local" session folder - meant for running the app on a single person's own machine, not for a multi-user deployment.
LOCAL_MODE = False
# Which sign-in flow to use when LOCAL_MODE is False (set via the --auth CLI flag): "otp-smtp" (default) emails a code
#  over SMTP; "otp-http" emails the same code via SendGrid's HTTP API instead, for hosts that block outbound SMTP;
#  "password" and "basic" check a username/password from AUTH_USERS (a Dash login form vs. a shared HTTP Basic
#  prompt); "oauth-google" delegates to Google sign-in. See auth.render_login_view and auth.signed_in_identity.
AUTH_METHOD = "otp-smtp"
# Username/password pairs for --auth password and --auth basic (see _parse_auth_users above).
AUTH_USERS = _parse_auth_users(os.environ.get("AUTH_USERS", ""))
# Signs the Flask session cookie: auto-generated once and persisted to a local dotfile unless overridden via the
#  environment, so sessions survive app restarts.
FLASK_SECRET_KEY = _persisted_secret("FLASK_SECRET_KEY", ".flask_secret")
# OAuth 2.0 app credentials for --auth oauth-google, from Google Cloud Console. GOOGLE_REDIRECT_URI must exactly match
#  the one registered there, e.g. "https://<host>/auth/google/callback".
GOOGLE_CLIENT_ID = os.environ.get("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.environ.get("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.environ.get("GOOGLE_REDIRECT_URI")
MS_PER_DAY = 24 * 60 * 60 * 1000
OAUTH_STATE_TTL = timedelta(minutes=10)
OTP_LENGTH = 8
OTP_MAX_ATTEMPTS = 5
OTP_RESEND_COOLDOWN = timedelta(seconds=30)
OTP_TTL = timedelta(minutes=10)
PENDING_OTPS: dict[str, dict] = {}  # normalized email -> {"code", "expires_at", "attempts", "sent_at"}
PENDING_OAUTH_STATES: dict[str, datetime] = {}  # CSRF state token -> expiry, for --auth oauth-google
# SHA256 salt for session keys: auto-generated once and persisted to a local dotfile unless overridden via the
#  environment, so returning users keep landing in the same folder across app restarts.
SESSION_SALT = _persisted_secret("SESSION_SALT", ".session_salt")
# SendGrid's HTTP API, used instead of SMTP when --auth otp-http is selected (see auth.send_otp_email_http): reached
#  over HTTPS, which stays usable on hosts that block outbound SMTP ports. Falls back to console logging, same as the
#  SMTP path, if unset. The "From" address (SMTP_FROM, below) is shared between both transports.
SENDGRID_API_KEY = os.environ.get("SENDGRID_API_KEY")
# SMTP is optional: without it, OTPs are printed to the server console instead, so the app stays usable for local
#  testing without real email credentials.
SMTP_HOST = os.environ.get("SMTP_HOST")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
SMTP_USERNAME = os.environ.get("SMTP_USERNAME")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD")
SMTP_FROM = os.environ.get("SMTP_FROM") or SMTP_USERNAME
# Presets bundled with the app, shared by every user (every course CSV in the repo root, i.e. not the indexation table).
BUNDLED_PRESETS = {f.name: f for f in HERE.iterdir() if f.suffix == ".csv" and f.name != INDEX_VALUES_CSV.name}
DEFAULT_PRESET_NAME = next(iter(BUNDLED_PRESETS), None)
# Custom CSVs uploaded through the browser are private to the user that uploaded them: they are saved under
#  sessions/<key>/, where <key> is the SHA256 of that user's own identity plus SESSION_SALT (see auth.session_key).
#  That identity is never stored in the folder name, only its salted hash - anonymous on disk, while still reliably
#  mapping the same person back to the same folder across visits and app restarts.
SESSIONS_ROOT = HERE / "sessions"
SESSIONS_ROOT.mkdir(exist_ok=True)
SLIDER_START = add_months(date(date.today().year, date.today().month, 1), 1)
STATUS_COLORS = {'served': "#4CAF50", 'suspended': "#9E9E9E", 'remaining': "#E74C3C"}

