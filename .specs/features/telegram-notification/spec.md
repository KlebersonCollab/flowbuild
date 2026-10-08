# Specification: Telegram Notification Component (ADR 0023)

## 1. User Stories
- **US-1**: As a developer running an automation flow, I want to send an instant alert to a Telegram channel or group via my bot token, so that team members are notified of key events.
- **US-2**: As an engineer formatting alerts, I want to specify `parse_mode` as HTML or MarkdownV2, so that links, bold text, and code blocks render cleanly in Telegram.
- **US-3**: As a workflow creator, I want the node to output the dispatched `message_id`, so that downstream nodes can reference or track the specific message.

## 2. Business Rules & Invariants
- **BR-1**: `bot_token`, `chat_id`, and `message` are strictly required inputs. If any of these are missing or blank, execution must immediately return `success: False`, `status_code: 0`, and a descriptive error message without sending an HTTP request.
- **BR-2**: Requests must be POSTed as JSON to `https://api.telegram.org/bot<bot_token>/sendMessage`.
- **BR-3**: If `parse_mode` is `"None"`, the `parse_mode` property is omitted from the JSON payload.
- **BR-4**: If `disable_web_page_preview` is True, `"disable_web_page_preview": true` is included in the payload.
- **BR-5**: If `disable_notification` is True, `"disable_notification": true` is included in the payload.
- **BR-6**: Execution is considered successful if Telegram returns HTTP 200 and the JSON response has `"ok": true`. The output `message_id` is parsed from `result.message_id` (or 0 if absent).
- **BR-7**: Network errors, DNS resolution failures, or connection timeouts must be caught gracefully, setting `success: False`, `status_code: 0`, and setting `response` to the exception message.

## 3. Acceptance Criteria (BDD)

### Happy Path (Success Scenarios)
- **AC-1: Plain Text / HTML Notification Dispatch**
  - **Given** a valid bot token, chat ID `-1001234567890`, and message `<b>Deploy successful!</b>` with `parse_mode="HTML"`
  - **When** the node executes against the Telegram Bot API returning HTTP 200 with `{"ok": true, "result": {"message_id": 999}}`
  - **Then** output `success` is `True`, `status_code` is `200`, `message_id` is `999`, and `response` contains the raw JSON string.

- **AC-2: Silent Message and Disabled Previews**
  - **Given** `disable_notification=True` and `disable_web_page_preview=True`
  - **When** the node executes
  - **Then** the dispatched JSON request payload contains `"disable_notification": true` and `"disable_web_page_preview": true`.

### Input & Validation Scenarios
- **AC-3: Missing Credentials or Message**
  - **Given** an empty `bot_token`, empty `chat_id`, or empty `message`
  - **When** the component executes
  - **Then** `success` is `False`, `status_code` is `0`, `message_id` is `0`, and `response` reports the missing parameter.

### Edge Cases & Exceptions (Resilience)
- **AC-4: Telegram API Error Response (Invalid Token or Chat)**
  - **Given** an invalid chat ID or unauthorized token returning HTTP 400 with `{"ok": false, "error_code": 400, "description": "Bad Request: chat not found"}`
  - **When** the component executes
  - **Then** `success` is `False`, `status_code` is `400`, `message_id` is `0`, and `response` captures the Telegram error response.

- **AC-5: Network Timeout / Connection Failure**
  - **Given** an unreachable network host or request timeout
  - **When** the HTTP request is executed
  - **Then** the node outputs `success: False`, `status_code: 0`, `message_id` is `0`, and `response` contains the exception detail.

- **AC-6: Variable Template Interpolation**
  - **Given** a message string containing `{{ENVIRONMENT}} alert for {{SERVICE}}`
  - **When** the node is executed within `FlowRunner` with variables `ENVIRONMENT="prd"` and `SERVICE="payment"`
  - **Then** the payload sent to Telegram contains `"prd alert for payment"`.

## 4. Test Data & Boundary Matrix
| Parameter / Field | Valid Inputs (Happy) | Invalid / Boundary Inputs (Edge) |
|---|---|---|
| `bot_token` | `"123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11"` | `""`, `None` |
| `chat_id` | `"-1001234567890"`, `"@my_channel"`, `"987654321"` | `""`, `None` |
| `message` | `"Deployment complete"`, `"<b>Alert</b>"` | `""`, `None` |
| `parse_mode` | `"HTML"`, `"MarkdownV2"`, `"Markdown"`, `"None"` | `""` (defaults to `"HTML"`) |
| `disable_notification` | `True`, `False` | `None` |
| `timeout` | `15`, `30` | `0`, `-1` |

## 5. Verification Sensors
| Sensor | Command / Target | Success Threshold |
|---|---|---|
| Backend Test Suite | `uv run pytest backend/tests/test_telegram_notification.py` | 100% pass |
| Frontend Test Suite | `npx vitest run frontend/tests/telegram_notification.test.ts` | 100% pass |
| Full Vitest Suite | `npx vitest run` | 100% pass |
| Frontend Build | `npm run build` in `frontend/` | Exit 0, 0 type errors |
| Backend Pytest Suite | `uv run pytest` in `backend/` | 100% pass |
