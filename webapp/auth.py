"""Everything related to signing users in: the five --auth methods (otp-smtp, otp-http, password, basic,
oauth-google), the identity/session-key helpers the rest of the app relies on, and the login-view UI for whichever
method is active. Importing this module registers its Flask routes/before_request hook and Dash callbacks against
the shared `app` from .instance - see server.py, which is what actually triggers that import."""
from __future__ import annotations

import hashlib
import json
import secrets
import smtplib
import urllib.parse
import urllib.request
from datetime import datetime
from email.message import EmailMessage

from dash import Input, Output, State, dcc, html, no_update
from flask import Response, has_request_context, redirect, request, session
from werkzeug.security import check_password_hash

from . import config
from .instance import app
from .strings import STRINGS


def deliver_otp(to_email: str, code: str) -> bool:
    """ Dispatches to whichever OTP transport --auth selected. """
    return send_otp_email_http(to_email, code) if config.AUTH_METHOD == "otp-http" \
        else send_otp_email_smtp(to_email, code)


def render_login_view():
    """ Dispatches to whichever login form matches AUTH_METHOD. Never called under LOCAL_MODE, and never reached under
     --auth basic either (require_basic_auth rejects unauthenticated requests before Dash renders anything)."""
    if config.AUTH_METHOD == "password":
        return render_password_login_view()
    if config.AUTH_METHOD == "oauth-google":
        return render_oauth_login_view()
    return render_otp_login_view()


def render_oauth_login_view():
    return html.Div([
        html.H2(STRINGS[config.DEFAULT_LANG]["app_title"]),
        html.P("Sign in with your Google account to continue.", style={"color": "#555"}),
        html.A(html.Button("Sign in with Google", id="oauth-google-btn"), href="/auth/google/login"),
    ])


def render_otp_login_view():
    """ Shared by --auth otp-smtp and --auth otp-http: same email + code UI, only the delivery transport differs
     (see deliver_otp). """
    return html.Div([
        html.H2(STRINGS[config.DEFAULT_LANG]["app_title"]),
        html.P(
            "Enter your email address to receive an 8-digit verification code.",
            style={"color": "#555"},
        ),
        html.Div(
            style={"display": "flex", "gap": "8px", "marginBottom": "8px"},
            children=[
                dcc.Input(id="auth-email", type="email", placeholder="you@example.com",
                           style={"width": "260px"}),
                html.Button("Send code", id="auth-send-btn", n_clicks=0),
            ],
        ),
        html.Div(id="auth-status", style={"color": "#555", "marginBottom": "12px"}),
        html.Div(
            id="auth-otp-row",
            style={"display": "none", "gap": "8px", "alignItems": "center"},
            children=[
                dcc.Input(id="auth-otp", type="text", placeholder="8-digit code", maxLength=config.OTP_LENGTH,
                           style={"width": "140px"}),
                html.Button("Verify", id="auth-verify-btn", n_clicks=0),
            ],
        ),
        html.Div(id="auth-error", style={"color": "crimson", "marginTop": "8px"}),
    ])


def render_password_login_view():
    return html.Div([
        html.H2(STRINGS[config.DEFAULT_LANG]["app_title"]),
        html.P("Enter your username and password.", style={"color": "#555"}),
        html.Div(
            style={"display": "flex", "gap": "8px", "marginBottom": "8px"},
            children=[
                dcc.Input(id="auth-username", type="text", placeholder="username", style={"width": "180px"}),
                dcc.Input(id="auth-password", type="password", placeholder="password", style={"width": "180px"}),
                html.Button("Sign in", id="auth-password-btn", n_clicks=0),
            ],
        ),
        html.Div(id="auth-error", style={"color": "crimson", "marginTop": "8px"}),
    ])


