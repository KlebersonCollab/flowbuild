# Task List: Modern Toast Notification System

## Sequence Guidelines (MetaGPT SOP)
- **Strict Sequential Order**: Tasks must be executed top-to-bottom without reordering.
- **Atomic File Boundaries**: Each task modifies at most 1–3 specific target files.
- **Decoupled Test Setup**: Test tasks (`Type: test`) precede implementation tasks (`Type: feat`).
- **Sensor Evidence Gate**: Mark complete `[x]` ONLY after passing build, lint, and test sensors with recorded evidence.

## Implementation Tasks

| Status | ID | Type | Description | Target Files | Dependencies | Evidence |
|---|---|---|---|---|---|---|
| [x] | TASK-01 | test | Add unit tests for toastStore verifying add, remove, and auto-dismiss behavior | `frontend/tests/toast.test.ts` | None | [toast.test.ts] 4 vitest tests passing verifying type dispatch, auto-dismiss timers, and clearAll |
| [x] | TASK-02 | feat | Implement reactive toastStore with success, warn, error, and info helpers | `frontend/src/stores/toastStore.ts` | TASK-01 | [toastStore.ts] Global Pinia store with typed toast models, auto-expiry, and convenient helper methods |
| [x] | TASK-03 | feat | Build ToastContainer component matching Linear dark tokens and smooth transitions | `frontend/src/components/ToastContainer.vue`, `frontend/src/App.vue` | TASK-02 | [ToastContainer.vue & App.vue] Mounted globally at root layout with Linear dark borders, semantic accents, and Vue transitions |
| [x] | TASK-04 | feat | Replace native alert calls in TopNav with toast.warn and toast.error | `frontend/src/components/TopNav.vue` | TASK-03 | [TopNav.vue] Replaced all browser alert() calls with toast.warn and toast.error (zero alert() references remain) |
| [x] | TASK-05 | review | Run full sensor verification (Pytest, Vitest, Vue build, and SDD integrity sensor) | `frontend/`, `backend/`, `.specs/` | TASK-04 | 47/47 Pytest passing, 33/33 Vitest passing, clean vue-tsc build in 512ms, SDD sensor 100% OK |

## Schema Dictionary
- **Status**: `[ ]` (Pending) | `[x]` (Verified Complete).
- **ID**: `TASK-01`, `TASK-02`, etc.
- **Type**: `test` | `feat` | `fix` | `refactor` | `docs` | `rules` | `skill` | `review`.
- **Target Files**: Concrete comma-separated file paths (relative to workspace root).
- **Dependencies**: Comma-separated list of preceding task IDs or `None`.
- **Evidence**: Commit hash (`git rev-parse --short HEAD`) + sensor output snippet.
