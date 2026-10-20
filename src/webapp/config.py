"""App-wide constants and environment-driven configuration, shared by every other module in this package.

LOCAL_MODE and AUTH_METHOD are settings the CLI (see cli.py) and wsgi.py mutate after this module has already been
imported, as are CAP_YEARS and MIN_RENDEMENT_RATE (by the CLI only; both default to their environment variable) -
every other module reads them as `config.LOCAL_MODE` / `config.AUTH_METHOD` / ... (not via
`from .config import LOCAL_MODE`) so they see the current value instead of a stale copy taken at import time.
"""
from __future__ import annotations

import os
import re
import secrets
from datetime import date, datetime, timedelta
from pathlib import Path

import dash_bootstrap_components as dbc

from simulator import CAP_MODE as DEFAULT_CAP_MODE, CAP_MODES, CAP_YEARS as LAW_CAP_YEARS, add_months, load_courses, \
                      parse_decimal

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
        path.chmod(0o600)  # Readable by the app's own user only.
        return path.read_text().strip()
    value = secrets.token_hex(32)
    path.touch(mode=0o600)
    path.write_text(value)
    return value


def is_course_csv(path: Path) -> bool:
    """ Whether a file is a valid course list, i.e. a CSV that the upload itself would accept (Course, Price, End Date
     columns with parseable values, and an optional Bundle column) - which de facto excludes other data CSVs such as the indexation table."""
    if path.suffix != ".csv":
        return False
    try:
        load_courses(path)
    except Exception:
        return False
    return True


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


# Maximum total of cumulated rendement periods in years (art. 179, §5; --cap-years CLI flag): 15 years as of the law.
CAP_YEARS = int(os.environ.get("CAP_YEARS") or LAW_CAP_YEARS)
if CAP_YEARS <= 0:
    raise ValueError("CAP_YEARS must be strictly positive")
# How the maximum total rendement period applies initially (--cap-mode CLI flag; each visitor can change it): per bunch
#  of cumulated periods (default) or per rendement period - the two readings of art. 179, §5 (see simulator.CAP_MODES).
CAP_MODE = os.environ.get("CAP_MODE") or DEFAULT_CAP_MODE
if CAP_MODE not in CAP_MODES:
    raise ValueError(f"CAP_MODE must be one of: {', '.join(CAP_MODES)}")
COURSE_COLUMNS = ("Course", "Price", "End Date", "Bundle", "Start Date")  # CSV headers, for both import and export
#  (Bundle and Start Date optional - a row with a Start Date is a period of non-activity, see simulator.Inactivity)
DEFAULT_LANG = "en"
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
EMPTY_ROW = {"Course": "", "Price": "", "End Date": "", "Bundle": "", "Start Date": ""}
FALLBACK_SLIDER_MONTHS = 60  # used when there is no valid period to size the range on
# Official references of the laws mentioned in the texts (see law_segments): their Justel number (the consolidated
#  legislation database of the Belgian Official Journal) per date, in the language of the text (French for English,
#  which Justel does not offer).
LAW_REFERENCES = {"28/02/2007": "2007022835", "31/07/2013": "2013073104"}
LAW_MENTION_RE = re.compile(r"(?:loi du|wet van|law of) (\d{2}/\d{2}/\d{4})")


def justel_url(number: str, lang: str) -> str:
    """ The consolidated text of a law on Justel, in Dutch for "nl", in French otherwise. """
    language, la, table = ("nl", "N", "wet") if lang == "nl" else ("fr", "F", "loi")
    return f"https://www.ejustice.just.fgov.be/cgi_loi/change_lg.pl?language={language}&la={la}&table_name={table}" \
           f"&cn={number}"


def law_segments(text: str, lang: str) -> list[tuple[str, str | None]]:
    """ Splits text into (segment, url) pairs, url being the official reference of a law mentioned in it (see
     LAW_REFERENCES) and None elsewhere - to render the mentions of laws as hyperlinks. """
    segments, last = [], 0
    for match in LAW_MENTION_RE.finditer(text):
        if (number := LAW_REFERENCES.get(match.group(1))) is None:
            continue
        segments += [(text[last:match.start()], None), (match.group(0), justel_url(number, lang))]
        last = match.end()
    segments.append((text[last:], None))
    return [(segment, url) for segment, url in segments if segment]


