# Project Roadmap & Milestones (FlowBuild)

## Milestone 1: Architectural Foundation & Decoupled Engine Core (Target: Sprint 1)
- [ ] Define Python Component Base Classes (`Component`, `Input`, `Output`, `FieldTypes`).
- [ ] Implement dynamic Component Registry with auto-discovery and JSON schema serialization.
- [ ] Implement core DAG Engine: graph parsing, topological sort, dependency injection, and cycle detection.
- [ ] Implement async execution runner with context passing and error handling.
- [ ] Implement FastAPI endpoints: `GET /api/v1/components`, `POST /api/v1/flows`, `POST /api/v1/flows/{id}/run`, and SSE execution event stream.

## Milestone 2: Vue 3 Visual Builder & Dynamic Canvas (Target: Sprint 2)
- [ ] Initialize Vue 3 + Vite + TypeScript project adhering to [DESIGN.md](file:///F:/Projetos/flowbuild/DESIGN.md).
- [ ] Integrate `@vue-flow/core` with custom node wrapper (`CustomNode.vue`).
- [ ] Implement dynamic node configuration panel driven entirely by component JSON schema.
- [ ] Implement Pinia stores (`flowStore`, `registryStore`, `executionStore`).
- [ ] Connect frontend to backend SSE execution stream for live node highlighting and telemetry.

## Milestone 3: Core Automation Nodes & Extensibility (Target: Sprint 3)
- [ ] Automation Trigger nodes: `ManualTrigger`, `WebhookTrigger`, `ScheduleTrigger`.
- [ ] Operational Action nodes: `HttpRequest`, `PythonScript`, `DataFilter`, `JsonTransform`.
- [ ] Control Flow nodes: `IfCondition`, `SwitchNode`, `LoopIterator`.
- [ ] AI / LLM nodes: `PromptTemplate`, `OpenAIChat`, `GeminiChat`.
- [ ] Custom Python component loader from user directory (`components/custom/`).

## Milestone 4: Persistence, Sandboxing & Production Readiness (Target: Sprint 4)
- [ ] Database persistence for flows and execution history (SQLAlchemy / SQLite / PostgreSQL).
- [ ] Safe execution sandbox for user-submitted Python code.
- [ ] Export / Import workflows as portable JSON.
- [ ] Headless execution CLI and production Docker containerization.
