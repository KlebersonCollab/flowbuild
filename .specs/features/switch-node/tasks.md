# Task List: Switch / Router Node Component (ADR 0018)

## Sequence Guidelines (MetaGPT SOP)
- **Strict Sequential Order**: Tasks must be executed top-to-bottom without reordering.
- **Atomic File Boundaries**: Each task modifies at most 1–3 specific target files.
- **Decoupled Test Setup**: Test tasks (`Type: test`) precede implementation tasks (`Type: feat`).
- **Sensor Evidence Gate**: Mark complete `[x]` ONLY after passing build, lint, and test sensors with recorded evidence.

## Implementation Tasks

| Status | ID | Type | Description | Target Files | Dependencies | Evidence |
|---|---|---|---|---|---|---|
| [x] | TASK-01 | test | Add backend integration tests for SwitchNodeComponent and FlowRunner multi-branch skipping | `backend/tests/test_switch_node.py` | None | Baseline test suite created (5 tests captured, awaiting TASK-02 implementation) |
| [x] | TASK-02 | feat | Implement SwitchNodeComponent and expand FlowRunner conditional handle skipping | `backend/src/backend/app/components/builtins/logic.py`, `backend/src/backend/app/components/builtins/__init__.py`, `backend/src/backend/app/engine/runner.py` | TASK-01 | pytest 82 passed (5/5 SwitchNode tests passing, 0 regressions) |
| [x] | TASK-03 | test | Add frontend unit tests verifying SwitchNodeComponent schema, ports, and palette display | `frontend/tests/switch_node.test.ts` | TASK-02 | vitest 4 passed in tests/switch_node.test.ts |
| [x] | TASK-04 | feat | Update CustomNode and ComponentPalette with GitFork icon and Indigo styling for Switch / Router | `frontend/src/components/CustomNode.vue`, `frontend/src/components/ComponentPalette.vue` | TASK-03 | vitest 79 passed, vue-tsc & vite build clean |
| [x] | TASK-05 | review | Run full sensor verification (Pytest, Vitest, Vue build, and SDD integrity sensor) | `frontend/`, `backend/`, `.specs/` | TASK-04 | Commit `677ba0b` - Pytest 82 passed, Vitest 79 passed, Vue build clean, SDD integrity 100%, Spec drift OK |

## Schema Dictionary
- **Status**: `[ ]` (Pending) | `[x]` (Verified Complete).
- **ID**: `TASK-01`, `TASK-02`, etc.
- **Type**: `test` | `feat` | `fix` | `refactor` | `docs` | `rules` | `skill` | `review`.
- **Target Files**: Concrete comma-separated file paths (relative to workspace root).
- **Dependencies**: Comma-separated list of preceding task IDs or `None`.
- **Evidence**: Commit hash (`git rev-parse --short HEAD`) + sensor output snippet.
