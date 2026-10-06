# Task List: Automation Engine Suite

## Sequence Guidelines (MetaGPT SOP)
- **Strict Sequential Order**: Tasks must be executed top-to-bottom without reordering.
- **Atomic File Boundaries**: Each task modifies at most 1–3 specific target files.
- **Decoupled Test Setup**: Test tasks (`Type: test`) precede implementation tasks (`Type: feat`).
- **Sensor Evidence Gate**: Mark complete `[x]` ONLY after passing build, lint, and test sensors with recorded evidence.

## Implementation Tasks

| Status | ID | Type | Description | Target Files | Dependencies | Evidence |
|---|---|---|---|---|---|---|
| [x] | TASK-01 | test | Define unit test suite for SQLite persistence, Flow CRUD, and execution history database | `backend/tests/test_persistence.py` | None | `9e9aa81` 2/2 persistence tests passing |
| [x] | TASK-02 | feat | Implement SQLite database repository with WAL mode for flows and execution records | `backend/src/backend/app/db.py`, `backend/src/backend/app/models.py` | TASK-01 | `9e9aa81` DatabaseManager WAL mode verified |
| [x] | TASK-03 | test | Define unit test suite for HTTP Auth, IfConditionComponent, and CronTriggerComponent | `backend/tests/test_advanced_components.py` | TASK-02 | `803c407` 4/4 advanced component tests passing |
| [x] | TASK-04 | feat | Implement enhanced HttpRequestComponent (Bearer, Basic, API Key) and IfConditionComponent | `backend/src/backend/app/components/builtins/actions.py`, `backend/src/backend/app/components/builtins/logic.py` | TASK-03 | `803c407` HTTP Auth + Logic branching passing |
| [x] | TASK-05 | feat | Implement CronTriggerComponent and background asyncio cron scheduler service | `backend/src/backend/app/components/builtins/triggers.py`, `backend/src/backend/app/engine/scheduler.py` | TASK-04 | `b3fbe9b` CronTrigger + CronSchedulerService pass |
| [x] | TASK-06 | test | Define unit tests for Webhook routing, Flow CRUD API, and Freeze vs Unfreeze retry engine | `backend/tests/test_flow_crud_and_retry.py` | TASK-05 | `b3fbe9b` 3/3 Webhook & Retry tests passing |
| [x] | TASK-07 | feat | Implement Webhook router, Flow CRUD endpoints, and Freeze/Unfreeze execution retry engine | `backend/src/backend/app/api/routes.py`, `backend/src/backend/app/engine/runner.py` | TASK-06 | `b3fbe9b` Webhooks, CRUD and Replay engine pass |
| [x] | TASK-08 | test | Define frontend tests for flow management store and execution retry actions | `frontend/tests/automation.test.ts` | TASK-07 | `432e1aa` 2/2 automation store tests passing |
| [x] | TASK-09 | feat | Implement FlowsModal for Flow CRUD/activation and add Execution History with Freeze/Unfreeze retry to ExecutionDrawer | `frontend/src/components/FlowsModal.vue`, `frontend/src/components/ExecutionDrawer.vue`, `frontend/src/components/TopNav.vue` | TASK-08 | `432e1aa` FlowsModal & History drawer pass |
| [x] | TASK-10 | review | Run full sensor verification (Pytest, Vitest, Vue build, and SDD integrity sensor) | `backend/`, `frontend/`, `.specs/` | TASK-09 | 24/24 pytest pass, 7/7 vitest pass, vue-tsc pass, integrity ok |

## Schema Dictionary
- **Status**: `[ ]` (Pending) | `[x]` (Verified Complete).
- **ID**: `TASK-01`, `TASK-02`, etc.
- **Type**: `test` | `feat` | `fix` | `refactor` | `docs` | `rules` | `skill` | `review`.
- **Target Files**: Concrete comma-separated file paths (relative to workspace root).
- **Dependencies**: Comma-separated list of preceding task IDs or `None`.
- **Evidence**: Commit hash (`git rev-parse --short HEAD`) + sensor output snippet.
