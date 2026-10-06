# Feature Plan: 100% Reactivity Auto-Save, Draft Lifecycle, Version Incrementing, and Cross-Environment Lineage Synchronization

## 1. Executive Summary
Empower FlowBuild with full 100% reactive canvas auto-save that retains working state without bumping version strings, guarantees that flows under edit stay in Draft and inactive states (preventing unexpected background execution), enables semantic version incrementing exclusively on explicit save ("Salvar Fluxo Atual"), and resolves bidirectional cross-environment flow lineage to eliminate duplicate flows when switching between DEV, QA, and PRD.

## 2. Architecture & Design Principles
- **Reactivity & Non-destructive Auto-save**: Deep watcher on node positions, dimensions, parameter inputs, and graph edges automatically writes debounced drafts to SQLite.
- **Draft Safety Guarantee**: In-progress drafts have `is_draft = true` and `is_active = false`. Crons and webhooks do not trigger uncommitted drafts.
- **Explicit Version Progression**: Semantic versioning patch increments (`v1.0.0` -> `v1.0.1`) only execute upon explicit user "Salvar Fluxo Atual" actions.
- **Environment Lineage Invariance**: Canvas flow ID synchronizes bidirectionally with target environment counterparts (`source_flow_id` lookup), preventing QA-suffixed flows from being cloned into DEV.

## 3. Scope & Milestones
- **Milestone 1**: Database schema & models update (`is_draft: bool` column in `flows` table and soft migration).
- **Milestone 2**: Frontend `flowStore` enhancements (deep auto-save reactivity, `publishOrSaveFlow` with version bump, lineage synchronization in `setEnvironment`).
- **Milestone 3**: UI refinements in `TopNav.vue` and `FlowsModal.vue` (dedicated "Salvar Fluxo (vX.Y.Z)" button, Draft vs Saved badges, and disabled states with explanatory tooltips for drafts).
- **Milestone 4**: Automated testing across backend (Pytest) and frontend (Vitest) verifying all invariants.
