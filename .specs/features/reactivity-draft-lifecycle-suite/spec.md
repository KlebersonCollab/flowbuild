# Feature Specification: 100% Reactivity Auto-Save, Draft Lifecycle, Version Incrementing, and Cross-Environment Lineage Synchronization

## Acceptance Criteria (BDD)

### AC-01: Auto-Save on Canvas Modification without Version Bumping
- **Given** an open workflow with version `v1.0.0`
- **When** a node is moved, an input parameter is edited, a connection is made, or a node is added
- **Then** the flow is immediately marked as `is_draft = true` and `is_active = false`
- **And** the flow state is auto-saved in the database without changing the version string `v1.0.0`.

### AC-02: Explicit Save Increments Semantic Subversion and Clears Draft
- **Given** an open workflow in draft state (`is_draft = true`, version `v1.0.0`)
- **When** the user explicitly triggers "Salvar Fluxo Atual" (via TopNav or FlowsModal)
- **Then** the version is incremented to `v1.0.1` (patch increment)
- **And** `is_draft` is set to `false`
- **And** the flow can now be toggled active/inactive and is eligible for promotion.

### AC-03: Draft Guard on Promotion and Activation
- **Given** a workflow in draft state (`is_draft = true`)
- **When** viewed in the FlowsModal or TopNav
- **Then** the workflow displays a `RASCUNHO` / `DRAFT` indicator
- **And** the Promote button is disabled with a notice requiring saving before promotion.

### AC-04: Bidirectional Cross-Environment Lineage Synchronization
- **Given** a DEV flow `flow-1` promoted to QA as `flow-1-qa` (with `source_flow_id = 'flow-1'`)
- **When** the user loads `flow-1-qa` in QA and then switches the active environment back to `DEV`
- **Then** the canvas automatically resolves and loads the parent DEV flow `flow-1`
- **And** saving while in DEV updates `flow-1` rather than generating a duplicate `flow-1-qa` in DEV.
