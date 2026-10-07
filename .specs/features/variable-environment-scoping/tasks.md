# Task List: Variable Environment Scoping & Selection (ADR 0015)

## Sequence Guidelines (MetaGPT SOP)
- **Strict Sequential Order**: Tasks must be executed top-to-bottom without reordering.
- **Atomic File Boundaries**: Each task modifies at most 1–3 specific target files.
- **Decoupled Test Setup**: Test tasks (`Type: test`) precede implementation tasks (`Type: feat`).
- **Sensor Evidence Gate**: Mark complete `[x]` ONLY after passing build, lint, and test sensors with recorded evidence.

## Implementation Tasks

| Status | ID | Type | Description | Target Files | Dependencies | Evidence |
|---|---|---|---|---|---|---|
| [x] | TASK-01 | test | Add backend integration tests for VariableComponent environment selection ('current', 'all', 'dev', 'qa', 'prd') | `backend/tests/test_variable_environment.py` | None | pytest 4 passed |
| [x] | TASK-02 | feat | Add environment SelectInput and resolution logic to VariableComponent | `backend/src/backend/app/components/builtins/variables.py` | TASK-01 | pytest 71 passed |
| [x] | TASK-03 | test | Add frontend unit tests verifying VariableComponent environment schema and serialization | `frontend/tests/variables_environment.test.ts` | TASK-02 | vitest 71 passed |
| [x] | TASK-04 | review | Run full sensor verification (Pytest, Vitest, Vue build, and SDD integrity sensor) | `frontend/`, `backend/`, `.specs/` | TASK-03 | Commit `b1b885d` - Pytest 71 passed, Vitest 71 passed, Vue build clean, SDD integrity 100% |

## Schema Dictionary
- **Status**: `[ ]` (Pending) | `[x]` (Verified Complete).
- **ID**: `TASK-01`, `TASK-02`, etc.
- **Type**: `test` | `feat` | `fix` | `refactor` | `docs` | `rules` | `skill` | `review`.
- **Target Files**: Concrete comma-separated file paths (relative to workspace root).
- **Dependencies**: Comma-separated list of preceding task IDs or `None`.
- **Evidence**: Commit hash (`git rev-parse --short HEAD`) + sensor output snippet.
