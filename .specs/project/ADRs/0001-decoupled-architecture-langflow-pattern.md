# ADR 0001: Decoupled Architecture Inspired by Langflow

## Status
Accepted

## Context
We need to design a workflow builder for automations that is as decoupled as Langflow. In Langflow, the runtime execution engine and the visual user interface are completely decoupled:
1. The execution engine can run headlessly (e.g. via API or CLI) without the UI.
2. The frontend does not hardcode node components or forms; instead, the backend dynamically exposes a Component Registry with rich JSON schemas defining inputs, outputs, types, and configurations.
3. The user wants the backend in Python (for ecosystem synergy with automation, AI, and scripting) and the frontend in Vue 3 with TypeScript (modern reactive UI, type safety).

## Decision
1. **Backend Runtime (Python + FastAPI + asyncio)**:
   - Implement an extensible base class `Component` with typed input descriptors (`StrInput`, `IntInput`, `DictInput`, `BoolInput`, `HandleInput`) and output descriptors (`Output`).
   - Dynamically discover components via Python reflection/introspection and generate a standardized JSON Component Catalog.
   - Execute workflows using an asynchronous DAG engine (`asyncio`) supporting topological sorting, cycle detection, parallel branch execution, and context state passing.
   - Stream live execution status to the frontend via Server-Sent Events (SSE) or WebSockets.
   - Expose a headless execution endpoint (`POST /api/v1/flows/{id}/run`) so flows can be triggered programmatically or via webhooks.

2. **Frontend Builder (Vue 3 + TypeScript + @vue-flow/core)**:
   - Build a Single Page Application using Vite, Vue 3 Composition API (`<script setup>`), and TypeScript.
   - Use `@vue-flow/core` for graph visualization, interactive node dragging, handle connection, and zooming/panning.
   - Create a universal dynamic node component (`CustomNode.vue`) and dynamic property inspector that parses the backend's JSON schema to render input controls (inputs, dropdowns, code editors, sliders, toggles).
   - Manage application state using Pinia.
   - Implement UI styles according to [DESIGN.md](file:///F:/Projetos/flowbuild/DESIGN.md) (Linear dark system).

3. **Data Contract (Flow Schema JSON)**:
   - Standardize flow JSON structure:
     - `id`: string (UUID)
     - `name`: string
     - `description`: string
     - `nodes`: list of `{ id, type, position: {x, y}, data: { inputs: {...} } }`
     - `edges`: list of `{ id, source, sourceHandle, target, targetHandle }`

## Consequences
- **Positive**:
  - Zero frontend code changes required when introducing new automation components in Python.
  - Headless execution enables workflows to run in production without UI overhead.
  - Full TypeScript type-safety across the frontend.
  - Clean separation of concerns between visual rendering and runtime execution.
- **Negative / Considerations**:
  - Dynamic form generation in Vue requires robust dynamic input components (text, textarea, json, code, select).
  - Sandboxing is required when executing arbitrary user-defined Python code nodes.
