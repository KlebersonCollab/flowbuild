# Technical Map & Codebase Synthesis (FlowBuild)

## 1. Executive Summary

FlowBuild is an automation workflow builder designed from the ground up to achieve strict architectural decoupling between the **Python Execution Runtime** and the **Vue 3 + TypeScript Visual Builder**, mirroring the core architectural strengths of Langflow while expanding into general automation (webhooks, APIs, scripting, data pipelines, and AI chains).

## 2. Architecture Synthesis

```
Repository Root
├── .agents/                 # AI-SDD Governance, memory graph, skills, and sensors
├── .specs/                  # Spec-Driven Development documentation & ADRs
│   ├── codebase/            # Technical Map, Stack, Conventions, Concerns, Architecture
│   └── project/             # Project Vision, Roadmap, Operational State, ADRs
├── backend/                 # Python Backend (FastAPI + Async DAG Engine)
│   ├── app/
│   │   ├── api/             # REST & SSE route controllers (flows, components, webhooks)
│   │   ├── core/            # Config, exceptions, logging, security
│   │   ├── engine/          # Graph parser, DAG topological sorter, async runner, execution context
│   │   ├── components/      # Component base classes, input/output descriptors, component registry
│   │   │   ├── base.py
│   │   │   ├── inputs.py
│   │   │   ├── registry.py
│   │   │   └── builtins/    # Standard nodes (Triggers, Actions, Logic, AI)
│   │   └── models/          # Pydantic models for Flow, Node, Edge, ExecutionState
│   └── tests/               # Backend test suite (pytest, pytest-asyncio)
└── frontend/                # Vue 3 Frontend (Vite + TypeScript + @vue-flow/core)
    ├── src/
    │   ├── api/             # HTTP & SSE client services
    │   ├── components/      # UI components (Canvas, Palette, Inspector, CustomNode, TopNav)
    │   ├── stores/          # Pinia stores (flowStore, registryStore, executionStore)
    │   ├── types/           # TypeScript interfaces matching backend JSON schemas
    │   └── assets/          # Tailwind styling conforming to DESIGN.md
    └── tests/               # Frontend unit & component tests (Vitest)
```

## 3. Technology Matrix

| Layer | Primary Technology | Key Packages | Role / Responsibility |
|---|---|---|---|
| **Backend Runtime** | Python 3.11+ | UV, FastAPI, Uvicorn, Pydantic v2, httpx, asyncio | Component reflection, DAG execution, Webhooks, SSE |
| **Frontend Visual** | Vue 3 + TypeScript | Vite, `@vue-flow/core`, Pinia, Lucide Vue | Flow canvas, dynamic schema forms, telemetry UI |
| **Design System** | Linear Dark Canvas | Tailwind CSS v3, custom CSS tokens | Implements [DESIGN.md](file:///F:/Projetos/flowbuild/DESIGN.md) (`#010102`, `#5e6ad2`) |
| **Data Contract** | JSON Schema | Standard Flow JSON, Component Schema Catalog | Complete decoupling of frontend and backend |

## 4. Operational Invariants

1. **Zero UI hardcoding of components**: The frontend queries `GET /api/v1/components` and dynamically renders inputs, outputs, and property inspectors.
2. **Headless Execution**: The backend executes flows triggered by webhooks or API requests without any frontend involvement.
3. **Deterministic DAG ordering**: Every workflow is topological sorted and validated for cycles prior to execution.
4. **Asynchronous Parallelism**: Unconnected branches run concurrently with `asyncio`.
5. **Design Tokens Invariance**: The frontend canvas and chrome strictly honor the Linear Dark theme tokens defined in `DESIGN.md`.
