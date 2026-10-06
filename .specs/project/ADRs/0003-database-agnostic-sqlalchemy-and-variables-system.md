# ADR 0003: Database-Agnostic SQLAlchemy (SQLite/PostgreSQL), Variables System and Canvas Auto-Persistence

## Status
Accepted

## Context
FlowBuild currently uses SQLite via `sqlite3` for local persistence. The user needs:
1. Support for both SQLite (default zero-config local) and PostgreSQL (for scalable production deployments) using an agnostic database engine.
2. Canvas node position persistence: when moving or configuring nodes, the `{x, y}` positions must be persistently saved so reloading or switching flows preserves the visual layout.
3. A comprehensive Variables Management system:
   - **Global Variables**: System-wide configuration accessible by any flow (e.g. shared domain, common tokens).
   - **Flow Variables**: Scoped exclusively to a specific flow (e.g. flow-specific endpoint, environment flag).
   - Variables must be usable both as a standalone canvas node (`VariableComponent`) and through automatic string template interpolation (e.g. `{{BASE_URL}}` or `{{API_KEY}}`) in any node's inputs.

## Decision
1. **Database-Agnostic Engine (SQLAlchemy Core/ORM)**:
   - Implement `DatabaseEngine` in `backend/app/db.py` powered by SQLAlchemy 2.0.
   - Default connection string: `DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///flowbuild.db")`.
   - Supports SQLite (`sqlite:///...`) and PostgreSQL (`postgresql://...` or `postgresql+psycopg://...`) seamlessly without code modifications.
   - Tables managed via SQLAlchemy metadata:
     - `flows`: `id`, `name`, `description`, `is_active`, `flow_data` (JSON), `created_at`, `updated_at`.
     - `executions`: `id`, `flow_id`, `trigger_type`, `status`, `started_at`, `completed_at`, `duration_ms`, `error_message`, `node_states` (JSON), `initial_payload` (JSON).
     - `variables`: `id`, `key`, `value`, `scope` ('global' | 'flow'), `flow_id`, `is_secret`, `created_at`, `updated_at`.
2. **Variables System & Resolution**:
   - Variable Hierarchy: Flow variables override Global variables of the same key.
   - Resolution engine in `FlowRunner`:
     - Injects resolved variable map into execution context.
     - Performs recursive string template substitution for `{{VAR_NAME}}`, `{{global.VAR}}`, `{{flow.VAR}}` across all node inputs before execution.
   - `VariableComponent`: Built-in component outputting variable value directly to handle connections.
3. **Canvas Auto-Persistence**:
   - In Vue 3 frontend (`FlowCanvas.vue`), hook into `@node-drag-stop`.
   - Debounced auto-save mechanism (`saveFlowToBackend()`) guarantees node coordinates `{x, y}` are permanently persisted to the database on drag completion.
4. **Variables Management UI**:
   - Add "Variáveis" Modal in frontend (`VariablesModal.vue`) with tabs for Globais and Do Fluxo, supporting full CRUD, scope selection, and secret masking.

## Consequences
- **Positive**:
  - Full PostgreSQL compatibility for cloud and production environments with zero code drift from local development.
  - No more lost canvas layouts on drag.
  - Reusability of tokens and URLs through scoped variables and dynamic `{{VAR}}` interpolation.
- **Negative / Considerations**:
  - PostgreSQL usage in production requires installing driver (`psycopg[binary]`), which can be installed on demand when deploying with Postgres.
