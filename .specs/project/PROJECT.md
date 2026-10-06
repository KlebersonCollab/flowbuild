# Project Vision & North Star (FlowBuild)

## 1. Vision Statement

**FlowBuild** is a high-performance, modular automation workflow builder inspired by the decoupled architecture of Langflow, tailored for modern automation pipelines (webhooks, APIs, data transforms, and AI agents).

The platform separates the **Python Execution Runtime** (FastAPI, asyncio DAG engine, dynamic component loader) from the **Visual Designer** (Vue 3 + TypeScript + Vite + `@vue-flow/core`), connected through a strict JSON Schema Contract.

## 2. Core Pillars

1. **Decoupled Architecture (The Langflow Model)**:
   - **Backend Independence**: The Python backend can run headlessly as an API worker or webhook consumer in production without the visual UI.
   - **Dynamic Component Schema**: Adding a new automation component requires writing only a Python class. The backend generates JSON schema definitions that the Vue 3 frontend interprets dynamically to construct UI controls and ports.
   - **No Frontend Rebuilds for New Components**: Anyone can author a custom automation node in Python, drop it in the components directory, and it immediately appears on the canvas palette.

2. **Full-Spectrum Automation (Beyond Chat)**:
   - While Langflow focuses heavily on LLM/RAG chains, FlowBuild provides a versatile workflow automation runtime similar to n8n and Zapier, combined with Langflow's Pythonic component ergonomics.
   - Native support for Webhooks, HTTP API clients, Python script sandbox execution, Cron schedulers, Conditional branches (If/Else, Switch), Loops/Iterators, Data transformations, and LLM orchestration.

3. **Modern Vue 3 + TypeScript Frontend**:
   - Built on Vue 3 Composition API (`<script setup>`) and TypeScript.
   - Flow canvas using `@vue-flow/core`.
   - Polished dark UI strictly respecting [DESIGN.md](file:///F:/Projetos/flowbuild/DESIGN.md) (Linear canvas `#010102`, lavender `#5e6ad2`, surface hierarchy).

4. **Execution Performance & Traceability**:
   - Asynchronous DAG execution with topological ordering and branch parallelization.
   - Real-time step-by-step telemetry via Server-Sent Events (SSE) / WebSockets to highlight active nodes, show intermediate output data, and provide step execution logs.

## 3. Target Audience

- **Backend Engineers & Automation Builders**: Wanting to automate workflows, trigger webhooks, query APIs, or chain AI prompts without vendor lock-in.
- **Teams needing a Self-Hosted Workflow Engine**: Needing an extensible, self-contained open-source workflow engine where custom company logic can be added in simple Python modules.
