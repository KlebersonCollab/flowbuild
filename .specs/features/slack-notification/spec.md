# Specification: Slack Notification Component (ADR 0020)

## 1. User Stories
- **US-1**: As a workflow creator, I want to send formatted notification messages directly to a Slack channel using an Incoming Webhook, so that team members are instantly notified of workflow events or errors.
- **US-2**: As an operations engineer, I want the Slack component to handle network errors or invalid URLs gracefully without failing the entire flow, so that notifications don't unexpectedly crash critical downstream tasks.
- **US-3**: As a workflow builder, I want to visually identify Slack notification nodes on the canvas with a distinct icon and badge color, so that notification points are easily distinguishable in the flow graph.

## 2. Business Rules & Invariants
- **BR-1**: `webhook_url` and `text` are required inputs. If missing or blank, the component must return `success: False` with descriptive diagnostic feedback without crashing.
- **BR-2**: When `status_code` is 200 and response body contains `"ok"`, `success` must be `True`. Any other status code must result in `success: False`.
- **BR-3**: Network errors, DNS resolution failures, or connection timeouts must be caught and return `success: False` with `status_code: 0` and error details in `response`.
- **BR-4**: Optional parameters (`channel`, `username`, `icon_emoji`, `blocks`, `attachments`) should only be included in the JSON payload when non-empty.

## 3. Acceptance Criteria (BDD)

### Happy Path (Success Scenarios)
- **AC-1: Standard Text Notification**
  - **Given** a valid Slack webhook URL and message `"Pipeline completed successfully"`
  - **When** the node executes against an endpoint returning HTTP 200 `"ok"`
  - **Then** output `success` is `True`, `status_code` is `200`, and `response` is `"ok"`.

- **AC-2: Rich Payload with Blocks and Custom Identity**
  - **Given** a webhook URL, message text, `username="AlertBot"`, `icon_emoji=":fire:"`, and Block Kit `blocks` array
  - **When** the node executes
  - **Then** the dispatched JSON request payload contains all configured fields and delivers successfully.

### Input & Validation Scenarios
- **AC-3: Missing Webhook URL or Text**
  - **Given** an empty `webhook_url` or empty `text`
  - **When** the component executes
  - **Then** `success` is `False`, `status_code` is `0`, and `response` reports the missing required field.

### Edge Cases & Exceptions (Resilience)
- **AC-4: Network Failure & Timeout Handling**
  - **Given** an unreachable host or connection timeout during webhook delivery
  - **When** the HTTP POST times out or encounters a connection error
  - **Then** the node catches the exception, outputs `success: False`, `status_code: 0`, and records the exception error in `response`.

- **AC-5: Upstream Variable Interpolation in Message**
  - **Given** a message formatted with template variables like `"Build {{BUILD_ID}} finished with status {{STATUS}}"`
  - **When** the node executes within `FlowRunner` with context variables
  - **Then** the resolved message text received by the webhook has interpolated values.

## 4. Test Data & Boundary Matrix
| Parameter / Field | Valid Inputs (Happy) | Invalid / Boundary Inputs (Edge) |
|---|---|---|
| `webhook_url` | `"https://hooks.slack.com/services/T00/B00/X00"` | `""`, `"not-a-url"`, `None` |
| `text` | `"Alert message"`, `"Alert with {{VAR}}"` | `""`, `None` |
| `channel` | `"#general"`, `"@alice"`, `""` | `None` |
| `username` | `"FlowBot"`, `""` | `None` |
| `icon_emoji` | `":bell:"`, `":warning:"`, `""` | `None` |
| `timeout` | `10`, `30`, `60` | `0`, `-5` |

## 5. Verification Sensors
| Sensor | Command / Target | Success Threshold |
|---|---|---|
| Backend Test Suite | `uv run pytest backend/tests/test_slack_notification.py` | 100% pass |
| Frontend Test Suite | `npx vitest run frontend/tests/slack_notification.test.ts` | 100% pass |
| Frontend Build | `npm run build` in `frontend/` | Exit 0, 0 type errors |
| SDD Integrity Sensor | `node .agents/scripts/verify-sdd-integrity.js` | 100% pass |
| Spec Drift Sensor | `node .agents/scripts/check-spec-drift.js` | 100% pass |

## 6. UI & Design System Tokens
- **Icon**: `MessageSquare` from `lucide-vue-next`.
- **Theme**: Rose accent (`text-rose-400 bg-rose-500/10 border-rose-500/30`), badge `bg-rose-500/15 text-rose-300 border-rose-500/30`, dot `bg-rose-400`.
- **Palette**: Categorized under `"Actions"`.
