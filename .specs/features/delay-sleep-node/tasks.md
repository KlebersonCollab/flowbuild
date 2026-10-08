# Task List: Delay / Sleep Node Component (ADR 0017)

## Sequence Guidelines (MetaGPT SOP)
- **Strict Sequential Order**: Tasks must be executed top-to-bottom without reordering.
- **Atomic File Boundaries**: Each task modifies at most 1–3 specific target files.
- **Decoupled Test Setup**: Test tasks (`Type: test`) precede implementation tasks (`Type: feat`).
- **Sensor Evidence Gate**: Mark complete `[x]` ONLY after passing build, lint, and test sensors with recorded evidence.

## Implementation Tasks

| Status | ID | Type | Description | Target Files | Dependencies | Evidence |
|---|---|---|---|---|---|---|
| [x] | TASK-01 | test | Add backend integration tests for DelayComponent (seconds, ms, minutes, zero/negative, data pass-through, and template interpolation) | `backend/tests/test_delay_component.py` | None | Baseline test suite created (6 tests captured, awaiting TASK-02 implementation) |
| [x] | TASK-02 | feat | Implement DelayComponent with non-blocking asyncio.sleep and transparent payload pass-through | `backend/src/backend/app/components/builtins/logic.py`, `backend/src/backend/app/components/builtins/__init__.py` | TASK-01 | pytest 77 passed (6/6 DelayComponent tests passing) |
| [x] | TASK-03 | test | Add frontend unit tests verifying DelayComponent schema, palette inclusion, and numeric input rendering | `frontend/tests/delay_component.test.ts` | TASK-02 | vitest 4 passed in tests/delay_component.test.ts |
| [x] | TASK-04 | feat | Update CustomNode and ComponentPalette with Clock icon, Amber/Orange badges, and quick inline number input controls | `frontend/src/components/CustomNode.vue`, `frontend/src/components/ComponentPalette.vue` | TASK-03 | vitest 75 passed, vue-tsc and vite build clean |
| [x] | TASK-05 | review | Run full sensor verification (Pytest, Vitest, Vue build, and SDD integrity sensor) | `frontend/`, `backend/`, `.specs/` | TASK-04 | Commit `c4fb065` - Pytest 77 passed, Vitest 75 passed, Vue build clean, SDD integrity 100%, Spec drift OK |

## Schema Dictionary
- **Status**: `[ ]` (Pending) | `[x]` (Verified Complete).
- **ID**: `TASK-01`, `TASK-02`, etc.
- **Type**: `test` | `feat` | `fix` | `refactor` | `docs` | `rules` | `skill` | `review`.
- **Target Files**: Concrete comma-separated file paths (relative to workspace root).
- **Dependencies**: Comma-separated list of preceding task IDs or `None`.
- **Evidence**: Commit hash (`git rev-parse --short HEAD`) + sensor output snippet.
