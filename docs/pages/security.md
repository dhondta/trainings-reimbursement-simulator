# Security

This page reviews the [web dashboard](dashboard.md) against the [OWASP Top 10](https://owasp.org/Top10/) (2025
edition), the reference list of the most critical web application security risks, and explains how each one is
addressed. The [command-line tool](command-line.md) only reads local files given by its user, and has no network-facing
surface.

## Overview

The dashboard is a small [Plotly Dash](https://dash.plotly.com/) (Flask) application:

- it has **no database**, runs **no shell command** and deserializes **no untrusted data** (no `pickle`, no `eval`);
- the only data it stores are the **course lists uploaded** by signed-in users, each user in their own folder, named
  after a salted hash of their identity (`sessions/<SHA256(identity + salt)>/`);
- it renders everything through Dash components (React), which escape every value, or through ReportLab paragraphs,
  whose values are escaped explicitly;
- its only dependencies are Dash, Dash Bootstrap Components and ReportLab (see [Supply chain](#a03-software-supply-chain-failures)).

## A01 - Broken Access Control

- **Per-user storage** - The folder of a user is derived on the server from the identity stored in their signed session
  cookie (`auth.session_key`), never from a value sent by the browser, so that a user cannot reach another user's
  files.
- **No path traversal** - An uploaded file name is reduced to its last component (`Path(filename).name`), forced to
  `.csv`, and never overwrites an existing upload. A preset is only loaded by a name found in the list of the user's own
  presets (`presets_for_session`), never as a path.
- **Unauthenticated requests** - Without sign-in, uploads are refused (`auth_required`) and only the bundled presets,
  which are public, are listed. The calculation callbacks only compute on the data sent with the request, and read no
  stored file.
- **Local mode** - `--local` disables sign-in, for a single person running the app on their own machine: the
  development server then only listens on `127.0.0.1`.

## A02 - Security Misconfiguration

- **Session cookie** - `HttpOnly` (not readable by scripts), `SameSite=Lax` (not sent with cross-site requests,
  against CSRF) and `Secure` (HTTPS only) unless in local mode - see `SECURE_COOKIES` in
  [Deployment](deployment.md#configuration-environment-variables).
- **Security headers** - Every response carries `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY` and
  `Content-Security-Policy: frame-ancestors 'none'` (no framing by other sites, against clickjacking), and
  `Referrer-Policy: strict-origin-when-cross-origin`.
- **No debug mode** - Flask's debug mode and Dash's developer tools are off unless `--debug` is given, so that no
  traceback is ever shown to visitors.
- **Secrets** - The cookie-signing key and the session salt are generated randomly on first run (256 bits each),
  stored in files readable by the application's user only (mode `0600`) and ignored by Git, or taken from the
  environment (`FLASK_SECRET_KEY`, `SESSION_SALT`).

## A03 - Software Supply Chain Failures

- **Minimal dependencies** - Three direct dependencies (`requirements.txt`): Dash, Dash Bootstrap Components and
  ReportLab, with minimum versions.
- **Monitoring with Snyk** - The repository is monitored by [Snyk](https://snyk.io/), which scans `requirements.txt`
  and the transitive dependencies it pulls for known vulnerabilities; its status is shown by the
  [Known Vulnerabilities](https://snyk.io/test/github/dhondta/trainings-reimbursement-simulator?targetFile=requirements.txt)
  badge of the README. A vulnerable dependency is thus reported as soon as it is disclosed, and fixed by raising its
  minimum version.
- **Continuous integration** - The [GitHub workflow](development.md#continuous-integration) installs the dependencies
  from scratch and tests the application on every push, on several Python versions.

## A04 - Cryptographic Failures

- **Passwords** - Stored as Werkzeug hashes (scrypt, salted) in `AUTH_USERS`, generated with `--hash-password`; never
  in clear.
- **One-time codes** - Drawn with Python's `secrets` module (cryptographically secure), and compared in constant time.
- **Sessions** - Signed by Flask (HMAC) with the 256-bit secret key, so that they cannot be forged.
- **Pseudonymous storage** - The identity of a user (email or username) is never written to disk: their folder is
  named after its salted SHA-256 hash.
- **Transport** - TLS is expected from the server or reverse proxy in front of the app (see
  [Deployment](deployment.md#production-server)); the session cookie is then restricted to HTTPS. Emails are sent over
  STARTTLS (SMTP) or HTTPS (SendGrid), and the Google sign-in and Statbel's data are reached over HTTPS.

## A05 - Injection

- **No interpreter fed with user data** - No SQL, no shell, no template rendered from user input, no `eval`.
- **CSV parsing** - Uploads are parsed by Python's `csv` module, and every value is converted to its type (price as a
  decimal, dates as dates) or rejected with an error; course names are only displayed.
- **Cross-site scripting** - Values are displayed through Dash components, which escape them (no raw HTML is rendered
  anywhere), and inserted in the PDF report through `xml.sax.saxutils.escape`.
- **Email header injection** - The email address is checked against a pattern excluding spaces and line breaks before
  a code is sent, and the message is built with Python's `EmailMessage`.

## A06 - Insecure Design

The application limits by design what a single user can make it do:

| Limit | Value |
|---|---|
| Rows of a course list (uploads, presets, edits, every computation) | 50 |
| Size of an uploaded CSV (checked before it is even decoded) | 2 KiB |
| Uploaded CSVs kept per user | 10 |
| PDF reports per user | 1 per minute |
| One-time code requests per email address | 1 per 30 seconds |

Values sent by the browser are checked on the server whatever the interface allows (e.g. the number of rows, or the cap
mode, which falls back to the app-wide one if unknown), as requests can be forged.

## A07 - Authentication Failures

- **One-time codes** (`otp-smtp`, `otp-http`) - 8 digits, valid for 10 minutes and for 5 attempts, after which a new
  code must be requested (at most one every 30 seconds): guessing one has a chance of 5 in 100,000,000 per code.
- **Passwords** (`password`, `basic`) - After 5 failed attempts within 15 minutes, a username is locked out for the rest
  of that time, even with the right password (online brute force). An unknown username is checked against a dummy hash,
  so that it takes as long to reject as a known one (no username enumeration by timing), and both get the same message.
- **Google sign-in** (`oauth-google`) - Authorization code flow with a random, single-use `state` valid for 10 minutes
  (CSRF), and only a verified email address is accepted.
- **Sessions** - Expire after 30 days; signing out removes the identity from the session.

## A08 - Software or Data Integrity Failures

- **Uploads** - Validated as course lists (columns, values, number of rows) before being kept, and deleted otherwise.
- **Indexation table** - The [automatic update](input-files.md#updating-the-table) checks the rows derived from
  Statbel's data (each coefficient must be `1.02ⁿ`, following the previous one) before replacing the file, which is
  left unchanged on any error.
- **Sessions** - Signed, so that their content (the identity) cannot be altered by the browser.

## A09 - Security Logging and Alerting Failures

- **Security events** - Failed sign-ins, lockouts, incorrect one-time codes and failed code deliveries are logged on
  the server console with their time, as are the updates of the indexation table.
- **Dependencies** - New vulnerabilities in the dependencies are reported by [Snyk](#a03-software-supply-chain-failures).

The server console is meant to be collected by the hosting platform or the process manager (e.g. systemd's journal),
and HTTP access logs are kept by the server or reverse proxy in front of the app.

## A10 - Mishandling of Exceptional Conditions

- **Invalid input** - Every row of a course list is validated, and invalid ones are reported in the interface instead of
  failing; an invalid upload is rejected with its error and deleted.
- **No internal details leaked** - A failed code delivery shows a generic message, its details (e.g. of the mail server)
  being logged on the server only; without debug mode, an unexpected error never shows a traceback.
- **External services** - Calls to Google, SendGrid, the SMTP server and Statbel have timeouts, and a failed update of
  the indexation table is retried later, the app keeping the table it has.

## Responsibilities of the deployment

Some protections depend on how the dashboard is served (see [Deployment](deployment.md)):

- **TLS** - Serve the app over HTTPS, behind a reverse proxy or a platform providing it; the session cookie is
  restricted to HTTPS (`SECURE_COOKIES`).
- **Request rate limiting** - The app limits PDF reports, code requests and sign-in attempts, but not the number of
  requests as such: a reverse proxy or the hosting platform should limit them per client, against denial of service.
- **Email delivery** - Configure SMTP or SendGrid for the `otp-*` methods: without them, codes are printed on the server
  console, which is only meant for testing.
- **Single worker** - Pending codes, sign-in failures and the PDF cooldown are kept in memory per process (see
  [Production server](deployment.md#production-server)).

Known limitations, accepted given the application's purpose:

- **Sessions** - Sessions are stored in the signed cookie itself: signing out cannot invalidate a copy of the cookie
  before it expires. Changing `FLASK_SECRET_KEY` invalidates all sessions at once.
- **Scripts** - Dash relies on inline scripts, so the Content Security Policy only restricts framing; the Bootstrap
  theme and icons are loaded from the jsDelivr CDN.
- **CSV export** - A course list is exported as entered: a course named like a spreadsheet formula would be interpreted
  as such by a spreadsheet, which only affects the person who entered it.
