# Feature Plan: Worktree Folder Hierarchy & Split Navigation in Flows Manager

## 1. Problem Statement
The flows management modal (`FlowsModal.vue`) previously displayed folders as a flat horizontal strip of pill buttons. As users create multiple workflows across departments or domains, this layout suffered from:
- Poor scalability when many folders exist.
- Inability to nest folders hierarchically (e.g., `Financeiro/Cobrança` vs `Financeiro/Boletos`).
- Visual clutter and inefficient space utilization within a wide modal dialog.

## 2. Goals & Success Criteria
- Implement a hierarchical tree builder (`folderTree.ts`) that parses paths delimited by `/` into a recursive `FolderTreeNode` structure with flow count aggregations.
- Replace the horizontal filter pills in `FlowsModal.vue` with a modern IDE-style split view (sidebar worktree on the left, flow cards on the right).
- Support collapsible/expandable directory nodes with toggle chevrons and folder icons.
- Provide a quick search/filter input for folders in the worktree.
- Maintain full compatibility with existing flow definitions and active environments (`dev`, `qa`, `prd`).
- Retain all flow card capabilities (open in canvas, promote to QA/PRD, toggle active, edit description, copy webhook URL/cURL).
- 100% test coverage for the tree structure and modal integration.

## 3. Scope Boundaries
- **In Scope**:
  - `frontend/src/utils/folderTree.ts`: pure tree construction and path filtering utilities.
  - `frontend/tests/folder_tree.test.ts`: comprehensive unit tests for tree hierarchy, flow count aggregation, and path matching.
  - `frontend/src/components/FlowsModal.vue`: split view layout with left worktree sidebar and right flows content area.
  - `frontend/tests/flows_modal_worktree.test.ts`: component tests for the worktree UI and folder selection.
- **Out of Scope**:
  - Database schema changes (the existing `folder` string field natively supports `/` delimited paths).
  - Drag-and-drop flow reassignment across folders (future milestone).
