# ADR 0013: Responsive Flows Manager Viewport, Collapsible Sidebar, and Grid Layout

## Status
Accepted

## Date
2026-10-06

## Context
In ADR 0012, a split view worktree was introduced to organize workflows into folders. However, the modal dialog container had a fixed Tailwind `max-w-5xl` constraint (1024px) regardless of viewport size, and the sidebar occupied 256px unconditionally. On standard screens (1080p, laptops), this left roughly 700px for flow cards.

Because each flow card contains the flow name, up to 5 status badges, description editor, action buttons (Promover, Abrir, Excluir), and a multi-element webhook banner (method badge, auth badge, URL, and 2 copy buttons), content frequently collided, truncated, or broke layout lines awkwardly.

## Decision
1. **Dynamic Fluid Viewport & Maximization**:
   - Change default modal dimensions to `w-[96vw] max-w-[1550px] h-[92vh]` to take advantage of available screen real estate.
   - Introduce a Fullscreen / Maximize toggle button (`Maximize2` / `Minimize2`) in the modal header allowing users to expand the modal to 100% of the viewport (`fixed inset-0 w-full h-full rounded-none`).
2. **Collapsible Worktree Sidebar (`isSidebarOpen`)**:
   - Add a toggle button (`PanelLeftClose` / `PanelLeftOpen`) in the toolbar / breadcrumbs bar to collapse or expand the worktree sidebar with one click.
   - When collapsed, the flows pane expands to occupy 100% of the horizontal space.
3. **Card Layout & Anti-Clipping**:
   - Redesign card anatomy with clean responsive wrapping (`flex-wrap gap-2`).
   - Allow URLs in webhook banners to wrap or display cleanly with tooltips and responsive badge alignment, preventing clipping.
4. **Display Mode Switcher (List vs. Grid)**:
   - Provide a view mode toggle in the breadcrumbs bar:
     - **Lista**: Full-width cards (ideal for deep details and wide actions).
     - **Grade**: 2-column grid (`grid grid-cols-1 xl:grid-cols-2 gap-3.5`) in wide viewports to maximize visual density.
   - Persist user preference in `localStorage`.

## Consequences
- **Positive**: Eliminates horizontal clipping completely; provides maximum flexibility for both laptop and ultra-wide monitor users; preserves all flow operations with generous breathing room.
- **Backward Compatibility**: Fully backward compatible with existing flow data, worktree utilities, and environment promotions.
