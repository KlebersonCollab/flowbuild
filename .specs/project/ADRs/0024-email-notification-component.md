# ADR 0024: Email Notification Component (SMTP Delivery)

## Status
Accepted

## Date
2026-10-07

## Context
Sending transactional emails, monitoring digests, system failure reports, and customer alerts is a core requirement for automation workflow engines.

While webhook components exist for Slack, Discord, and Telegram, email remains the universal protocol across all enterprise, business, and developer operations.
Interacting with SMTP servers requires:
1. Multi-mode connection support: Plain SMTP, STARTTLS (RFC 3207, port 587), and direct SMTPS / SSL (port 465).
2. Authenticated login via username and password / app password.
3. MIME multipart formatting supporting both rich HTML bodies and plaintext fallbacks.
4. Flexible recipient parsing supporting single or comma-separated lists of email addresses.
5. Non-blocking asynchronous execution so SMTP round-trip network latency does not block the asyncio event loop.

A dedicated `EmailNotificationComponent` provides native email dispatch capability directly from the FlowBuild visual canvas.

## Decision
1. **Component Design (`EmailNotificationComponent`)**:
   - Class name: `EmailNotificationComponent`
   - Display name: `"Email Notification"`
   - Category: `"Actions"`
   - Description: `"Sends transactional emails and alerts via standard SMTP with HTML and plain text support."`
   - Icon: `"mail"`
2. **Inputs**:
   - `smtp_host` (`StrInput`, required=True): SMTP server hostname (e.g., `smtp.gmail.com`, `smtp.sendgrid.net`).
   - `smtp_port` (`IntInput`, default=587): SMTP port (e.g., 587 for STARTTLS, 465 for SSL, 25 for plain).
   - `smtp_user` (`StrInput`, default=""): Authentication username or API user.
   - `smtp_password` (`StrInput`, default=""): Authentication password or API key.
   - `use_tls` (`BoolInput`, default=True): Enable STARTTLS upgrade.
   - `use_ssl` (`BoolInput`, default=False): Connect directly via SSL/TLS (`SMTP_SSL`).
   - `from_email` (`StrInput`, required=True): Sender address (e.g. `alerts@example.com`).
   - `to_email` (`StrInput`, required=True): Recipient address(es), comma-separated.
   - `subject` (`StrInput`, required=True): Email subject line (supports `{{VARIABLES}}`).
   - `body_html` (`StrInput`, default=""): HTML email body content.
   - `body_text` (`StrInput`, default=""): Plain text fallback content.
   - `timeout` (`IntInput`, default=20): Connection and send timeout in seconds.
3. **Outputs**:
   - `success` (`Output`, type="bool"): True if SMTP server accepted and dispatched the email.
   - `status_code` (`Output`, type="int"): 250 on successful dispatch or error code / 0 on failure.
   - `response` (`Output`, type="str"): Success status summary or error diagnostics.
   - `recipients_count` (`Output`, type="int"): Number of recipients reached.
4. **Execution Semantics & Resilience**:
   - Runs synchronous `smtplib` operations inside non-blocking `asyncio.to_thread`.
   - Validates required inputs (`smtp_host`, `from_email`, `to_email`, `subject`, and either `body_html` or `body_text`).
   - Constructs standard `MIMEMultipart("alternative")` payloads.
   - Traps authentication failures, connection timeouts, and socket errors without crashing the DAG runner, emitting `success: False` with clear error details.
5. **Frontend Canvas & Palette Integration**:
   - In `ComponentPalette.vue` and `CustomNode.vue`, map `email` / `mail` to `Mail` icon and Violet styling (`text-violet-400 bg-violet-500/10 border-violet-500/30`).

## Consequences
- **Positive**: Native enterprise-grade email dispatching directly within workflows.
- **Completeness**: Completes the core Messaging & Notifications roadmap cluster (Slack, Discord, Telegram, Email).
- **Safety**: Fully non-blocking via `asyncio.to_thread` with granular exception isolation.
- **Backwards Compatibility**: 100% additive; no breaking changes.
