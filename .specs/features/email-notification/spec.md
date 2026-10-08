# Specification: Email Notification Component (ADR 0024)

## 1. User Stories
- **US-1**: As a developer configuring workflow alerts, I want to send an email to specified recipients using my SMTP server credentials, so that critical alerts reach our inbox.
- **US-2**: As an operations engineer, I want to send HTML emails with a plain text alternative, so that email clients render formatted emails properly or fall back to plaintext.
- **US-3**: As a workflow creator, I want support for both STARTTLS (port 587) and SSL/TLS (port 465), so that I can connect to any email service provider.

## 2. Business Rules & Invariants
- **BR-1**: `smtp_host`, `from_email`, `to_email`, and `subject` are required inputs. Additionally, at least one of `body_html` or `body_text` must be provided.
- **BR-2**: `to_email` accepts a single address or multiple addresses separated by commas (e.g. `"alice@example.com, bob@example.com"`). Whitespace around addresses must be stripped.
- **BR-3**: If `use_ssl` is True, `smtplib.SMTP_SSL` must be used; otherwise, `smtplib.SMTP` is used. If `use_tls` is True and `use_ssl` is False, `server.starttls()` must be executed.
- **BR-4**: If `smtp_user` and `smtp_password` are provided, `server.login()` must be executed before sending.
- **BR-5**: Synchronous SMTP operations must be executed in a worker thread (`asyncio.to_thread`) to prevent blocking the event loop.
- **BR-6**: Successful transmission yields `success: True`, `status_code: 250`, `response: "Email sent successfully to N recipient(s)"`, and `recipients_count: N`.
- **BR-7**: SMTP errors (`SMTPAuthenticationError`, `SMTPConnectError`, timeouts) must be trapped gracefully without crashing the runner, producing `success: False`, `status_code: 0`, and the exception error text in `response`.

## 3. Acceptance Criteria (BDD)

### Happy Path (Success Scenarios)
- **AC-1: Plain Text and HTML Email via STARTTLS**
  - **Given** valid SMTP host `"smtp.example.com"`, port 587, `from_email="noreply@example.com"`, `to_email="dev@example.com"`, `subject="Deployment Report"`, `body_html="<h1>Success</h1>"`, and `body_text="Success"`
  - **When** the node executes against an SMTP server that accepts the message
  - **Then** output `success` is `True`, `status_code` is `250`, `recipients_count` is `1`, and `response` indicates success.

- **AC-2: Multi-Recipient Dispatch via Direct SSL**
  - **Given** `to_email="user1@example.com, user2@example.com, user3@example.com"`, `use_ssl=True`, port 465
  - **When** the node executes
  - **Then** output `recipients_count` is `3`, and the email is sent to all 3 addresses.

### Input & Validation Scenarios
- **AC-3: Missing Required Fields**
  - **Given** an empty `smtp_host`, empty `from_email`, empty `to_email`, empty `subject`, or empty bodies
  - **When** the component executes
  - **Then** `success` is `False`, `status_code` is `0`, and `response` indicates the missing parameter.

### Edge Cases & Exceptions (Resilience)
- **AC-4: SMTP Authentication Failure**
  - **Given** invalid credentials resulting in `smtplib.SMTPAuthenticationError`
  - **When** the component executes
  - **Then** `success` is `False`, `status_code` is `0`, and `response` captures the authentication error.

- **AC-5: Connection Timeout or Host Unreachable**
  - **Given** an unreachable host causing a socket timeout
  - **When** the component executes
  - **Then** `success` is `False`, `status_code` is `0`, and `response` contains the timeout exception.

- **AC-6: Variable Template Interpolation**
  - **Given** `subject="Alert for {{HOST}} - {{STATUS}}"` and `body_text="Server {{HOST}} is {{STATUS}}"`
  - **When** executed in `FlowRunner` with variables `HOST="db-1"`, `STATUS="HEALTHY"`
  - **Then** the sent email contains interpolated values `"Alert for db-1 - HEALTHY"`.

## 4. Test Data & Boundary Matrix
| Parameter / Field | Valid Inputs (Happy) | Invalid / Boundary Inputs (Edge) |
|---|---|---|
| `smtp_host` | `"smtp.gmail.com"`, `"127.0.0.1"` | `""`, `None` |
| `smtp_port` | `587`, `465`, `25` | `0`, `-1` |
| `from_email` | `"bot@domain.com"`, `"Alerts <bot@domain.com>"` | `""`, `None` |
| `to_email` | `"a@b.com"`, `"a@b.com, c@d.com"` | `""`, `None` |
| `subject` | `"Notice"`, `"Status {{CODE}}"` | `""`, `None` |
| `body_html` | `"<p>Hello</p>"`, `""` (if body_text provided) | `""` (when body_text is also empty) |
| `use_tls` / `use_ssl` | `True`, `False` | `None` |

## 5. Verification Sensors
| Sensor | Command / Target | Success Threshold |
|---|---|---|
| Backend Test Suite | `uv run pytest backend/tests/test_email_notification.py` | 100% pass |
| Frontend Test Suite | `npx vitest run frontend/tests/email_notification.test.ts` | 100% pass |
| Full Vitest Suite | `npx vitest run` | 100% pass |
| Frontend Build | `npm run build` in `frontend/` | Exit 0, 0 type errors |
| Backend Pytest Suite | `uv run pytest` in `backend/` | 100% pass |
