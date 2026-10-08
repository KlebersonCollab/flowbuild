# Plan: Showcase Workflow Templates (ADR 0021)

## 1. Problem Statement & Motivation
Users need intuitive, real-world examples demonstrating the potential of FlowBuild's latest components (`DelayComponent`, `SwitchNodeComponent`, `DataFilterComponent`, `SlackWebhookComponent`, `PaginatedHttpComponent`). Without pre-built showcase templates, users must manually discover and connect these advanced nodes from scratch.

Providing pre-built, ready-to-run templates directly from the top navigation dropdown allows users to test, inspect, and understand complex orchestration patterns in seconds.

## 2. Scope & Boundaries
- **In Scope**:
  - Implement 4 new templates in `frontend/src/stores/flowStore.ts`:
    - `switch_router_flow`: Multi-branch routing with `SwitchNodeComponent` and `SlackWebhookComponent`.
    - `data_filter_alert_flow`: Collection filtering with `DataFilterComponent` and dual output branch handling.
    - `delay_polling_flow`: Timed async pauses with `DelayComponent`.
    - `etl_pagination_filter_flow`: End-to-end pipeline uniting pagination, filtering, JSON transformation, and Slack alerts.
  - Review and refine existing 5 templates to ensure clear labels and descriptions.
  - Group templates into clear semantic sections inside the `TopNav.vue` dropdown.
  - Frontend unit tests verifying all 9 templates load correct node types, edges, and valid inputs.
- **Out of Scope**:
  - Backend schema migrations (templates are client-side canvas initializers serialized into standard flows).

## 3. High-Level Approach
- Expand `loadTemplate` in `flowStore.ts` with explicit node coordinates, descriptive default payloads, and correctly configured port connections (`sourceHandle` / `targetHandle`).
- Upgrade `TopNav.vue` dropdown layout to display grouped categories (*Básicos*, *Lógica & Controle*, *Dados & Alertas*) with colored badge accents matching `DESIGN.md`.
- Validate via Vitest that every template loads all expected nodes, handles, and properties.

## 4. Dependencies & Prerequisites
- `flowStore.ts` and `TopNav.vue`.
- Built-in components registered in backend and frontend.

## 5. Architectural Decision Records (ADRs)
- Relates to [ADR 0021: Showcase Workflow Templates for Advanced Logic, Data Filtering and Messaging Nodes](../../project/ADRs/0021-showcase-templates.md).
