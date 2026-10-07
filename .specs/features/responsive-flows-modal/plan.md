# Feature Plan: Responsive Flows Manager Viewport & Grid Layout

## 1. Problem Statement
The flows management dialog (`FlowsModal.vue`) felt cramped and caused text/badges/buttons to truncate or clip horizontally because:
- The modal width was capped at `max-w-5xl` (1024px).
- The worktree sidebar permanently claimed 256px, leaving minimal room for information-dense flow cards.
- The cards lacked responsive multi-column options and fluid wrapping for webhooks and action buttons.

## 2. Goals & Success Criteria
- Expand modal default dimensions to `w-[96vw] max-w-[1550px] h-[92vh]`.
- Provide a Fullscreen / Maximize toggle in the modal header (`Maximize2` / `Minimize2`).
- Provide a Collapsible Sidebar toggle (`PanelLeftClose` / `PanelLeftOpen`).
- Support View Mode switcher: single-column full-width List view vs. 2-column Grid view (`grid-cols-1 xl:grid-cols-2`).
- Ensure cards, webhook URLs, and badges do not clip, with clean wrapping and tooltips.
- 100% test pass rate across Vitest and Pytest test suites.

## 3. Scope Boundaries
- **In Scope**:
  - `frontend/src/components/FlowsModal.vue`: viewport sizing, maximize mode, sidebar collapse, view mode switcher (list/grid), card wrapping refinements.
  - `frontend/tests/flows_modal_responsive.test.ts`: tests for maximize toggle, sidebar collapse, and view mode switcher.
- **Out of Scope**:
  - Drag-and-drop column reordering (future milestone).
