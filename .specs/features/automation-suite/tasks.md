# Task List: Automation Engine Suite

## Sequence Guidelines (MetaGPT SOP)
- **Strict Sequential Order**: Tasks must be executed top-to-bottom without reordering.
- **Atomic File Boundaries**: Each task modifies at most 1–3 specific target files.
- **Decoupled Test Setup**: Test tasks (`Type: test`) precede implementation tasks (`Type: feat`).
- **Sensor Evidence Gate**: Mark complete `[x]` ONLY after passing build, lint, and test sensors with recorded evidence.

## Implementation Tasks

| Status | ID | Type | Description | Target Files | Dependencies | Evidence |
|---|---|---|---|---|---|---|
| [ ] | TASK-01 | test | Define unit test suite for SQLite persistence, Flow CRUD, and execution history database | `backend/tests/test_persistence.py` | None | Pending execution |
| [ ] | TASK-02 | feat | Implement SQLite database repository with WAL mode for flows and execution records | `backend/src/backend/app/db.py`, `backend/src/backend/app/models.py` | TASK-01 | Pending execution |
| [ ] | TASK-03 | test | Define unit test suite for HTTP Auth, IfConditionComponent, and CronTriggerComponent | `backend/tests/test_advanced_components.py` | TASK-02 | Pending execution |
| [ ] | TASK-04 | feat | Implement enhanced HttpRequestComponent (Bearer, Basic, API Key) and IfConditionComponent | `backend/src/backend/components/actions.py`, `backend/src/backend/components/logic.py` | TASK-03 | Pending execution |
| [ ] | TASK-05 | feat | Implement CronTriggerComponent and background asyncio cron scheduler service | `backend/src/backend/components/triggers.py`, `backend/src/backend/engine/scheduler.py` | TASK-04 | Pending execution |
| [ ] | TASK-06 | test | Define unit tests for Webhook routing, Flow CRUD API, and Freeze vs Unfreeze retry engine | `backend/tests/test_flow_crud_and_retry.py` | TASK-05 | Pending execution |
| [ ] | TASK-07 | feat | Implement Webhook router, Flow CRUD endpoints, and Freeze/Unfreeze execution retry engine | `backend/src/backend/app/api/routes.py`, `backend/src/backend/engine/runner.py` | TASK-06 | Pending execution |
| [ ] | TASK-08 | test | Define frontend tests for flow management store and execution retry actions | `frontend/tests/automation.test.ts` | TASK-07 | Pending execution |
| [ ] | TASK-09 | feat | Implement FlowsModal for Flow CRUD/activation and add Execution History with Freeze/Unfreeze retry to ExecutionDrawer | `frontend/src/components/FlowsModal.vue`, `frontend/src/components/ExecutionDrawer.vue`, `frontend/src/components/TopNav.vue` | TASK-08 | Pending execution |
| [ ] | TASK-10 | review | Run full sensor verification (Pytest, Vitest, Vue build, and SDD integrity sensor) | `backend/`, `frontend/`, `.specs/` | TASK-09 | Pending execution |

## Schema Dictionary
- **Status**: `[ ]` (Pending) | `[x]` (Verified Complete).
- **ID**: `TASK-01`, `TASK-02`, etc.
- **Type**: `test` | `feat` | `fix` | `refactor` | `docs` | `rules` | `skill` | `review`.
- **Target Files**: Concrete comma-separated file paths (relative to workspace root).
- **Dependencies**: Comma-separated list of preceding task IDs or `None`.
- **Evidence**: Commit hash (`git rev-parse --short HEAD`) + sensor output snippet.
