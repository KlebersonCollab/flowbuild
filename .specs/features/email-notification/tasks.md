# Task List: Email Notification Component (ADR 0024)

## Sequence Guidelines (MetaGPT SOP)
- **Strict Sequential Order**: Tasks must be executed top-to-bottom without reordering.
- **Atomic File Boundaries**: Each task modifies at most 1–3 specific target files.
- **Decoupled Test Setup**: Test tasks (`Type: test`) precede implementation tasks (`Type: feat`).
- **Sensor Evidence Gate**: Mark complete `[x]` ONLY after passing build, lint, and test sensors with recorded evidence.

## Implementation Tasks

| Status | ID | Type | Description | Target Files | Dependencies | Evidence |
|---|---|---|---|---|---|---|
| [x] | TASK-01 | test | Add backend integration tests for EmailNotificationComponent (STARTTLS, SSL, multi-recipients, auth failure, connection error, FlowRunner variable interpolation) | `backend/tests/test_email_notification.py` | None | pytest 6 passed in tests/test_email_notification.py |
| [x] | TASK-02 | feat | Implement EmailNotificationComponent using async smtplib thread worker and register in builtins | `backend/src/backend/app/components/builtins/actions.py`, `backend/src/backend/app/components/builtins/__init__.py` | TASK-01 | pytest 114 passed in backend/ (6/6 Email tests passing, 0 regressions) |
| [x] | TASK-03 | test | Add frontend unit tests verifying EmailNotificationComponent schema, ports, and palette display | `frontend/tests/email_notification.test.ts` | TASK-02 | vitest 4 passed in tests/email_notification.test.ts |
| [x] | TASK-04 | feat | Update CustomNode and ComponentPalette with Mail icon and Violet styling for Email | `frontend/src/components/CustomNode.vue`, `frontend/src/components/ComponentPalette.vue` | TASK-03 | vitest 105 passed, vue build passed, Mail icon & Violet styling applied |
| [x] | TASK-05 | review | Run full sensor verification (Pytest, Vitest, Vue build, and SDD integrity sensor) | `frontend/`, `backend/`, `.specs/` | TASK-04 | Commit 74f6a8b, pytest 114 passed, vitest 105 passed, vue build passed, verify-sdd-integrity passed |

## Schema Dictionary
- **Status**: `[ ]` (Pending) | `[x]` (Verified Complete).
- **ID**: `TASK-01`, `TASK-02`, etc.
- **Type**: `test` | `feat` | `fix` | `refactor` | `docs` | `rules` | `skill` | `review`.
- **Target Files**: Concrete comma-separated file paths (relative to workspace root).
- **Dependencies**: Comma-separated list of preceding task IDs or `None`.
- **Evidence**: Commit hash (`git rev-parse --short HEAD`) + sensor output snippet.
