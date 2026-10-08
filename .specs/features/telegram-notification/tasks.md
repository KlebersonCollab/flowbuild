# Task List: Telegram Notification Component (ADR 0023)

## Sequence Guidelines (MetaGPT SOP)
- **Strict Sequential Order**: Tasks must be executed top-to-bottom without reordering.
- **Atomic File Boundaries**: Each task modifies at most 1–3 specific target files.
- **Decoupled Test Setup**: Test tasks (`Type: test`) precede implementation tasks (`Type: feat`).
- **Sensor Evidence Gate**: Mark complete `[x]` ONLY after passing build, lint, and test sensors with recorded evidence.

## Implementation Tasks

| Status | ID | Type | Description | Target Files | Dependencies | Evidence |
|---|---|---|---|---|---|---|
| [ ] | TASK-01 | test | Add backend integration tests for TelegramWebhookComponent (successful delivery, message_id extraction, silent mode, API error response, network error, and FlowRunner variable interpolation) | `backend/tests/test_telegram_notification.py` | None | Pending execution |
| [ ] | TASK-02 | feat | Implement TelegramWebhookComponent with Bot API POST formatting, parameter options, and register in builtins | `backend/src/backend/app/components/builtins/actions.py`, `backend/src/backend/app/components/builtins/__init__.py` | TASK-01 | Pending execution |
| [ ] | TASK-03 | test | Add frontend unit tests verifying TelegramWebhookComponent schema, ports, and palette display | `frontend/tests/telegram_notification.test.ts` | TASK-02 | Pending execution |
| [ ] | TASK-04 | feat | Update CustomNode and ComponentPalette with Send icon and Sky styling for Telegram | `frontend/src/components/CustomNode.vue`, `frontend/src/components/ComponentPalette.vue` | TASK-03 | Pending execution |
| [ ] | TASK-05 | review | Run full sensor verification (Pytest, Vitest, Vue build, and SDD integrity sensor) | `frontend/`, `backend/`, `.specs/` | TASK-04 | Pending execution |

## Schema Dictionary
- **Status**: `[ ]` (Pending) | `[x]` (Verified Complete).
- **ID**: `TASK-01`, `TASK-02`, etc.
- **Type**: `test` | `feat` | `fix` | `refactor` | `docs` | `rules` | `skill` | `review`.
- **Target Files**: Concrete comma-separated file paths (relative to workspace root).
- **Dependencies**: Comma-separated list of preceding task IDs or `None`.
- **Evidence**: Commit hash (`git rev-parse --short HEAD`) + sensor output snippet.
