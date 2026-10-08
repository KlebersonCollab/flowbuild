# Task List: Showcase Workflow Templates Expansion (ADR 0032)

## Sequence Guidelines (MetaGPT SOP)
- **Strict Sequential Order**: Tasks must be executed top-to-bottom without reordering.
- **Atomic File Boundaries**: Each task modifies at most 1–3 specific target files.
- **Decoupled Test Setup**: Test tasks (`Type: test`) precede implementation tasks (`Type: feat`).
- **Sensor Evidence Gate**: Mark complete `[x]` ONLY after passing build, lint, and test sensors with recorded evidence.

## Implementation Tasks

| Status | ID | Type | Description | Target Files | Dependencies | Evidence |
|---|---|---|---|---|---|---|
| [x] | TASK-01 | test | Add frontend unit tests in showcase_templates.test.ts for database_csv_export_flow, batch_kv_discord_flow, and resilient_try_catch_telegram_flow | `frontend/tests/showcase_templates.test.ts` | None | Vitest 9 passed in 81ms |
| [x] | TASK-02 | feat | Implement 3 new showcase workflow templates in flowStore.ts with node configurations, positions, and edges | `frontend/src/stores/flowStore.ts` | TASK-01 | Vitest 9 passed |
| [x] | TASK-03 | feat | Reorganize TopNav templates dropdown menu into 4 thematic sections and wire template triggers | `frontend/src/components/TopNav.vue` | TASK-02 | Vitest 136 passed, Vue build exit 0 |
| [x] | TASK-04 | review | Run full sensor verification (Vitest, Vue build, spec drift sensor, and SDD integrity sensor) | `frontend/`, `.specs/` | TASK-03 | SDD Integrity 100% OK, spec drift 0 |

## Schema Dictionary
- **Status**: `[ ]` (Pending) | `[x]` (Verified Complete).
- **ID**: `TASK-01`, `TASK-02`, etc.
- **Type**: `test` | `feat` | `fix` | `refactor` | `docs` | `rules` | `skill` | `review`.
- **Target Files**: Concrete comma-separated file paths (relative to workspace root).
- **Dependencies**: Comma-separated list of preceding task IDs or `None`.
- **Evidence**: Commit hash (`git rev-parse --short HEAD`) + sensor output snippet.
