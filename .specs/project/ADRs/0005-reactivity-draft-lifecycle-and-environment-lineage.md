# ADR 0005: 100% Reactivity Auto-Save, Draft Lifecycle, Version Incrementing, and Cross-Environment Lineage Synchronization

## Status
Accepted

## Context
When orchestrating workflows in FlowBuild across multi-tier environments (DEV -> QA -> PRD):
1. **Reactivity & Persistence**: Users require that any interaction on the canvas (moving nodes, modifying parameters, connecting edges, or adding/deleting components) is 100% reactively auto-saved without losing working state.
2. **Draft Lifecycle & Inactivity**: While in an uncommitted draft editing state, the flow must be marked as `DRAFT` and remain **inactive** (`is_active: false`). Unfinished drafts must never be triggered by scheduled crons or incoming webhooks.
3. **Semantic Version Incrementing**: Auto-saving drafts must NOT bump the version string. Version or subversion increments (e.g., `v1.0.0` -> `v1.0.1`) must only occur upon explicit user intent ("Salvar o Fluxo atual"). Only saved/published flows can be activated/deactivated or promoted.
4. **Environment Switcher & Promotion Deduplication**: When a flow is promoted from DEV to QA, the QA flow inherits `source_flow_id` pointing to the DEV parent. Switching back from QA to DEV retained the QA ID on the canvas, leading to duplicate flow records (e.g. `flow-xxx-qa` saved into DEV).

## Decision
1. **Schema & Models**:
   - Add `is_draft: bool = False` to `flows` table in `DatabaseManager` with automatic PRAGMA migration.
   - Update `FlowModel` and `FlowRecord` with `is_draft`.
2. **Deep Reactivity & Non-Bumping Auto-Save**:
   - Implement deep reactive watchers and VueFlow node/edge event listeners in the frontend.
   - Any modification flags `is_draft = true` and `is_active = false` and initiates debounced auto-save to database.
   - Auto-save persists the canvas state without altering the current version.
3. **Explicit Save & Version Bump**:
   - Add `publishOrSaveFlow()` in `flowStore`: increments semantic patch subversion (`v1.0.0` -> `v1.0.1`), sets `is_draft = false`, and allows flow activation/promotion.
   - Add dedicated "Salvar Fluxo" button and Draft badge to `TopNav.vue` and `FlowsModal.vue`.
4. **Bidirectional Lineage Synchronization in `setEnvironment`**:
   - When switching environments, `setEnvironment(env)` automatically resolves and loads the corresponding linked flow (matching `source_flow_id` or parent ID) belonging to the target environment.
   - `saveFlowToBackend` sanitizes IDs, preventing cross-environment pollution and duplicate flows.
5. **Draft Guard on Execution & Promotion**:
   - Draft flows cannot be promoted or scheduled until explicitly saved.

## Consequences
- **Positive**: 100% reactive editing with zero lost work, clear distinction between draft and saved states, safe isolation of in-progress flows from background triggers, and clean lineage without duplicate flows.
- **Negative**: Extra column `is_draft` in database schema (handled via automatic soft migration).
