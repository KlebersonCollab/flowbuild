# Specification: Discord Notification Component (ADR 0022)

## 1. User Stories
- **US-1**: As a developer running automation flows, I want to send formatted notification messages directly to a Discord channel via Webhook, so that my team receives instant alerts.
- **US-2**: As an operations engineer, I want to include rich embed cards with custom titles, descriptions, and accent colors, so that notifications are visually structured and readable.
- **US-3**: As a workflow creator, I want Discord's HTTP 204 No Content response to be treated as successful delivery, so that the workflow continues without false failure flags.

## 2. Business Rules & Invariants
- **BR-1**: `webhook_url` is required. Either `content`, `embed_title`, `embed_description`, or `embeds` must be non-empty. If missing, the node must return `success: False` with descriptive diagnostics.
- **BR-2**: Status codes 200 and 204 are considered successful deliveries (`success = True`). When HTTP 204 is received with an empty body, `response` must default to `"ok"`.
- **BR-3**: Embed colors specified as Hex strings (e.g. `"#5865F2"` or `"5865F2"`) must be converted to decimal integers (e.g. `5814783`) as required by Discord's API.
- **BR-4**: Network timeouts or unreachable host errors must be trapped gracefully without crashing the runner, outputting `success: False` and `status_code: 0`.

## 3. Acceptance Criteria (BDD)

### Happy Path (Success Scenarios)
- **AC-1: Plain Text Notification with HTTP 204 Delivery**
  - **Given** a valid Discord webhook URL and message content `"Deploy succeeded!"`
  - **When** the node executes against an endpoint returning HTTP 204 No Content
  - **Then** output `success` is `True`, `status_code` is `204`, and `response` is `"ok"`.

- **AC-2: Rich Embed Card with Hex Color Conversion**
  - **Given** message content, `embed_title="Build Notice"`, `embed_description="Pass 100%"`, and `embed_color="#00FF00"`
  - **When** the node executes
  - **Then** the dispatched JSON request payload contains an `embeds` array with decimal color `65280` (`0x00FF00`).

### Input & Validation Scenarios
- **AC-3: Missing Webhook URL or Empty Payload**
  - **Given** an empty `webhook_url` or missing message/embed fields
  - **When** the component executes
  - **Then** `success` is `False`, `status_code` is `0`, and `response` reports the missing parameter.

### Edge Cases & Exceptions (Resilience)
- **AC-4: Network Failure & Timeout Handling**
  - **Given** an unreachable host or connection timeout
  - **When** the HTTP POST encounters a network error
  - **Then** the node outputs `success: False`, `status_code: 0`, and records the error description in `response`.

- **AC-5: Variable Interpolation in Discord Message**
  - **Given** a message formatted with template variables like `"Alert for cluster {{CLUSTER_NAME}}"`
  - **When** the node executes within `FlowRunner`
  - **Then** the resolved payload dispatched to Discord contains interpolated values.

## 4. Test Data & Boundary Matrix
| Parameter / Field | Valid Inputs (Happy) | Invalid / Boundary Inputs (Edge) |
|---|---|---|
| `webhook_url` | `"https://discord.com/api/webhooks/123/abc"` | `""`, `None` |
| `content` | `"Hello Discord!"`, `"{{STATUS}} alert"` | `""` (valid if embed present), `None` |
| `embed_color` | `"#5865F2"`, `"5814783"`, `"#FF0000"` | `"invalid_color"` (falls back to default Blurple) |
| `username` | `"DeployBot"`, `"AlertBot"` | `""` (omits override) |
| `timeout` | `10`, `30` | `0`, `-1` |

## 5. Verification Sensors
| Sensor | Command / Target | Success Threshold |
|---|---|---|
| Backend Test Suite | `uv run pytest backend/tests/test_discord_notification.py` | 100% pass |
| Frontend Test Suite | `npx vitest run frontend/tests/discord_notification.test.ts` | 100% pass |
| Full Vitest Suite | `npx vitest run` | 100% pass |
| Frontend Build | `npm run build` in `frontend/` | Exit 0, 0 type errors |
| Backend Pytest Suite | `uv run pytest` in `backend/` | 100% pass |
| SDD Integrity Sensor | `node .agents/scripts/verify-sdd-integrity.js` | 100% pass |
| Spec Drift Sensor | `node .agents/scripts/check-spec-drift.js` | 100% pass |

## 6. UI & Design System Tokens
- **Icon**: `MessageCircle` from `lucide-vue-next`.
- **Theme**: Blurple / Indigo styling matching Discord branding (`text-[#828fff] bg-[#5e6ad2]/10 border-[#5e6ad2]/30`).
- **Category**: Categorized under `"Actions"`.
