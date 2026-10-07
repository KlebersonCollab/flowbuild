# Feature Specification: Responsive Flows Manager Viewport & Grid Layout

## 1. UI Components & State Models

### 1.1 Modal Window Dimensions & Maximize Mode
In `FlowsModal.vue`:
- State: `isMaximized = ref<boolean>(false)`
- When `!isMaximized`:
  - Classes: `w-[96vw] max-w-[1550px] h-[92vh] rounded-xl`
- When `isMaximized`:
  - Classes: `fixed inset-0 w-full h-full rounded-none max-w-none max-h-none`
- Header button: `Maximize2` (when not maximized) and `Minimize2` (when maximized).

### 1.2 Collapsible Worktree Sidebar
- State: `isSidebarOpen = ref<boolean>(true)`
- Header / Breadcrumb toggle button: `PanelLeftClose` (when open) / `PanelLeftOpen` (when closed).
- When `!isSidebarOpen`:
  - Sidebar `<aside>` is hidden (`v-if="isSidebarOpen"`).
  - Main panel `<main>` takes `w-full flex-1`.
  - Breadcrumb displays a small button to re-open sidebar with tooltip.

### 1.3 View Mode (List vs. Grid)
- State: `viewMode = ref<'list' | 'grid'>('list')`
- Stored/restored with `localStorage.getItem('flowbuild_flows_view_mode')`.
- Toggle buttons in breadcrumb toolbar:
  - List icon (`List`) -> single column (`space-y-3`).
  - Grid icon (`LayoutGrid`) -> 2-column grid (`grid grid-cols-1 xl:grid-cols-2 gap-3.5`).

### 1.4 Anti-Clipping Card Structure
- Card header wraps comfortably:
  - Title & badges: `flex flex-wrap items-center gap-2 min-w-0 flex-1`.
  - Action buttons: `flex flex-wrap items-center gap-1.5 shrink-0`.
- Webhook banner:
  - Responsive layout: `flex flex-col sm:flex-row sm:items-center justify-between gap-2 p-2.5 rounded bg-[#090a0b]`.
  - URL text: `break-all` or `truncate` with full tooltip title and horizontal scrolling if necessary.
  - Copy buttons: clean alignment with fixed icons and clear feedback.

## 2. Acceptance Criteria & Test Matrix
1. **Maximize Mode**: Clicking the maximize button toggles `isMaximized` and applies full-screen CSS classes. Clicking minimize restores window dimensions.
2. **Sidebar Collapse**: Clicking the sidebar toggle hides the sidebar and gives full width to the flows pane. Re-clicking restores the worktree.
3. **View Mode Toggle**: Switching between list and grid mode toggles `viewMode` state, updates container classes (`space-y-3` vs `grid grid-cols-1 xl:grid-cols-2`), and persists choice in localStorage.
4. **Card Information Visibility**: Badges, actions, and webhook controls remain completely visible without truncation collisions.
