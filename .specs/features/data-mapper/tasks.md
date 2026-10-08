# Task List: Data Mapper Component (ADR 0025)

## Sequence Guidelines (MetaGPT SOP)
- **Strict Sequential Order**: Tasks must be executed top-to-bottom without reordering.
- **Atomic File Boundaries**: Each task modifies at most 1–3 specific target files.
- **Decoupled Test Setup**: Test tasks (`Type: test`) precede implementation tasks (`Type: feat`).
- **Sensor Evidence Gate**: Mark complete `[x]` ONLY after passing build, lint, and test sensors with recorded evidence.

## Implementation Tasks

| Status | ID | Type | Description | Target Files | Dependencies | Evidence |
|---|---|---|---|---|---|---|
| [x] | TASK-01 | test | Add backend integration tests for DataMapperComponent (single object, array of items, items_path, pass_unmapped, missing keys, and FlowRunner) | `backend/tests/test_data_mapper.py` | None | pytest 6 passed in tests/test_data_mapper.py |
| [x] | TASK-02 | feat | Implement DataMapperComponent with recursive path resolver and collection handling in actions.py | `backend/src/backend/app/components/builtins/actions.py`, `backend/src/backend/app/components/builtins/__init__.py` | TASK-01 | pytest 120 passed in backend/ (6/6 DataMapper tests passing, 0 regressions) |
| [x] | TASK-03 | test | Add frontend unit tests verifying DataMapperComponent schema, ports, and palette display | `frontend/tests/data_mapper.test.ts` | TASK-02 | vitest 4 passed in tests/data_mapper.test.ts |
| [x] | TASK-04 | feat | Update CustomNode and ComponentPalette with ArrowRightLeft icon and Emerald styling for Data Mapper | `frontend/src/components/CustomNode.vue`, `frontend/src/components/ComponentPalette.vue` | TASK-03 | vitest 109 passed, vue build passed, ArrowRightLeft icon & Emerald styling applied |
| [x] | TASK-05 | review | Run full sensor verification (Pytest, Vitest, Vue build, and SDD integrity sensor) | `frontend/`, `backend/`, `.specs/` | TASK-04 | Commit 4a2e7bd, pytest 120 passed, vitest 109 passed, vue build passed, verify-sdd-integrity passed |

## Schema Dictionary
- **Status**: `[ ]` (Pending) | `[x]` (Verified Complete).
- **ID**: `TASK-01`, `TASK-02`, etc.
- **Type**: `test` | `feat` | `fix` | `refactor` | `docs` | `rules` | `skill` | `review`.
- **Target Files**: Concrete comma-separated file paths (relative to workspace root).
- **Dependencies**: Comma-separated list of preceding task IDs or `None`.
- **Evidence**: Commit hash (`git rev-parse --short HEAD`) + sensor output snippet.
