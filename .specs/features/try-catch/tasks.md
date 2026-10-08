# Task List: Try / Catch Component (ADR 0031)

## Sequence Guidelines (MetaGPT SOP)
- **Strict Sequential Order**: Tasks must be executed top-to-bottom without reordering.
- **Atomic File Boundaries**: Each task modifies at most 1–3 specific target files.
- **Decoupled Test Setup**: Test tasks (`Type: test`) precede implementation tasks (`Type: feat`).
- **Sensor Evidence Gate**: Mark complete `[x]` ONLY after passing build, lint, and test sensors with recorded evidence.

## Implementation Tasks

| Status | ID | Type | Description | Target Files | Dependencies | Evidence |
|---|---|---|---|---|---|---|
| [x] | TASK-01 | test | Add backend tests for TryCatchComponent (success routing, error routing, fallback emission, FlowRunner error interception, branch skipping) | `backend/tests/test_try_catch.py` | None | Pytest 5 passed in 0.18s |
| [x] | TASK-02 | feat | Implement TryCatchComponent in logic.py, register in builtins, and enable error interception and branch handles in runner.py | `backend/src/backend/app/components/builtins/logic.py`, `backend/src/backend/app/engine/runner.py`, `backend/src/backend/app/components/builtins/__init__.py` | TASK-01 | Pytest 157 passed in 3.19s |
| [x] | TASK-03 | test | Add frontend unit tests verifying TryCatchComponent schema, ports, and palette display | `frontend/tests/try_catch.test.ts` | TASK-02 | Vitest 4 passed in 56ms |
| [x] | TASK-04 | feat | Update CustomNode and ComponentPalette with ShieldAlert icon and Rose styling for Try / Catch | `frontend/src/components/CustomNode.vue`, `frontend/src/components/ComponentPalette.vue` | TASK-03 | Vitest 133 passed, Vue build exit 0 |
| [x] | TASK-05 | review | Run full sensor verification (Pytest, Vitest, Vue build, and SDD integrity sensor) | `frontend/`, `backend/`, `.specs/` | TASK-04 | SDD Integrity 100% OK, spec drift 0 |

## Schema Dictionary
- **Status**: `[ ]` (Pending) | `[x]` (Verified Complete).
- **ID**: `TASK-01`, `TASK-02`, etc.
- **Type**: `test` | `feat` | `fix` | `refactor` | `docs` | `rules` | `skill` | `review`.
- **Target Files**: Concrete comma-separated file paths (relative to workspace root).
- **Dependencies**: Comma-separated list of preceding task IDs or `None`.
- **Evidence**: Commit hash (`git rev-parse --short HEAD`) + sensor output snippet.
