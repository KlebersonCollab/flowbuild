# Task List: Responsive Flows Manager Viewport & Grid Layout

## Sequence Guidelines (MetaGPT SOP)
- **Strict Sequential Order**: Tasks must be executed top-to-bottom without reordering.
- **Atomic File Boundaries**: Each task modifies at most 1–3 specific target files.
- **Decoupled Test Setup**: Test tasks (`Type: test`) precede implementation tasks (`Type: feat`).
- **Sensor Evidence Gate**: Mark complete `[x]` ONLY after passing build, lint, and test sensors with recorded evidence.

## Implementation Tasks

| Status | ID | Type | Description | Target Files | Dependencies | Evidence |
|---|---|---|---|---|---|---|
| [x] | TASK-01 | test | Add unit tests for maximize mode, collapsible sidebar, and list/grid view switching in FlowsModal | `frontend/tests/flows_modal_responsive.test.ts` | None | `eeeab4a` + `vitest tests/flows_modal_responsive.test.ts 3 passed` |
| [x] | TASK-02 | feat | Implement dynamic fluid sizing, maximize toggle, collapsible sidebar, and view mode switcher in FlowsModal.vue | `frontend/src/components/FlowsModal.vue` | TASK-01 | `eeeab4a` + `FlowsModal.vue fluid sizing, maximize toggle, sidebar collapse & viewMode switcher implemented` |
| [x] | TASK-03 | review | Run full sensor verification (Pytest, Vitest, Vue build, and SDD integrity sensor) | `frontend/`, `backend/`, `.specs/` | TASK-02 | `eeeab4a` + `62 pytest passed, 63 vitest passed, vue build clean, sdd sensor OK` |

## Schema Dictionary
- **Status**: `[ ]` (Pending) | `[x]` (Verified Complete).
- **ID**: `TASK-01`, `TASK-02`, etc.
- **Type**: `test` | `feat` | `fix` | `refactor` | `docs` | `rules` | `skill` | `review`.
- **Target Files**: Concrete comma-separated file paths (relative to workspace root).
- **Dependencies**: Comma-separated list of preceding task IDs or `None`.
- **Evidence**: Commit hash (`git rev-parse --short HEAD`) + sensor output snippet.