LANGUAGE_OPTIONS = [{"label": "EN", "value": "en"}, {"label": "FR", "value": "fr"}, {"label": "NL", "value": "nl"}]
# When True (set via the --local CLI flag), the sign-in/OTP flow is skipped entirely and every visitor shares a single
#  "local" session folder - meant for running the app on a single person's own machine, not for a multi-user deployment.
LOCAL_MODE = False
# Which sign-in flow to use when LOCAL_MODE is False (set via the --auth CLI flag): "otp-smtp" (default) emails a code
#  over SMTP; "otp-http" emails the same code via SendGrid's HTTP API instead, for hosts that block outbound SMTP;
#  "password" and "basic" check a username/password from AUTH_USERS (a Dash login form vs. a shared HTTP Basic
#  prompt); "oauth-google" delegates to Google sign-in. See auth.render_login_view and auth.signed_in_identity.
AUTH_METHOD = "otp-smtp"
# Whether the indexation table is updated when the app starts, then on the first day of every month at midnight while it
#  runs (see scheduler.py; --update-index-values CLI flag, or the UPDATE_INDEX_VALUES env var set to 1, true or yes).
UPDATE_INDEX_VALUES = os.environ.get("UPDATE_INDEX_VALUES", "").lower() in ("1", "true", "yes")
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
# Optional minimum rendement rate in € per month (see simulator.MIN_RENDEMENT_RATE; --min-rate CLI flag): unset keeps
#  the 24-month periods prescribed by the law, otherwise cheaper triggering courses get proportionally shorter periods.
#  It is a base amount, indexed like the threshold with the coefficient of each month served.
MIN_RENDEMENT_RATE = parse_decimal(os.environ["MIN_RENDEMENT_RATE"]) if os.environ.get("MIN_RENDEMENT_RATE") else None
if MIN_RENDEMENT_RATE is not None and MIN_RENDEMENT_RATE <= 0:
    raise ValueError("MIN_RENDEMENT_RATE must be strictly positive")
# Optional maximum rendement rate in € per month (see simulator.MAX_RENDEMENT_RATE; --max-rate CLI flag): unset keeps
#  the 24-month periods prescribed by the law, otherwise more expensive triggering courses get proportionally longer
#  periods. Indexed like MIN_RENDEMENT_RATE, and strictly greater than it when both are set.
MAX_RENDEMENT_RATE = parse_decimal(os.environ["MAX_RENDEMENT_RATE"]) if os.environ.get("MAX_RENDEMENT_RATE") else None
if MAX_RENDEMENT_RATE is not None and MAX_RENDEMENT_RATE <= 0:
    raise ValueError("MAX_RENDEMENT_RATE must be strictly positive")
if MIN_RENDEMENT_RATE is not None and MAX_RENDEMENT_RATE is not None and MAX_RENDEMENT_RATE <= MIN_RENDEMENT_RATE:
    raise ValueError("MAX_RENDEMENT_RATE must be strictly greater than MIN_RENDEMENT_RATE")
# Optional remainder in € below which a period's last month is merged into the previous one (see
#  simulator.POSTPONE_REMAINDER; --postpone-remainder CLI flag). It is a base amount, indexed like the threshold.
POSTPONE_REMAINDER = parse_decimal(os.environ["POSTPONE_REMAINDER"]) if os.environ.get("POSTPONE_REMAINDER") else None
if POSTPONE_REMAINDER is not None and POSTPONE_REMAINDER <= 0:
    raise ValueError("POSTPONE_REMAINDER must be strictly positive")
