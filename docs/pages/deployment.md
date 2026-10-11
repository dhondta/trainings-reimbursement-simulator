# Deployment

This page covers serving the [web dashboard](dashboard.md) to several users.

## Sign-in and sessions

Unless started with `--local`, the dashboard requires signing in, so that uploaded CSVs stay private per person. A
signed-in user's uploads are saved under `sessions/<key>/`, where `<key>` is `SHA256(identity + salt)` - the identity
itself (email or username) is never written to disk, only its salted hash.

The sign-in method is chosen with `--auth` (default: `otp-smtp`):

```bash
python3 src/dash_app.py --auth otp-smtp     # emailed one-time code, sent via SMTP (the default)
python3 src/dash_app.py --auth otp-http     # same code, sent via SendGrid's HTTP API instead
python3 src/dash_app.py --auth password     # username/password, via a login form
python3 src/dash_app.py --auth basic        # same username/password, via a shared HTTP Basic prompt
python3 src/dash_app.py --auth oauth-google # delegates to Google sign-in
```

- **`otp-smtp`** - an 8-digit code is emailed via SMTP if configured (see below); otherwise it is printed to the server
  console, so the app is fully usable for local testing without any email setup.
- **`otp-http`** - identical flow, but the code is sent through SendGrid's HTTP API instead of opening a raw SMTP
  socket. Useful on hosts that block outbound SMTP ports (e.g. PythonAnywhere's free/lower tiers).
- **`password`** and **`basic`** - check a username/password against `AUTH_USERS` (below). `password` shows a login
  form inside the app, `basic` instead gates every request behind one shared browser-native HTTP Basic prompt (so there
  is no real "sign out" in that mode - browsers cache Basic credentials until closed). Generate a hash for `AUTH_USERS`
  with:
  ```bash
  python3 src/dash_app.py --hash-password 'your-password-here'
  ```
- **`oauth-google`** - sign-in is delegated to Google; requires an OAuth 2.0 client registered in
  [Google Cloud Console](https://console.cloud.google.com/) with `GOOGLE_REDIRECT_URI` (below) added as an authorized
  redirect URI, e.g. `https://<your-host>/auth/google/callback`.

`--local` skips sign-in entirely: the main view loads directly and any upload is saved to the application's folder. Use
it only when you are the sole user, since it removes the per-person isolation described above. It takes priority over
`--auth`.

## Configuration (environment variables)

All optional - the app works out of the box without any of them (falling back to console-logged codes under the default
`--auth otp-smtp`).

| Variable | Default | Purpose |
|---|---|---|
| `SMTP_HOST` | *(unset)* | SMTP server used to email the code (`--auth otp-smtp`). Without it, codes are printed to the console instead. |
| `SMTP_PORT` | `587` | SMTP port (STARTTLS). |
| `SMTP_USERNAME` | *(unset)* | SMTP login - for most providers this must be the **full email address**, not a label. |
| `SMTP_PASSWORD` | *(unset)* | SMTP password (e.g. a Gmail App Password, entered **without spaces**). |
| `SMTP_FROM` | `SMTP_USERNAME` | `From:` address on the code email, for both `otp-smtp` and `otp-http`. |
| `SENDGRID_API_KEY` | *(unset)* | SendGrid API key used to send the code over HTTPS (`--auth otp-http`). Without it, codes are printed to the console instead. |
| `AUTH_USERS` | *(unset)* | `user1=hash1,user2=hash2` credential list for `--auth password` / `--auth basic` (hashes from `--hash-password`). |
| `GOOGLE_CLIENT_ID` | *(unset)* | OAuth 2.0 client ID for `--auth oauth-google`. |
| `GOOGLE_CLIENT_SECRET` | *(unset)* | OAuth 2.0 client secret for `--auth oauth-google`. |
| `GOOGLE_REDIRECT_URI` | *(unset)* | Must exactly match the redirect URI registered in Google Cloud Console, e.g. `https://<host>/auth/google/callback`. |
| `CAP_YEARS` | `15` | Maximum total of cumulated rendement periods, in years. Overridden by `--cap-years`. See [Beyond the law](beyond-the-law.md#other-maximum-total-rendement-period). |
| `CAP_MODE` | `bunch` | How the maximum total rendement period applies, initially (each visitor can change it with the cap mode selector): `bunch` or `period`. Overridden by `--cap-mode`. See [the law](law.md#maximum-total-rendement-period-5). |
| `MIN_RENDEMENT_RATE` | *(unset)* | Minimum rendement rate in €/month. Overridden by `--min-rate`. See [Beyond the law](beyond-the-law.md#minimum-rendement-rate). |
| `MAX_RENDEMENT_RATE` | *(unset)* | Maximum rendement rate in €/month. Overridden by `--max-rate`. See [Beyond the law](beyond-the-law.md#maximum-rendement-rate). |
| `POSTPONE_REMAINDER` | *(unset)* | Remainder in € below which a period's last month is merged into the previous one. Overridden by `--postpone-remainder`. See [Beyond the law](beyond-the-law.md#postponed-remainder). |
| `UPDATE_INDEX_VALUES` | *(unset)* | `1`, `true` or `yes` [updates the indexation table](input-files.md#updating-the-table) when the app starts, then on the first day of every month at midnight. Enabled by `--update-index-values`. |
| `SECURE_COOKIES` | *(enabled)* | `0`, `false` or `no` lets the session cookie be sent over plain HTTP (otherwise HTTPS only, unless `--local`) - not recommended, see [Security](security.md#a02-security-misconfiguration). |
| `SESSION_SALT` | auto-generated, persisted to `src/.session_salt` | Salt used to hash identities into session keys. |
| `FLASK_SECRET_KEY` | auto-generated, persisted to `src/.flask_secret` | Signs the session cookie. |

`SESSION_SALT` and `FLASK_SECRET_KEY` are generated once on first run and written to local dotfiles (ignored by Git) so
that sessions and uploaded files survive app restarts. Set them explicitly (e.g. via your deployment's secret manager)
if you would rather not rely on files on disk.

## Production server

`src/wsgi.py` is the entry point for a WSGI server, e.g. with [Gunicorn](https://gunicorn.org/):

```bash
cd src
gunicorn --workers 1 --threads 4 --bind 0.0.0.0:8050 wsgi:server
```

Keep a single worker: the pending sign-in state of `otp-smtp`, `otp-http` and `oauth-google` (and the PDF export
cooldown) is held in memory per process, so a request handled by one worker would not see state set by another, and
each worker would run its own [monthly update of the indexation table](input-files.md#updating-the-table), only the
first one to find the new rows applying them without a restart. Use threads for concurrency instead.

As there is no command line there, `--local` and `--auth` are replaced by the `APP_LOCAL_MODE` (`1`, `true` or `yes`)
and `APP_AUTH_METHOD` environment variables.
