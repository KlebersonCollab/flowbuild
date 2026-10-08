# Task List: Data Filter Component (ADR 0019)

## Sequence Guidelines (MetaGPT SOP)
- **Strict Sequential Order**: Tasks must be executed top-to-bottom without reordering.
- **Atomic File Boundaries**: Each task modifies at most 1–3 specific target files.
- **Decoupled Test Setup**: Test tasks (`Type: test`) precede implementation tasks (`Type: feat`).
- **Sensor Evidence Gate**: Mark complete `[x]` ONLY after passing build, lint, and test sensors with recorded evidence.

## Implementation Tasks

| Status | ID | Type | Description | Target Files | Dependencies | Evidence |
|---|---|---|---|---|---|---|
| [x] | TASK-01 | test | Add backend integration tests for DataFilterComponent (operators, items_path extraction, custom expressions, and FlowRunner pipeline) | `backend/tests/test_data_filter.py` | None | Baseline test suite created (6 tests captured, awaiting TASK-02 implementation) |
| [x] | TASK-02 | feat | Implement DataFilterComponent with declarative comparison operators and item extraction | `backend/src/backend/app/components/builtins/actions.py`, `backend/src/backend/app/components/builtins/__init__.py` | TASK-01 | pytest 88 passed (6/6 DataFilter tests passing, 0 regressions) |
| [x] | TASK-03 | test | Add frontend unit tests verifying DataFilterComponent schema, ports, and palette display | `frontend/tests/data_filter.test.ts` | TASK-02 | vitest 4 passed in tests/data_filter.test.ts |
| [x] | TASK-04 | feat | Update CustomNode and ComponentPalette with Filter icon and Emerald styling for Data Filter | `frontend/src/components/CustomNode.vue`, `frontend/src/components/ComponentPalette.vue` | TASK-03 | vitest 83 passed, vue build passed, Filter icon & emerald styling applied |
| [x] | TASK-05 | review | Run full sensor verification (Pytest, Vitest, Vue build, and SDD integrity sensor) | `frontend/`, `backend/`, `.specs/` | TASK-04 | pytest 88 passed, vitest 83 passed, vue build passed, verify-sdd-integrity passed |

## Schema Dictionary
- **Status**: `[ ]` (Pending) | `[x]` (Verified Complete).
- **ID**: `TASK-01`, `TASK-02`, etc.
- **Type**: `test` | `feat` | `fix` | `refactor` | `docs` | `rules` | `skill` | `review`.
- **Target Files**: Concrete comma-separated file paths (relative to workspace root).
- **Dependencies**: Comma-separated list of preceding task IDs or `None`.
- **Evidence**: Commit hash (`git rev-parse --short HEAD`) + sensor output snippet.
