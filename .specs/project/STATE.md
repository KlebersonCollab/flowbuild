# Project State & Context (FlowBuild)

## 🏁 Session Status
- **Current Task**: Architectural analysis of Langflow and design of decoupled Python + Vue 3/TS workflow builder.
- **Progress**: 25% (Architecture and specification baseline established).
- **Next Steps**: Validate architectural blueprint with user, initialize backend core structure and frontend scaffolding.

## 💡 Decisions Log
- **2026-10-05 - Decoupled Architecture**: Selected Python FastAPI backend with an independent Vue 3 + TypeScript frontend communicating via REST and Server-Sent Events (SSE), adopting Langflow's dynamic schema-driven component model.
- **2026-10-05 - Package Manager**: Adopted `uv` as the official Python package and virtual environment manager for maximum dependency resolution speed and reproducibility with `pyproject.toml`.
- **2026-10-05 - Canvas Library**: Selected `@vue-flow/core` for the frontend canvas to match the capabilities of React Flow used in Langflow.
- **2026-10-05 - UI Styling**: Strict adherence to [DESIGN.md](file:///F:/Projetos/flowbuild/DESIGN.md) (Linear dark system, canvas `#010102`, lavender accent `#5e6ad2`).

## 🚧 Active Blockers
- None.

## ❄️ Deferred Ideas / Icebox
- Distributed Celery/Redis worker cluster for massive parallel automation jobs (Milestone 4+).
- Visual debugging breakpoints with step-by-step resume.

## ⚠️ Known Technical Debts
- None (Greenfield project).
