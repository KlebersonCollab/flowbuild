# Task List: 100% Reactivity Auto-Save, Draft Lifecycle, Version Incrementing, and Cross-Environment Lineage Synchronization

## Sequence Guidelines (MetaGPT SOP)
- **Strict Sequential Order**: Tasks must be executed top-to-bottom without reordering.
- **Atomic File Boundaries**: Each task modifies at most 1–3 specific target files.
- **Decoupled Test Setup**: Test tasks (`Type: test`) precede implementation tasks (`Type: feat`).
- **Sensor Evidence Gate**: Mark complete `[x]` ONLY after passing build, lint, and test sensors with recorded evidence.

## Implementation Tasks

| Status | ID | Type | Description | Target Files | Dependencies | Evidence |
|---|---|---|---|---|---|---|
| [ ] | TASK-01 | test | Define unit tests for is_draft column, draft lifecycle in flows table, and lineage deduplication | `backend/tests/test_draft_and_lineage.py` | None | Pending execution |
| [ ] | TASK-02 | feat | Add is_draft column to DatabaseManager and FlowModel/FlowRecord with soft migration | `backend/src/backend/app/db.py`, `backend/src/backend/app/models/flow.py` | TASK-01 | Pending execution |
| [ ] | TASK-03 | test | Define frontend unit tests for draft state auto-save, explicit version bumping, and environment lineage switching | `frontend/tests/draft_and_lineage.test.ts` | TASK-02 | Pending execution |
| [ ] | TASK-04 | feat | Update flowStore with deep reactivity watcher, bumpVersion helper, publishOrSaveFlow, and environment lineage switching | `frontend/src/stores/flowStore.ts`, `frontend/src/types/flow.ts` | TASK-03 | Pending execution |
| [ ] | TASK-05 | feat | Add TopNav "Salvar Fluxo (vX.Y.Z)" button, Draft vs Saved badges, and FlowsModal draft guards on promotion/activation | `frontend/src/components/TopNav.vue`, `frontend/src/components/FlowsModal.vue` | TASK-04 | Pending execution |
| [ ] | TASK-06 | review | Run full sensor verification (Pytest, Vitest, Vue build, and SDD integrity sensor) | `backend/`, `frontend/`, `.specs/` | TASK-05 | Pending execution |

## Schema Dictionary
- **Status**: `[ ]` (Pending) | `[x]` (Verified Complete).
- **ID**: `TASK-01`, `TASK-02`, etc.
- **Type**: `test` | `feat` | `fix` | `refactor` | `docs` | `rules` | `skill` | `review`.
- **Target Files**: Concrete comma-separated file paths (relative to workspace root).
- **Dependencies**: Comma-separated list of preceding task IDs or `None`.
- **Evidence**: Commit hash (`git rev-parse --short HEAD`) + sensor output snippet.
