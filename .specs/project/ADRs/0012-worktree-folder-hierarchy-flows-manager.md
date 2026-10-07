# ADR 0012: Worktree Folder Hierarchy & Split Navigation in Flows Manager

## Status
Accepted

## Date
2026-10-06

## Context
In ADR 0004, flow organization was initially introduced with a flat `folder` string field and a horizontal row of filter pill buttons in `FlowsModal.vue`. As the number of flows and organizational categories grows, horizontal buttons present severe UX limitations:
1. Horizontal scroll fatigue when numerous folders exist.
2. Lack of hierarchical relationships (e.g., inability to organize `Financeiro/Cobrança` and `Financeiro/Relatórios` under a common parent).
3. Cluttered layout that consumes vertical space before the user can see their workflows.

The user requested a "worktree" style layout where folders are organized in a tree hierarchy with expandable nodes and clean split navigation.

## Decision
1. **Hierarchical Path Resolution (`/` Delimiter)**:
   - Treat `/` in flow folder strings as a hierarchy separator (e.g. `Financeiro/Cobrança` represents child `Cobrança` inside parent `Financeiro`).
   - Default flows with empty or undefined folder to `Geral`.
2. **Dedicated Pure Tree Utility (`folderTree.ts`)**:
   - Provide `buildFolderTree(flows)` to transform a flat list of flows into a recursive `FolderTreeNode` structure:
     - `id`: unique canonical path string (e.g., `Financeiro/Cobrança`).
     - `name`: folder segment name.
     - `fullPath`: complete path.
     - `children`: nested `FolderTreeNode[]`.
     - `flowCount`: total count of flows in this folder and its subfolders.
     - `directCount`: count of flows directly assigned to this path.
   - Provide helper `matchFlowFolder(flowFolder, selectedPath)` supporting exact matches or sub-tree matches.
3. **Split View Layout in `FlowsModal.vue`**:
   - Replace the horizontal filter pills bar with a responsive two-pane split layout:
     - **Left Pane (Worktree Explorer)**:
       - Top: "Todos os Fluxos" with aggregate count.
       - Recursive folder tree with expandable/collapsible chevrons (`ChevronRight`, `ChevronDown`), folder icons (`Folder`, `FolderOpen`), level indentation, and flow counter badges.
       - Quick filter input to search folders in the tree.
     - **Right Pane (Flows Content)**:
       - Header displaying current folder breadcrumb path and total flows count.
       - Existing rich flow cards (status toggle, version, environment, promotions, edit description, canvas open, delete, and secure webhook cURL generation).
4. **Design System Adherence**:
   - Use Linear dark tokens from `DESIGN.md`: surface `#0f1011`, sidebar `#0b0c0e`, hairline `#23252a`, accent `#5e6ad2`, hover states `#828fff`.

## Consequences
- **Positive**: Clean, scalable navigation inspired by IDE worktree explorers; support for deep organizational hierarchies without schema changes in database.
- **Backward Compatibility**: Fully backward compatible with existing flat folder strings.
