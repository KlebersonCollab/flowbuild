# Coding & Project Conventions (FlowBuild)

## 1. Backend (Python) Conventions

- **Style Guide**: PEP 8 compliance enforced with `ruff`.
- **Naming Conventions**:
  - Modules and files: `snake_case.py` (e.g. `dag_engine.py`, `component_registry.py`).
  - Classes: `PascalCase` (e.g. `BaseComponent`, `HttpRequestNode`, `ExecutionContext`).
  - Functions & Variables: `snake_case` (e.g. `execute_flow`, `topological_sort`).
  - Constants: `UPPER_SNAKE_CASE` (e.g. `DEFAULT_TIMEOUT_SECONDS`).
- **Typing & Validation**:
  - Full type annotations on all function signatures using modern Python 3.11+ syntax (`str | None`, `list[dict[str, Any]]`).
  - Request and response contracts validated via Pydantic v2 models.
- **Asynchronous Code**:
  - All I/O operations (HTTP requests, file access, flow execution) must be `async def`.
  - Thread pools (`asyncio.to_thread`) reserved exclusively for blocking CPU-bound tasks.
- **Error Handling**:
  - Custom domain exceptions inheriting from `FlowBuildError` (e.g. `CyclicGraphError`, `NodeExecutionError`).
  - Never silence exceptions with naked `except: pass`.

## 2. Frontend (Vue 3 + TypeScript) Conventions

- **Component Architecture**:
  - Vue 3 Single File Components (SFC) using `<script setup lang="ts">`.
  - PascalCase for SFC filenames (e.g. `FlowCanvas.vue`, `NodeInspector.vue`, `CustomNode.vue`).
  - Props defined via `defineProps<{ ... }>()` with TypeScript interfaces.
  - Emits defined via `defineEmits<{ ... }>()`.
- **Naming Conventions**:
  - Variables, functions, and composables: `camelCase` (e.g. `selectedNode`, `useFlowStore`).
  - Types and Interfaces: `PascalCase` (e.g. `ComponentSchema`, `FlowDefinition`, `NodeData`).
- **State Management**:
  - Pinia stores named `use<Domain>Store` (e.g. `useFlowStore`, `useRegistryStore`).
- **Design System Fidelity**:
  - Strict adherence to tokens defined in [DESIGN.md](file:///F:/Projetos/flowbuild/DESIGN.md).
  - Canvas surface `#010102`, cards and panels `#0f1011` / `#141516`, hairline borders `#23252a`, accent `#5e6ad2`.
  - Zero arbitrary uncalibrated colors.

## 3. Communication & Schema Conventions

- **Flow Serialization Contract**:
  - Standard JSON schema representing flows:
    - `id`: UUID string.
    - `name`: string.
    - `nodes`: list of nodes with `id`, `type`, `position: { x, y }`, `data: { inputs: Record<string, any> }`.
    - `edges`: list of edges with `id`, `source`, `sourceHandle`, `target`, `targetHandle`.
- **API Response Formatting**:
  - Consistent JSON envelop: `{ "success": boolean, "data": Any, "error": string | null }`.
