# Project State & Context (FlowBuild)

## 🏁 Session Status
- **Current Task**: Mandatory Trigger Node Requirement for Workflow Execution (ADR 0006) completed and verified with 100% test pass rate across backend (43/43 pytest) and frontend (24/24 vitest + clean build).
- **Progress**: 100% (Trigger node validation guard on Run Flow button, execution drawer warning log, backend runtime guard in FlowRunner and /execute/stream, 100% test pass rate).
- **Next Steps**: Expand custom components catalog (DB query connectors, AI LLM agent nodes).

## 💡 Decisions Log
- **2026-10-06 - ADR 0006 (Mandatory Trigger Node Requirement)**: Enforced that workflow execution must originate from an initial trigger node (Manual, Webhook, Cron). Blocked headless execution in frontend (`TopNav.vue` & `flowStore.ts`) with clear UI warnings and console logs, and enforced runtime guard in backend `FlowRunner` and `/api/v1/flows/execute/stream`.
- **2026-10-06 - ADR 0005 (Reactivity, Draft Lifecycle & Lineage Sync)**: Implemented 100% reactive canvas auto-save on any node drag/input change without version bumping, draft state (`is_draft = true`, `is_active = false`) preventing premature execution of unfinished flows, explicit version/subversion bumping on "Salvar o Fluxo atual" (`v1.0.0` -> `v1.0.1`), draft guards on activation and promotion, and bidirectional cross-environment lineage resolution in `setEnvironment` preventing duplicate `-qa` flows in DEV.
- **2026-10-06 - ADR 0004 (Folders & Multi-Environment Promotion Pipeline)**: Implemented `folder` classification and multi-environment promotion pipeline (`dev` -> `qa` -> `prd`) with version tagging (`v1.0.0` -> `v1.1.0`), lineage tracking (`source_flow_id`), and 4-tier environment-aware variable resolution hierarchy in `FlowRunner` and `db_manager`. Added TopNav environment switcher with Linear Dark badges, FlowsModal folder pills and promotion buttons, and VariablesModal environment selector.
- **2026-10-06 - ADR 0003 (Database-Agnostic Engine & Variables System)**: Replaced raw sqlite3 with SQLAlchemy 2.0 supporting SQLite by default (`flowbuild.db`) and PostgreSQL via `DATABASE_URL`. Implemented scoped variables (`global` vs `flow`), string template interpolation `{{KEY}}` across all components in `FlowRunner`, dedicated `VariableComponent`, `VariablesModal.vue` UI, and canvas node drag auto-persistence with debounced sync.
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
