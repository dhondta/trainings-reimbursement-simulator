""" Assembles the Dash app: creates it (via .instance), applies Flask session settings from config, and imports the
auth/layout/callbacks modules so their route and callback decorators register against it. Import this module (or the
dash_app.py shim at the repo root) to get a fully wired `app`."""
from datetime import timedelta

import plotly.graph_objects as go
import plotly.io as pio

from . import config
from .instance import app
from .strings import STRINGS

app.title = STRINGS[config.DEFAULT_LANG]["app_title"]
app.server.secret_key = config.FLASK_SECRET_KEY
app.server.permanent_session_lifetime = timedelta(days=30)
# The session cookie is not readable by scripts, and not sent along with cross-site requests (CSRF).
app.server.config.update(SESSION_COOKIE_HTTPONLY=True, SESSION_COOKIE_SAMESITE="Lax")


def apply_cookie_policy() -> None:
    """ Restricts the session cookie to HTTPS unless in LOCAL_MODE (see config.SECURE_COOKIES) - to be called once
     LOCAL_MODE is known (see cli.py and wsgi.py). """
    app.server.config["SESSION_COOKIE_SECURE"] = config.SECURE_COOKIES and not config.LOCAL_MODE


@app.server.after_request
def security_headers(response):
    """ Headers hardening every response: no MIME sniffing, no framing by other sites (clickjacking), and no full
     URLs leaked to other sites. """
    response.headers.setdefault("X-Content-Type-Options", "nosniff")
    response.headers.setdefault("X-Frame-Options", "DENY")
    response.headers.setdefault("Content-Security-Policy", "frame-ancestors 'none'")
    response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
    return response
# Charts match the Bootstrap theme: a clean white base, with the theme's font and text color on top of it.
pio.templates["simulator"] = go.layout.Template(layout={'font': {'family': config.THEME_FONT,
                                                                 'color': config.THEME_COLORS["body"]},
                                                        'title': {'font': {'size': 16}}})
pio.templates.default = "plotly_white+simulator"
# Night mode: the same, in the light text color of Bootstrap's dark mode, over the card's background.
pio.templates["simulator_dark"] = go.layout.Template(layout={'font': {'family': config.THEME_FONT, 'color': "#DEE2E6"},
                                                             'title': {'font': {'size': 16}},
                                                             'paper_bgcolor': "rgba(0, 0, 0, 0)",
                                                             'plot_bgcolor': "rgba(0, 0, 0, 0)"})

# Order matters: auth defines render_login_view, which layout's render_page needs; callbacks has no such dependency
#  but is kept last for readability. Each import's only purpose is its side effect of registering Flask routes/Dash
#  callbacks against the `app` created above (see .instance's docstring for why this avoids an import cycle).
from . import auth       # noqa: E402,F401
from . import layout     # noqa: E402,F401
from . import callbacks  # noqa: E402,F401