def send_otp_email_http(to_email: str, code: str) -> bool:
    """ Emails the OTP through SendGrid's HTTP API (v3 /mail/send) if SENDGRID_API_KEY is configured; otherwise logs it
     to the server console, same fallback as send_otp_email_smtp. Reaches the provider over HTTPS instead of opening a
     raw SMTP socket, which some hosts (e.g. PythonAnywhere's free/lower tiers) block outbound. Used by --auth
     otp-http; swap this function's body for another provider's HTTP API if you don't use SendGrid. """
    if not config.SENDGRID_API_KEY:
        print(f"[dev] OTP for {to_email}: {code}  (SENDGRID_API_KEY not set - configure it to send real emails)")
        return False
    if not config.SMTP_FROM:
        raise RuntimeError("SMTP_FROM must be set to a verified sender address for --auth otp-http")
    payload = json.dumps({
        "personalizations": [{"to": [{"email": to_email}]}],
        "from": {"email": config.SMTP_FROM},
        "subject": "Your verification code",
        "content": [{"type": "text/plain",
                     "value": f"Your verification code is: {code}\n"
                              f"It expires in {int(config.OTP_TTL.total_seconds() // 60)} minutes."}],
    }).encode("utf-8")
    req = urllib.request.Request(
        "https://api.sendgrid.com/v3/mail/send", data=payload, method="POST",
        headers={"Authorization": f"Bearer {config.SENDGRID_API_KEY}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        if resp.status >= 300:
            raise RuntimeError(f"SendGrid returned HTTP {resp.status}")
    return True


def send_otp_email_smtp(to_email: str, code: str) -> bool:
    """ Emails the OTP if SMTP is configured (SMTP_HOST/SMTP_USERNAME/SMTP_PASSWORD env vars); otherwise logs it to the
     server console so the app stays usable in a local/dev environment without real email credentials. Returns True if
     an actual email was sent. Used by --auth otp-smtp. """
    if not (config.SMTP_HOST and config.SMTP_USERNAME and config.SMTP_PASSWORD):
        print(f"[dev] OTP for {to_email}: {code}  "
              f"(SMTP not configured - set SMTP_HOST/SMTP_USERNAME/SMTP_PASSWORD/SMTP_FROM to send real emails)")
        return False
    msg = EmailMessage()
    msg["Subject"] = "Your verification code"
    msg["From"] = config.SMTP_FROM
    msg["To"] = to_email
    msg.set_content(
        f"Your verification code is: {code}\nIt expires in {int(config.OTP_TTL.total_seconds() // 60)} minutes.")
    with smtplib.SMTP(config.SMTP_HOST, config.SMTP_PORT, timeout=10) as smtp:
        smtp.starttls()
        smtp.login(config.SMTP_USERNAME, config.SMTP_PASSWORD)
        smtp.send_message(msg)
    return True


def session_dir():
    """ In LOCAL_MODE, sign-in is skipped and uploaded CSV's are saved to the application's folder."""
    if config.LOCAL_MODE:
        return config.HERE
    if (key := session_key()) is None:
        return
    d = config.SESSIONS_ROOT / key
    d.mkdir(parents=True, exist_ok=True)
    return d


def session_key() -> str | None:
    """ SHA256 of the signed-in user's identity (see signed_in_identity) plus SESSION_SALT: identifies the same person
     across visits and app restarts without ever storing that identity itself in a folder name (anonymous on disk).
     Returns None outside of a request, or if nobody is signed in yet. """
    if not (identity := signed_in_identity()):
        return
    return hashlib.sha256(f"{identity}{config.SESSION_SALT}".encode("utf-8")).hexdigest()


def signed_in_identity() -> str | None:
    """ The identifier of whoever is currently signed in - an email address for otp-smtp/otp-http/oauth-google, or a
     username for password/basic - however AUTH_METHOD authenticated them. Returns None outside of a request, or if
     nobody is signed in. Basic Auth re-sends credentials with every request (RFC 7617) instead of using a session
     cookie, so it's read straight off the request; every other method stores it in the Flask session once
     verified. """
    if not has_request_context():
        return
    if config.AUTH_METHOD == "basic":
        return request.authorization.username if request.authorization else None
    return session.get("identity")


@app.server.route("/auth/google/callback")
def google_callback():
    """ Completes the flow started by google_login: exchanges the authorization code for a token, fetches the user's
     verified email, and signs them in the same way every other AUTH_METHOD does (session["identity"]). """
    state = request.args.get("state")
    expires = config.PENDING_OAUTH_STATES.pop(state, None) if state else None
    if not expires or datetime.now() > expires or "code" not in request.args:
        return "Sign-in failed or expired - please try again.", 400
    token_req = urllib.request.Request(
        "https://oauth2.googleapis.com/token", method="POST",
        data=urllib.parse.urlencode({
            "code": request.args["code"],
            "client_id": config.GOOGLE_CLIENT_ID,
            "client_secret": config.GOOGLE_CLIENT_SECRET,
            "redirect_uri": config.GOOGLE_REDIRECT_URI,
            "grant_type": "authorization_code",
        }).encode("utf-8"),
    )
    with urllib.request.urlopen(token_req, timeout=10) as resp:
        access_token = json.load(resp)["access_token"]
    userinfo_req = urllib.request.Request(
        "https://openidconnect.googleapis.com/v1/userinfo", headers={"Authorization": f"Bearer {access_token}"})
    with urllib.request.urlopen(userinfo_req, timeout=10) as resp:
        info = json.load(resp)
    if not info.get("email_verified"):
        return "Your Google account has no verified email address.", 400
    session["identity"] = info["email"]
    session.permanent = True
    return redirect("/")


@app.server.route("/auth/google/login")
def google_login():
    """ For --auth oauth-google: kicks off the OAuth 2.0 authorization-code flow with a real browser redirect (Dash
     callbacks can't do this - they answer AJAX requests, not full-page navigations). """
    state = secrets.token_urlsafe(24)
    config.PENDING_OAUTH_STATES[state] = datetime.now() + config.OAUTH_STATE_TTL
    params = urllib.parse.urlencode({
        "client_id": config.GOOGLE_CLIENT_ID,
        "redirect_uri": config.GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email",
        "state": state,
        "prompt": "select_account",
    })
    return redirect(f"https://accounts.google.com/o/oauth2/v2/auth?{params}")


@app.callback(Output("url", "pathname", allow_duplicate=True), Input("logout-btn", "n_clicks"),
              prevent_initial_call=True)
def logout(n_clicks):
    session.pop("identity", None)
    return f"/?signed-out={int(datetime.now().timestamp())}"


@app.server.before_request
def require_basic_auth():
    """ For --auth basic, gates every request behind a single shared HTTP Basic prompt (checked against AUTH_USERS)
     instead of Dash's login view, since Basic Auth credentials are supplied with the request itself (and cached by
     the browser) rather than through a page the app renders. No-op for every other AUTH_METHOD, and skipped entirely
     under LOCAL_MODE. """
    if config.LOCAL_MODE or config.AUTH_METHOD != "basic":
        return
    auth = request.authorization
    stored_hash = config.AUTH_USERS.get(auth.username) if auth else None
    if not auth or not stored_hash or not check_password_hash(stored_hash, auth.password or ""):
        return Response("Authentication required.", 401,
                        {"WWW-Authenticate": 'Basic realm="Training Reimbursement Simulator"'})


@app.callback(Output("auth-status", "children"), Output("auth-otp-row", "style"), Input("auth-send-btn", "n_clicks"),
              State("auth-email", "value"), prevent_initial_call=True)
def send_otp(n_clicks, email):
    email = (email or "").strip().lower()
    hidden, shown = {"display": "none"}, {"display": "flex", "gap": "8px", "alignItems": "center"}
    if not config.EMAIL_RE.match(email):
        return "Please enter a valid email address.", hidden
    now, pending = datetime.now(), config.PENDING_OTPS.get(email)
    if pending and now - pending["sent_at"] < config.OTP_RESEND_COOLDOWN:
        return "A code was already sent recently - please wait a moment.", shown
    code = f"{secrets.randbelow(10 ** config.OTP_LENGTH):0{config.OTP_LENGTH}d}"
    config.PENDING_OTPS[email] = {"code": code, "expires_at": now + config.OTP_TTL, "attempts": 0, "sent_at": now}
    try:
        sent = deliver_otp(email, code)
    except Exception as exc:
        return f"Could not send the email: {exc}", hidden
    if sent:
        return f"A verification code was sent to {email}.\n" \
                "Please check to make sure it hasn't been sent to your spam folder.", shown
    return "Email delivery is not configured on the server - check its console output for the code (dev mode).", shown


@app.callback(Output("auth-error", "children"), Output("url", "pathname", allow_duplicate=True),
              Input("auth-verify-btn", "n_clicks"), State("auth-email", "value"), State("auth-otp", "value"),
              prevent_initial_call=True)
def verify_otp(n_clicks, email, code):
    email = (email or "").strip().lower()
    code = (code or "").strip()
    pending = config.PENDING_OTPS.get(email)
    if not pending:
        return "Please request a code first.", no_update
    if datetime.now() > pending["expires_at"]:
        del config.PENDING_OTPS[email]
        return "This code has expired - please request a new one.", no_update
    if pending["attempts"] >= config.OTP_MAX_ATTEMPTS:
        del config.PENDING_OTPS[email]
        return "Too many attempts - please request a new code.", no_update
    if code != pending["code"]:
        pending["attempts"] += 1
        return "Incorrect code.", no_update
    del config.PENDING_OTPS[email]
    session["identity"] = email
    session.permanent = True
    return "", f"/?signed-in={int(datetime.now().timestamp())}"


@app.callback(Output("auth-error", "children", allow_duplicate=True), Output("url", "pathname", allow_duplicate=True),
              Input("auth-password-btn", "n_clicks"), State("auth-username", "value"), State("auth-password", "value"),
              prevent_initial_call=True)
def verify_password(n_clicks, username, password):
    username = (username or "").strip()
    stored_hash = config.AUTH_USERS.get(username)
    if not stored_hash or not check_password_hash(stored_hash, password or ""):
        return "Invalid username or password.", no_update
    session["identity"] = username
    session.permanent = True
    return "", f"/?signed-in={int(datetime.now().timestamp())}"