# Security limits: the most course rows a table may hold (enforced server-side on uploads, presets, added/pasted rows
#  and every computation), and the largest CSV file accepted by the "Import CSV" upload, in bytes.
MAX_COURSES = 50
MAX_UPLOAD_BYTES = 2 * 1024
# The most CSVs a user may keep uploaded (bundled presets don't count), and the minimum delay between two PDF exports by
#  the same user - tracked in memory per process (see wsgi.py on why a single worker is required), keyed by session key.
MAX_UPLOADS = 10
PDF_EXPORT_COOLDOWN = timedelta(minutes=1)
LAST_PDF_EXPORTS: dict[str, datetime] = {}  # session key -> time of that user's last PDF export
MS_PER_DAY = 24 * 60 * 60 * 1000
OAUTH_STATE_TTL = timedelta(minutes=10)
# Failed sign-ins tolerated per username (--auth password and --auth basic) within LOGIN_LOCKOUT, before any further
#  attempt for that username is refused until the oldest failure is that old - tracked in memory per process.
LOGIN_MAX_FAILURES = 5
LOGIN_LOCKOUT = timedelta(minutes=15)
FAILED_LOGINS: dict[str, list[datetime]] = {}  # username -> times of its recent failed sign-ins
OTP_LENGTH = 8
OTP_MAX_ATTEMPTS = 5
OTP_RESEND_COOLDOWN = timedelta(seconds=30)
OTP_TTL = timedelta(minutes=10)
PENDING_OTPS: dict[str, dict] = {}  # normalized email -> {"code", "expires_at", "attempts", "sent_at"}
PENDING_OAUTH_STATES: dict[str, datetime] = {}  # CSRF state token -> expiry, for --auth oauth-google
# SHA256 salt for session keys: auto-generated once and persisted to a local dotfile unless overridden via the
#  environment, so returning users keep landing in the same folder across app restarts.
SESSION_SALT = _persisted_secret("SESSION_SALT", ".session_salt")
# Whether the session cookie is only sent over HTTPS (the app being served behind TLS), unless in LOCAL_MODE, where the
#  app is served over plain HTTP on 127.0.0.1. Set the SECURE_COOKIES env var to 0, false or no to serve sign-in over
#  plain HTTP (not recommended).
SECURE_COOKIES = os.environ.get("SECURE_COOKIES", "").lower() not in ("0", "false", "no")
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
# Presets bundled with the app, shared by every user: every CSV in the repo root that is a valid course list.
BUNDLED_PRESETS = {f.name: f for f in HERE.iterdir() if is_course_csv(f)}
DEFAULT_PRESET_NAME = next(iter(BUNDLED_PRESETS), None)
# Custom CSVs uploaded through the browser are private to the user that uploaded them: they are saved under
#  sessions/<key>/, where <key> is the SHA256 of that user's own identity plus SESSION_SALT (see auth.session_key).
#  That identity is never stored in the folder name, only its salted hash - anonymous on disk, while still reliably
#  mapping the same person back to the same folder across visits and app restarts.
SESSIONS_ROOT = HERE / "sessions"
SESSIONS_ROOT.mkdir(exist_ok=True)
# Look and feel: a Bootswatch theme for Bootstrap (swap it for any other dbc.themes.* in one line, keeping THEME_COLORS
#  and THEME_FONT in sync with it for the charts), plus Bootstrap Icons. Both are served from a CDN.
THEME = dbc.themes.FLATLY
THEME_COLORS = {'primary': "#2C3E50", 'secondary': "#95A5A6", 'success': "#18BC9C", 'info': "#3498DB",
                'warning': "#F39C12", 'danger': "#E74C3C", 'body': "#212529", 'border': "#DEE2E6", 'light': "#F8F9FA"}
THEME_FONT = "Lato, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif"
ICONS = dbc.icons.BOOTSTRAP
SLIDER_START = add_months(date(date.today().year, date.today().month, 1), 1)
# Shared by both charts: rendement periods (served / suspended / inactive / remaining / expired) and amounts per course
#  (served, i.e. fully paid off / remaining / expired, i.e. forgiven under the maximum total rendement period). The
#  forgiven parts are a lighter grey than the suspended months, to tell them apart on the rendement periods' chart.
STATUS_COLORS = {'served': THEME_COLORS["success"], 'suspended': THEME_COLORS["secondary"],
                 'inactive': THEME_COLORS["warning"], 'remaining': THEME_COLORS["danger"], 'expired': "#D5DBDB",
                 'lapsed': THEME_COLORS["secondary"]}
# Months a period would still have been suspended once forgiven ('lapsed', see helpers.with_forgiven_runs): hatched
#  with the 'lapsed' color over this background, to tell them from the months it is really suspended.
HATCH_BACKGROUND = "#EEF1F1"
# The charts per color mode (see the night mode toggle in layout.py): their Plotly template (see server.py), the color of
#  the marks drawn over the bars (the departure date, the comparison with the courses not bundled), and the background
#  of the hatching (see HATCH_BACKGROUND).
CHART_STYLES = {'light': {'template': "plotly_white+simulator", 'departure': "black",
                          'unbundled': THEME_COLORS["primary"], 'hatch': HATCH_BACKGROUND},
                'dark': {'template': "plotly_dark+simulator_dark", 'departure': THEME_COLORS["light"],
                         'unbundled': THEME_COLORS["light"], 'hatch': "#3A4147"}}

