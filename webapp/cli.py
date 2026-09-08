"""Command-line entry point: `python3 dash_app.py [options]` (or `python -m webapp`) - see the --help text below for
the available sign-in methods and flags."""
from __future__ import annotations

import argparse

from werkzeug.security import generate_password_hash

from . import config
from .server import app


def main() -> None:
    parser = argparse.ArgumentParser(description="Training reimbursement simulator - web dashboard")
    parser.add_argument("--debug", action="store_true", help="set debug mode (server runs on http://127.0.0.1:8050)")
    parser.add_argument("--local", action="store_true",
                         help="disable sign-in and session management - everyone shares a single local session "
                              "(useful for running the app on your own machine only)")
    parser.add_argument("--auth", choices=["otp-smtp", "otp-http", "password", "oauth-google", "basic"],
                         default="otp-smtp",
                         help="sign-in method to use when --local is not set (default: otp-smtp). otp-smtp: emailed "
                              "one-time code over SMTP (SMTP_* env vars). otp-http: same code emailed via SendGrid's "
                              "HTTP API (SENDGRID_API_KEY, SMTP_FROM) - for hosts that block outbound SMTP. password: "
                              "username/password checked against AUTH_USERS, via a login form. basic: same "
                              "AUTH_USERS credentials, via a single shared HTTP Basic prompt gating the whole app. "
                              "oauth-google: delegates to Google sign-in (GOOGLE_CLIENT_ID/GOOGLE_CLIENT_SECRET/"
                              "GOOGLE_REDIRECT_URI)")
    parser.add_argument("--hash-password", metavar="PASSWORD",
                         help="print a hash for PASSWORD suitable for the AUTH_USERS env var (used by --auth "
                              "password and --auth basic), then exit")
    args = parser.parse_args()
    if args.hash_password is not None:
        print(generate_password_hash(args.hash_password))
        raise SystemExit(0)
    config.LOCAL_MODE = args.local
    config.AUTH_METHOD = args.auth
    app.run(debug=args.debug)


if __name__ == "__main__":
    main()

