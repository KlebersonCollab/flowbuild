# Task List: Variables System & Agnostic Persistence

## Sequence Guidelines (MetaGPT SOP)
- **Strict Sequential Order**: Tasks must be executed top-to-bottom without reordering.
- **Atomic File Boundaries**: Each task modifies at most 1–3 specific target files.
- **Decoupled Test Setup**: Test tasks (`Type: test`) precede implementation tasks (`Type: feat`).
- **Sensor Evidence Gate**: Mark complete `[x]` ONLY after passing build, lint, and test sensors with recorded evidence.

## Implementation Tasks

| Status | ID | Type | Description | Target Files | Dependencies | Evidence |
|---|---|---|---|---|---|---|
| [x] | TASK-01 | test | Define unit test suite for SQLAlchemy database abstraction and variables repository | `backend/tests/test_variables_and_db.py` | None | 17e7ca0 (25 passed in 0.85s) |
| [x] | TASK-02 | feat | Refactor DatabaseManager to SQLAlchemy supporting SQLite/PostgreSQL and implement variables table | `backend/src/backend/app/db.py`, `backend/src/backend/app/models/flow.py` | TASK-01 | 17e7ca0 (SQLAlchemy 2.0 Engine & variables_table passing) |
| [x] | TASK-03 | test | Define unit tests for VariableComponent, hierarchy resolution, and template interpolation | `backend/tests/test_variable_interpolation.py` | TASK-02 | 17e7ca0 (4 tests passed in 0.47s) |
| [x] | TASK-04 | feat | Implement VariableComponent and {{VAR}} string interpolation in FlowRunner | `backend/src/backend/app/components/builtins/variables.py`, `backend/src/backend/app/engine/runner.py` | TASK-03 | 17e7ca0 (VariableComponent & FlowRunner interpolation passing 29/29) |
| [x] | TASK-05 | feat | Implement Variables CRUD endpoints (GET, POST, PUT, DELETE /api/v1/variables) | `backend/src/backend/app/api/routes.py` | TASK-04 | 17e7ca0 (Variables CRUD endpoints verified in test_api.py, 30/30 passed) |
| [x] | TASK-06 | test | Define frontend tests for variables store and node position auto-save | `frontend/tests/variables.test.ts` | TASK-05 | 17e7ca0 (Vitest variables.test.ts 4/4 passed) |
| [x] | TASK-07 | feat | Implement variablesStore and VariablesModal UI with global/flow tabs | `frontend/src/stores/variablesStore.ts`, `frontend/src/components/VariablesModal.vue`, `frontend/src/components/TopNav.vue` | TASK-06 | 17e7ca0 (VariablesModal UI & variablesStore complete) |
| [x] | TASK-08 | feat | Implement canvas node drag auto-persistence on drag stop with debounced backend sync | `frontend/src/components/FlowCanvas.vue`, `frontend/src/stores/flowStore.ts` | TASK-07 | 17e7ca0 (onNodeDragStop with 600ms debounce persistence) |
| [x] | TASK-09 | review | Run full sensor verification (Pytest, Vitest, Vue build, and SDD integrity sensor) | `backend/`, `frontend/`, `.specs/` | TASK-08 | 17e7ca0 (Pytest 30/30, Vitest 11/11, vue-tsc & vite build OK, SDD OK) |

## Schema Dictionary
- **Status**: `[ ]` (Pending) | `[x]` (Verified Complete).
- **ID**: `TASK-01`, `TASK-02`, etc.
- **Type**: `test` | `feat` | `fix` | `refactor` | `docs` | `rules` | `skill` | `review`.
- **Target Files**: Concrete comma-separated file paths (relative to workspace root).
- **Dependencies**: Comma-separated list of preceding task IDs or `None`.
- **Evidence**: Commit hash (`git rev-parse --short HEAD`) + sensor output snippet.
