# Project State & Context (FlowBuild)

## 🏁 Session Status
- **Current Task**: Automation Engine Suite (HTTP Auth, IfCondition logic node, Cron triggers & background scheduler, SQLite persistence, Flow CRUD, Webhooks, Execution History, and Freeze vs Unfreeze replay) completed and verified with 100% test pass rate across backend and frontend.
- **Progress**: 95% (Production-ready automation engine with visual builder, background execution, audit history, and resilient disaster recovery).
- **Next Steps**: Expand custom components catalog (DB query connectors, AI LLM agent nodes).

## 💡 Decisions Log
- **2026-10-05 - Decoupled Architecture**: Selected Python FastAPI backend with an independent Vue 3 + TypeScript frontend communicating via REST and Server-Sent Events (SSE), adopting Langflow's dynamic schema-driven component model.
- **2026-10-05 - Package Manager**: Adopted `uv` as the official Python package and virtual environment manager for maximum dependency resolution speed and reproducibility with `pyproject.toml`.
- **2026-10-05 - Canvas Library**: Selected `@vue-flow/core` and `@vue-flow/minimap` for the frontend canvas to match the capabilities of React Flow used in Langflow.
- **2026-10-05 - UI Styling**: Strict adherence to [DESIGN.md](file:///F:/Projetos/flowbuild/DESIGN.md) (Linear dark system, canvas `#010102`, lavender accent `#5e6ad2`, `@tailwindcss/vite` compiler).
- **2026-10-05 - Live Telemetry & Console**: Implemented `ExecutionDrawer.vue` for real-time SSE streaming logs, execution durations, node output inspection, and canonical JSON export/import.
- **2026-10-05 - ADR 0002 (Persistence, Crons, History & Retry)**: Implemented SQLite database in WAL mode, independent CronSchedulerService via `croniter`, Webhook router matching, and DAG replay engine with Freeze (skip successful upstream calls) and Unfreeze (fresh restart).

## 🚧 Active Blockers
- None.

## ❄️ Deferred Ideas / Icebox
- Distributed Celery/Redis worker cluster for massive parallel automation jobs (Milestone 4+).
- Visual debugging breakpoints with step-by-step resume.

## ⚠️ Known Technical Debts
- None (Greenfield project).
