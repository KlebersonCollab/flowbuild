# Plan: Frontend Canvas & Dynamic Visual Builder

## 1. Problem Statement & Motivation
To match the decoupled experience of Langflow, the visual builder in Vue 3 + TypeScript must:
1. Render an interactive DAG workflow canvas supporting node addition, dragging, edge connections, and deletion.
2. Dynamically consume the backend's JSON Component Catalog and render all node controls, ports, and configuration forms without hardcoded UI code.
3. Manage flow state and execution feedback reactively using Pinia.
4. Stream real-time execution telemetry from the FastAPI backend via SSE, visually highlighting active and completed nodes.
5. Embody the Linear design language specified in [DESIGN.md](file:///F:/Projetos/flowbuild/DESIGN.md) (near-black surfaces `#010102`, hairline borders `#23252a`, and lavender-blue `#5e6ad2` accents).

## 2. Scope & Boundaries
- **In Scope**:
  - Vite + Vue 3 + TypeScript scaffolding with Tailwind CSS configured with Linear design tokens.
  - Interactive canvas powered by `@vue-flow/core`.
  - Universal dynamic node component (`CustomNode.vue`) rendering handles and status indicators.
  - Dynamic property inspector (`NodeInspector.vue`) generating form controls from schema types (`str`, `int`, `select`, `bool`, `dict`, `code`).
  - Component palette (`ComponentPalette.vue`) categorized by Triggers, Actions, Logic, and Transform.
  - Pinia stores (`useFlowStore`, `useRegistryStore`, `useExecutionStore`).
  - API and SSE client services connecting to FastAPI backend.
  - Automated component and store unit tests with Vitest.
- **Out of Scope**:
  - Full-screen code debugger with breakpoints and step-over pausing (future milestone).
  - Multi-user collaborative WebRTC canvas synchronization.

## 3. High-Level Approach
1. Initialize `frontend/` using Vite with Vue 3 and TypeScript template.
2. Install dependencies: `@vue-flow/core`, `@vue-flow/background`, `@vue-flow/controls`, `pinia`, `lucide-vue-next`, `tailwindcss`, `postcss`, `autoprefixer`, and `vitest`.
3. Configure Tailwind CSS with the exact design tokens from `DESIGN.md`.
4. Implement TypeScript domain types matching the backend's JSON contracts (`ComponentDefinition`, `FlowModel`, `NodeModel`, `EdgeModel`, `ExecutionEvent`).
5. Implement Pinia stores for state management and API client for REST + SSE.
6. Build Vue components: `CustomNode.vue`, `NodeInspector.vue`, `ComponentPalette.vue`, `TopNav.vue`, and `FlowCanvas.vue`.
7. Write and verify tests with Vitest, ensuring full compliance with acceptance criteria.

## 4. Dependencies & Prerequisites
- Node.js v20+ / npm v10+.
- Running backend or mock API for development testing.
- Design system tokens from `DESIGN.md`.

## 5. Architectural Decision Records (ADRs)
- [ADR 0001: Decoupled Architecture Inspired by Langflow](file:///F:/Projetos/flowbuild/.specs/project/ADRs/0001-decoupled-architecture-langflow-pattern.md)
