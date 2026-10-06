# Task List: Mandatory Trigger Node Requirement for Workflow Execution

## Sequence Guidelines (MetaGPT SOP)
- **Strict Sequential Order**: Tasks must be executed top-to-bottom without reordering.
- **Atomic File Boundaries**: Each task modifies at most 1–3 specific target files.
- **Decoupled Test Setup**: Test tasks (`Type: test`) precede implementation tasks (`Type: feat`).
- **Sensor Evidence Gate**: Mark complete `[x]` ONLY after passing build, lint, and test sensors with recorded evidence.

## Implementation Tasks

| Status | ID | Type | Description | Target Files | Dependencies | Evidence |
|---|---|---|---|---|---|---|
| [x] | TASK-01 | test | Add backend unit test verifying trigger requirement guard in FlowRunner and stream execution | `backend/tests/test_trigger_requirement.py` | None | [test_trigger_requirement.py] 3 test cases added covering no-trigger failure, with-trigger success, and stream api block |
| [x] | TASK-02 | feat | Implement trigger validation check in FlowRunner and API streaming endpoint | `backend/src/backend/app/engine/runner.py`, `backend/src/backend/app/api/routes.py` | TASK-01 | [FlowRunner & routes.py] require_trigger flag, has_trigger_node(), and fail-fast stream guard (43/43 pytest passing) |
| [x] | TASK-03 | test | Add frontend unit test verifying execution block when canvas lacks a trigger node | `frontend/tests/trigger_requirement.test.ts` | TASK-02 | [trigger_requirement.test.ts] 3 vitest cases covering empty/action-only block, trigger pass, and pre-configured templates |
| [x] | TASK-04 | feat | Implement trigger detection helper and TopNav execution guard with UI feedback | `frontend/src/stores/flowStore.ts`, `frontend/src/components/TopNav.vue` | TASK-03 | [flowStore & TopNav] hasTriggerNode, validateExecutionPreconditions, execution drawer warning log, and button title |
| [x] | TASK-05 | review | Run full sensor verification (Pytest, Vitest, Vue build, and SDD integrity sensor) | `backend/`, `frontend/`, `.specs/` | TASK-04 | 43/43 Pytest passing, 24/24 Vitest passing, clean vue-tsc build in 478ms, SDD sensor 100% OK |

## Schema Dictionary
- **Status**: `[ ]` (Pending) | `[x]` (Verified Complete).
- **ID**: `TASK-01`, `TASK-02`, etc.
- **Type**: `test` | `feat` | `fix` | `refactor` | `docs` | `rules` | `skill` | `review`.
- **Target Files**: Concrete comma-separated file paths (relative to workspace root).
- **Dependencies**: Comma-separated list of preceding task IDs or `None`.
- **Evidence**: Commit hash (`git rev-parse --short HEAD`) + sensor output snippet.
