# Task List: Variable Get/Set Mode Selection and Execution Persistence

## Sequence Guidelines (MetaGPT SOP)
- **Strict Sequential Order**: Tasks must be executed top-to-bottom without reordering.
- **Atomic File Boundaries**: Each task modifies at most 1–3 specific target files.
- **Decoupled Test Setup**: Test tasks (`Type: test`) precede implementation tasks (`Type: feat`).
- **Sensor Evidence Gate**: Mark complete `[x]` ONLY after passing build, lint, and test sensors with recorded evidence.

## Implementation Tasks

| Status | ID | Type | Description | Target Files | Dependencies | Evidence |
|---|---|---|---|---|---|---|
| [x] | TASK-01 | test | Add backend integration tests for VariableComponent in get and set modes, persistence, and downstream propagation in FlowRunner | `backend/tests/test_variable_get_set.py` | None | pytest 5 passed |
| [x] | TASK-02 | feat | Implement upsert_variable method in DatabaseManager | `backend/src/backend/app/db.py` | TASK-01 | pytest test_variables_and_db + test_variable_get_set passed |
| [x] | TASK-03 | feat | Update VariableComponent with mode (get/set), scope, persist, and dynamic execution behavior | `backend/src/backend/app/components/builtins/variables.py` | TASK-02 | pytest 67 passed |
| [x] | TASK-04 | feat | Update FlowRunner to propagate variables set at runtime to self.custom_variables and downstream nodes | `backend/src/backend/app/engine/runner.py` | TASK-03 | pytest test_flow_runner_propagates_set_variable_downstream passed |
| [x] | TASK-05 | test | Add frontend unit tests for VariableComponent get/set schema and execution verification | `frontend/tests/variables_get_set.test.ts`, `frontend/src/components/CustomNode.vue` | TASK-04 | vitest 68 passed |
| [x] | TASK-06 | review | Run full sensor verification (Pytest, Vitest, Vue build, and SDD integrity sensor) | `frontend/`, `backend/`, `.specs/` | TASK-05 | All sensors passed (pytest: 67 passed, vitest: 68 passed, vue-tsc & vite build: exit 0, sdd integrity: 100%) |

## Schema Dictionary
- **Status**: `[ ]` (Pending) | `[x]` (Verified Complete).
- **ID**: `TASK-01`, `TASK-02`, etc.
- **Type**: `test` | `feat` | `fix` | `refactor` | `docs` | `rules` | `skill` | `review`.
- **Target Files**: Concrete comma-separated file paths (relative to workspace root).
- **Dependencies**: Comma-separated list of preceding task IDs or `None`.
- **Evidence**: Commit hash (`git rev-parse --short HEAD`) + sensor output snippet.
