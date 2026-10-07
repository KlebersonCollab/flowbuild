# Feature Specification: Worktree Folder Hierarchy & Split Navigation in Flows Manager

## 1. Domain Model: Folder Tree Data Structures
File: `frontend/src/utils/folderTree.ts`

```typescript
export interface FolderTreeNode {
  id: string              // Unique identifier/path (e.g., "Financeiro/Cobrança")
  name: string            // Display name segment (e.g., "Cobrança")
  fullPath: string        // Canonical full path (e.g., "Financeiro/Cobrança")
  depth: number           // Tree nesting level (0 for root items)
  children: FolderTreeNode[]
  flowCount: number       // Count of flows in this folder and its descendant subfolders
  directCount: number     // Count of flows directly assigned to this folder
}
```

## 2. Behavioral Specifications

### 2.1 Hierarchy Construction (`buildFolderTree`)
- Given an array of flows `Array<{ folder?: string }>`:
- Flows with empty, null, or whitespace-only folders default to `"Geral"`.
- Paths with forward slashes `/` are split into segments (e.g., `"Financeiro/Cobrança/PIX"` -> parent `"Financeiro"`, child `"Cobrança"`, grandchild `"PIX"`).
- Intermediate parents are created automatically even if no flow is directly assigned to the parent.
- Trailing and leading slashes are stripped.
- Duplicate segments are consolidated.
- `flowCount` aggregates flows in the current folder plus all descendant children.
- Tree nodes are sorted alphabetically by `name`.

### 2.2 Path Matching (`matchFlowFolder`)
- A flow with folder `flowFolder` matches a selected worktree folder `selectedPath`:
  - When `selectedPath === 'all'`: returns `true` for all flows.
  - When `selectedPath === flowFolder`: exact match returns `true`.
  - When `flowFolder.startsWith(selectedPath + '/')`: recursive descendant match returns `true`.
  - Otherwise returns `false`.

### 2.3 Split View Layout (`FlowsModal.vue`)
- Left sidebar (`md:w-64` / `w-72`):
  - Top action item: "Todos os Fluxos" with total count badge.
  - Search input: filters folder nodes in real time.
  - Recursive folder node rendering:
    - Expand/collapse chevron (`ChevronDown` / `ChevronRight`) for nodes with children.
    - Folder icon (`FolderOpen` when expanded/selected, `Folder` otherwise).
    - Segment name and total count badge.
    - Left padding based on `depth * 12px`.
    - Active highlight when selected (`bg-[#5e6ad2]/20 text-[#828fff]`).
  - Quick action: "Nova Pasta" input/button to register a new folder path.
- Right content panel:
  - Header with breadcrumb path and flows count.
  - Filtered list of flows using `matchFlowFolder`.
  - Empty state message when the selected folder contains no flows in the active environment.
  - Existing flow cards preserved with all features (open, promote, toggle active, description edit, cURL generation).

## 3. Acceptance Criteria & Test Matrix
1. **Tree Builder**: Flat list `['Financeiro/Cobrança', 'Financeiro/Fiscal', 'RH', '']` produces root nodes `Financeiro`, `Geral`, `RH` with `Financeiro` having 2 children and `flowCount = 2`.
2. **Path Matching**: Selecting `Financeiro` matches both `Financeiro` and `Financeiro/Cobrança`.
3. **Collapsible State**: Toggling chevron on a parent folder expands/collapses its nested child nodes.
4. **Environment Isolation**: The folder tree dynamically reflects flow counts for the active environment (`dev`, `qa`, `prd`).
5. **Flow Management Actions**: All existing actions (open, save, delete, promote, copy webhook url/curl) operate identically without regression.
