# System Architecture (FlowBuild)

## 1. High-Level Architectural Diagram

```
+-----------------------------------------------------------------------------------+
|                            VUE 3 FRONTEND (SPA)                                   |
|                                                                                   |
|  +--------------------+  +----------------------+  +---------------------------+  |
|  | Component Palette  |  |  Interactive Canvas  |  | Dynamic Node Inspector    |  |
|  | (Grouped Catalog)  |  |   (@vue-flow/core)   |  | (Schema-driven Controls)  |  |
|  +--------------------+  +----------------------+  +---------------------------+  |
|            ^                        |                           ^                 |
|            |                        v                           |                 |
|            |             +---------------------+                |                 |
|            +-------------| Pinia Stores        |----------------+                 |
|                          | (Flow, Registry, Run)|                                 |
|                          +---------------------+                                  |
+-------------------------------------|---------------------------------------------+
                                      | HTTP (REST) & SSE
                                      v
+-----------------------------------------------------------------------------------+
|                            PYTHON FASTAPI BACKEND                                 |
|                                                                                   |
|  +----------------------+  +---------------------+  +--------------------------+  |
|  | Component Registry   |  | Flow Storage / API  |  | Webhook Ingestion        |  |
|  | Introspects Python   |  | CRUD & Serializer   |  | Headless Trigger         |  |
|  | Components to JSON   |  |                     |  |                          |  |
|  +----------------------+  +---------------------+  +--------------------------+  |
|            |                        |                           |                 |
|            v                        v                           v                 |
|  +-----------------------------------------------------------------------------+  |
|  |                           DAG EXECUTION ENGINE                              |  |
|  |  - Graph Validation & Cycle Detection                                       |  |
|  |  - Topological Sorter (Kahn's / DFS)                                        |  |
|  |  - Async Branch Concurrency (asyncio)                                       |  |
|  |  - Context & Data Passing (Output -> Input Resolution)                      |  |
|  |  - Telemetry & Event Streamer (SSE / WebSocket)                             |  |
|  +-----------------------------------------------------------------------------+  |
|                                     |                                             |
|                                     v                                             |
|  +-----------------------------------------------------------------------------+  |
|  |                           AUTOMATION NODES                                  |  |
|  |  [WebhookTrigger] [HttpRequest] [PythonSandbox] [IfElse] [Transform] [LLM]  |  |
|  +-----------------------------------------------------------------------------+  |
+-----------------------------------------------------------------------------------+
```

## 2. Key Architectural Subsystems

### A. Dynamic Component Model (Langflow Inspired)
In Langflow, components are self-describing Python classes. FlowBuild replicates this pattern:
- Every node inherits from `BaseComponent`.
- Inputs are declared as typed descriptors:
  - `StrInput(name="url", label="URL", required=True)`
  - `IntInput(name="retries", label="Retries", default=3)`
  - `SelectInput(name="method", label="Method", options=["GET", "POST", "PUT", "DELETE"])`
  - `CodeInput(name="script", label="Python Code", language="python")`
  - `DictInput(name="headers", label="Headers")`
  - `HandleInput(name="payload", label="Payload", input_types=["any", "dict"])`
- Outputs are declared via `Output(name="response", label="Response", output_type="dict", method="execute")`.
- When the backend boots, the `ComponentRegistry` automatically discovers all component classes and serializes them into a JSON Schema exposed via `GET /api/v1/components`.

### B. Graph Validation & DAG Execution Engine
Workflows are executed asynchronously:
1. **Serialization Validation**: Validates the flow JSON structure.
2. **Graph Construction**: Maps nodes and directed edges.
3. **Cycle Check**: Verifies that the graph is a Directed Acyclic Graph (DAG) using topological sort or depth-first cycle detection.
4. **Dependency Resolution**: Each node's input ports are evaluated. If an input port is linked by an edge to an upstream node's output port, it waits until the upstream node completes and receives its output value. If unlinked, it uses the static user configuration value.
5. **Concurrent Execution**: Independent branches run in parallel via `asyncio.create_task` or worker pools.
6. **Telemetry Streaming**: Node state updates (`pending` -> `running` -> `success` / `error`) and execution logs are emitted to the frontend SSE stream in real time.

### C. Headless Execution Protocol
- Flows can run without the frontend.
- When an incoming webhook matches a `WebhookTrigger` (`POST /api/v1/webhook/{path}`), the engine loads the flow from storage, injects the HTTP request payload into the trigger node, and executes the flow headlessly.
- Cron jobs or background schedules trigger flows via background tasks (`asyncio` / APScheduler / Celery).

### D. Frontend Visual Builder (Vue 3 + TypeScript)
- **Canvas**: Built on `@vue-flow/core`. Supports dragging nodes, creating edges between handles, zooming, panning, and mini-map navigation.
- **Universal Node Component (`CustomNode.vue`)**: Renders handles for inputs on the left and outputs on the right. Displays node title, icon, badges, and real-time execution status (idle, running spinner, green success border, red error border).
- **Dynamic Property Inspector (`NodeInspector.vue`)**: When a node is selected, this panel inspects the node's schema in the registry and renders the appropriate UI controls (text inputs, selects, toggles, code editor) dynamically without hardcoding.
- **Design System**: All colors, typography, borders, and spacing strictly follow [DESIGN.md](file:///F:/Projetos/flowbuild/DESIGN.md) (Linear dark system).
