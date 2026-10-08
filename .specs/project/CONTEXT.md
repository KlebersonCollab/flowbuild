# Domain Glossary & Project Context (FlowBuild)

## 1. Core Concepts & Taxonomy

- **Flow / Workflow**: A directed graph representing an automated sequence of actions and data transformations, composed of Nodes connected by Edges. Can be saved, versioned, exported as JSON, and executed independently in the backend.
- **Node (Component Instance)**: An instantiated step inside a Flow canvas. Corresponds to a specific Component definition (e.g. `WebhookTrigger`, `HttpRequest`, `PythonCode`, `OpenAIChat`), maintaining unique coordinates, configuration inputs, and execution state.
- **Component (Component Definition)**: A reusable, self-describing Python class defining input parameters, output handles, categorization, and execution logic (`build` or `run` method).
- **Handle / Port**: Connection points on a Node.
  - **Input Port**: Receives data or triggers from upstream Nodes. Can accept literals or connections.
  - **Output Port**: Emits computed data or triggers downstream Nodes.
- **Edge (Connection)**: A directed link connecting a source Node's Output Port to a target Node's Input Port. Carries typed data payloads during workflow execution.
- **DAG (Directed Acyclic Graph)**: The mathematical graph structure formed by validated Nodes and Edges, topologically sorted to determine execution sequence without cycles.
- **Execution Graph / Runner**: The Python engine runtime responsible for topological sorting, dependency injection, concurrent task execution (`asyncio`), state resolution, and error bubbling.
- **Headless Runtime**: Capability of the backend to execute flows triggered by HTTP Webhooks, Cron/Schedules, or CLI without loading or running the frontend UI.
- **Component Registry**: The central catalog in the backend that discovers, indexes, and validates all available Components, exposing them as a JSON Schema catalog to the frontend.
- **Dynamic Node Form**: The frontend mechanism where node configuration inputs (text, numbers, code editors, select menus, toggle switches) are rendered dynamically from the backend's JSON Component Schema, eliminating the need to write unique Vue components for each automation node.
- **Execution Context**: An in-memory key-value dictionary and runtime state passed across nodes during flow execution, holding environment secrets, node execution results, logs, and run telemetry.
- **Trigger**: A specialized node initiating flow execution (e.g. Incoming Webhook, Scheduled Cron, Event listener, or Manual Test Run).
- **Action**: An operational node performing work or transformation (e.g., HTTP Call, Custom Python Sandbox Execution, Database Query, LLM inference).
- **Linear Design System**: The UI visual language adhering to [DESIGN.md](file:///F:/Projetos/flowbuild/DESIGN.md), featuring near-black surfaces (`#010102`), subtle surface ladders, hairline borders, and Linear lavender-blue (`#5e6ad2`) accents.
- **Delay / Sleep Node (`DelayComponent`)**: A control flow logic component that suspends workflow execution for a specified duration (`delay` with unit: `seconds`, `milliseconds`, `minutes`) using non-blocking asynchronous sleep (`asyncio.sleep`) before transparently forwarding incoming payload data (`input_data`) to downstream nodes.
- **Switch / Router Node (`SwitchNodeComponent`)**: A multi-branch control flow logic component that routes incoming data to one of several output paths (`case_1`, `case_2`, `case_3`, or `default_branch`) based on expression matching, with cascading branch skipping on unselected handles.
- **Data Filter Node (`DataFilterComponent`)**: A transform component that filters arrays of items or dictionary payloads declaratively based on field comparison operators (`equals`, `contains`, `greater_than`, etc.) or Python expressions, emitting `filtered_items`, `discarded_items`, and count telemetry.
- **Slack Notification Node (`SlackWebhookComponent`)**: An action component that sends formatted messages and alerts to Slack channels via Incoming Webhooks, supporting custom bot identity, Block Kit blocks, attachments, variable interpolation, and error resilience.

---

## 2. Invariants & Architectural Contracts

1. **Schema Decoupling**: The Vue 3 frontend must never hardcode node execution logic or node input fields. All node parameters, types, and options are defined in Python and rendered dynamically in the UI.
2. **Headless Execution**: The Python backend execution engine must be 100% functional via REST API / CLI / Webhook triggers without requiring a browser or frontend connection.
3. **Graph Serialization**: A flow is canonically serialized as a clean JSON document containing metadata, nodes array, and edges array.
4. **Non-blocking Concurrency**: All node runs in the execution engine support asynchronous execution (`asyncio`) so independent branches in the DAG run concurrently.
5. **Real-time Telemetry**: During execution from the visual builder, the engine streams execution events (node started, node completed, node error, intermediate data) via Server-Sent Events (SSE) or WebSockets.
