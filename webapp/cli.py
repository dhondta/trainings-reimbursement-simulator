"""Command-line entry point: `python3 dash_app.py [options]` (or `python -m webapp`) - see the --help text below for
the available sign-in methods and flags."""
from __future__ import annotations

import argparse

from werkzeug.security import generate_password_hash

from simulator import REPAYMENT_MONTHS, parse_decimal

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
    parser.add_argument("--cap-years", type=int, default=config.CAP_YEARS,
                         help="maximum validity of a rendement period, in years (default: CAP_YEARS env var, else "
                              "15 years as of art. 179, §5)")
    parser.add_argument("--min-rate", type=parse_decimal, default=config.MIN_RENDEMENT_RATE,
                         help="minimum rendement rate in € per month, shortening the rendement period of cheaper "
                              "courses; base amount, indexed every month like the threshold (default: "
                              "MIN_RENDEMENT_RATE env var, else none - not as of the law, which always spreads it "
                              f"over {REPAYMENT_MONTHS} months)")
    parser.add_argument("--max-rate", type=parse_decimal, default=config.MAX_RENDEMENT_RATE,
                         help="maximum rendement rate in € per month, lengthening the rendement period of more "
                              "expensive courses; base amount, indexed every month like the threshold, and strictly "
                              "greater than --min-rate (default: MAX_RENDEMENT_RATE env var, else none - not as of the "
                              f"law, which always spreads it over {REPAYMENT_MONTHS} months)")
    parser.add_argument("--postpone-remainder", type=parse_decimal, default=config.POSTPONE_REMAINDER,
                         help="amount in € below which the last month of a rendement period is merged into the "
                              "previous one, ending the period one month earlier; base amount, indexed every month "
                              "like the threshold (default: POSTPONE_REMAINDER env var, else none - not as of the law)")
    args = parser.parse_args()
    if args.cap_years <= 0:
        parser.error("--cap-years must be strictly positive")
    if args.min_rate is not None and args.min_rate <= 0:
        parser.error("--min-rate must be strictly positive")
    if args.max_rate is not None and args.max_rate <= 0:
        parser.error("--max-rate must be strictly positive")
    if args.min_rate is not None and args.max_rate is not None and args.max_rate <= args.min_rate:
        parser.error("--max-rate must be strictly greater than --min-rate")
    if args.postpone_remainder is not None and args.postpone_remainder <= 0:
        parser.error("--postpone-remainder must be strictly positive")
    if args.hash_password is not None:
        print(generate_password_hash(args.hash_password))
        raise SystemExit(0)
    config.LOCAL_MODE = args.local
    config.AUTH_METHOD = args.auth
    config.CAP_YEARS = args.cap_years
    config.MIN_RENDEMENT_RATE = args.min_rate
    config.MAX_RENDEMENT_RATE = args.max_rate
    config.POSTPONE_REMAINDER = args.postpone_remainder
    # Debug mode keeps hot reload and server-side tracebacks, but not Dash's dev tools pane at the bottom of the page.
    app.run(debug=args.debug, dev_tools_ui=args.debug)


if __name__ == "__main__":
    main()

