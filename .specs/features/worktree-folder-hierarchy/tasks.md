# Task List: Worktree Folder Hierarchy & Split Navigation in Flows Manager

## Sequence Guidelines (MetaGPT SOP)
- **Strict Sequential Order**: Tasks must be executed top-to-bottom without reordering.
- **Atomic File Boundaries**: Each task modifies at most 1–3 specific target files.
- **Decoupled Test Setup**: Test tasks (`Type: test`) precede implementation tasks (`Type: feat`).
- **Sensor Evidence Gate**: Mark complete `[x]` ONLY after passing build, lint, and test sensors with recorded evidence.

## Implementation Tasks

| Status | ID | Type | Description | Target Files | Dependencies | Evidence |
|---|---|---|---|---|---|---|
| [x] | TASK-01 | test | Create unit tests for folderTree utilities (hierarchical parsing, flow count aggregation, recursive matching) | `frontend/tests/folder_tree.test.ts` | None | `dfc8007` + `vitest tests/folder_tree.test.ts 11 passed` |
| [x] | TASK-02 | feat | Implement buildFolderTree, matchFlowFolder, and flattenTree utilities in folderTree.ts | `frontend/src/utils/folderTree.ts` | TASK-01 | `dfc8007` + `folderTree.ts tree building & matching utilities implemented` |
| [x] | TASK-03 | feat | Refactor FlowsModal.vue to a two-pane worktree split view with collapsible folders, folder search, and breadcrumbs | `frontend/src/components/FlowsModal.vue` | TASK-02 | `dfc8007` + `FlowsModal.vue split worktree view implemented & vue build passed` |
| [x] | TASK-04 | test | Add component integration tests for worktree navigation and selection in FlowsModal | `frontend/tests/flows_modal_worktree.test.ts` | TASK-03 | `dfc8007` + `vitest tests/flows_modal_worktree.test.ts 3 passed` |
| [x] | TASK-05 | review | Run full sensor verification (Pytest, Vitest, Vue build, and SDD integrity sensor) | `frontend/`, `backend/`, `.specs/` | TASK-04 | `dfc8007` + `62 pytest passed, 60 vitest passed, vue build clean, sdd sensor OK` |

## Schema Dictionary
- **Status**: `[ ]` (Pending) | `[x]` (Verified Complete).
- **ID**: `TASK-01`, `TASK-02`, etc.
- **Type**: `test` | `feat` | `fix` | `refactor` | `docs` | `rules` | `skill` | `review`.
- **Target Files**: Concrete comma-separated file paths (relative to workspace root).
- **Dependencies**: Comma-separated list of preceding task IDs or `None`.
- **Evidence**: Commit hash (`git rev-parse --short HEAD`) + sensor output snippet.
