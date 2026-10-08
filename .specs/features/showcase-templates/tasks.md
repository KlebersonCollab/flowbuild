# Task List: Showcase Workflow Templates (ADR 0021)

## Sequence Guidelines (MetaGPT SOP)
- **Strict Sequential Order**: Tasks must be executed top-to-bottom without reordering.
- **Atomic File Boundaries**: Each task modifies at most 1–3 specific target files.
- **Decoupled Test Setup**: Test tasks (`Type: test`) precede implementation tasks (`Type: feat`).
- **Sensor Evidence Gate**: Mark complete `[x]` ONLY after passing build, lint, and test sensors with recorded evidence.

## Implementation Tasks

| Status | ID | Type | Description | Target Files | Dependencies | Evidence |
|---|---|---|---|---|---|---|
| [x] | TASK-01 | test | Add frontend unit tests verifying all 9 templates in flowStore and template loading | `frontend/tests/showcase_templates.test.ts` | None | vitest 6 passed in tests/showcase_templates.test.ts |
| [x] | TASK-02 | feat | Implement 4 new showcase templates (switch_router, data_filter_alert, delay_polling, etl_pagination_filter) in flowStore.ts | `frontend/src/stores/flowStore.ts` | TASK-01 | vitest 93 passed (all 9 templates loading nodes and valid edges) |
| [x] | TASK-03 | feat | Upgrade TopNav.vue templates dropdown with categorized semantic sections and Linear dark badges | `frontend/src/components/TopNav.vue` | TASK-02 | vue build passed, categorized dropdown with 3 sections rendered |
| [x] | TASK-04 | review | Run full sensor verification (Pytest, Vitest, Vue build, and SDD integrity sensor) | `frontend/`, `backend/`, `.specs/` | TASK-03 | pytest 94 passed, vitest 93 passed, vue build passed, verify-sdd-integrity passed |

## Schema Dictionary
- **Status**: `[ ]` (Pending) | `[x]` (Verified Complete).
- **ID**: `TASK-01`, `TASK-02`, etc.
- **Type**: `test` | `feat` | `fix` | `refactor` | `docs` | `rules` | `skill` | `review`.
- **Target Files**: Concrete comma-separated file paths (relative to workspace root).
- **Dependencies**: Comma-separated list of preceding task IDs or `None`.
- **Evidence**: Commit hash (`git rev-parse --short HEAD`) + sensor output snippet.
