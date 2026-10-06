# Task List: Folders Organization & Multi-Environment Promotion Pipeline (DEV -> QA -> PRD)

## Sequence Guidelines (MetaGPT SOP)
- **Strict Sequential Order**: Tasks must be executed top-to-bottom without reordering.
- **Atomic File Boundaries**: Each task modifies at most 1–3 specific target files.
- **Decoupled Test Setup**: Test tasks (`Type: test`) precede implementation tasks (`Type: feat`).
- **Sensor Evidence Gate**: Mark complete `[x]` ONLY after passing build, lint, and test sensors with recorded evidence.

## Implementation Tasks

| Status | ID | Type | Description | Target Files | Dependencies | Evidence |
|---|---|---|---|---|---|---|
| [x] | TASK-01 | test | Define unit tests for folders, environments in flows table, and multi-environment variables resolution | `backend/tests/test_folders_and_environments.py` | None | 5 test cases defined in `test_folders_and_environments.py` covering folders, 4-tier vars, promotion, and runner env |
| [x] | TASK-02 | feat | Add folder, environment, version, and source_flow_id to DatabaseManager, and environment to variables table | `backend/src/backend/app/db.py`, `backend/src/backend/app/models/flow.py` | TASK-01 | DatabaseManager and Pydantic models updated with folder, environment, version, source_flow_id and 4-tier resolution hierarchy |
| [x] | TASK-03 | feat | Implement FlowRunner environment-aware variable resolution and promote endpoint in API routes | `backend/src/backend/app/engine/runner.py`, `backend/src/backend/app/api/routes.py` | TASK-02 | FlowRunner supports environment variable resolution; routes support /flows/{id}/promote and folder/environment query params (38/38 pytest passing) |
| [x] | TASK-04 | test | Define frontend unit tests for environment switching, folder grouping, and promotion actions | `frontend/tests/environments_and_folders.test.ts` | TASK-03 | 4 frontend tests defined covering environment switching, folder grouping, promotion API call, and env-scoped variables |
| [x] | TASK-05 | feat | Update flowStore and variablesStore to support folders, environments (DEV, QA, PRD), and promotion | `frontend/src/stores/flowStore.ts`, `frontend/src/stores/variablesStore.ts` | TASK-04 | Implemented environments, folders, promoteFlow and variable filtering; 16/16 Vitest tests passing |
| [x] | TASK-06 | feat | Implement TopNav Environment Switcher and FlowsModal folder grouping & promotion buttons | `frontend/src/components/TopNav.vue`, `frontend/src/components/FlowsModal.vue`, `frontend/src/components/VariablesModal.vue` | TASK-05 | TopNav environment switcher, folder/version badges, FlowsModal folder pills and promotion buttons, VariablesModal env badges and filters; clean vue-tsc build |
| [x] | TASK-07 | review | Run full sensor verification (Pytest, Vitest, Vue build, and SDD integrity sensor) | `backend/`, `frontend/`, `.specs/` | TASK-06 | 38/38 Pytest passing, 16/16 Vitest passing, vue-tsc build clean, and SDD integrity sensor 100% OK |

## Schema Dictionary
- **Status**: `[ ]` (Pending) | `[x]` (Verified Complete).
- **ID**: `TASK-01`, `TASK-02`, etc.
- **Type**: `test` | `feat` | `fix` | `refactor` | `docs` | `rules` | `skill` | `review`.
- **Target Files**: Concrete comma-separated file paths (relative to workspace root).
- **Dependencies**: Comma-separated list of preceding task IDs or `None`.
- **Evidence**: Commit hash (`git rev-parse --short HEAD`) + sensor output snippet.
