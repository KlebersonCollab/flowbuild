# Plan: Database Query Component (ADR 0028)

## 1. Problem Statement & Motivation
Workflows in FlowBuild frequently require interacting with relational databases to fetch operational records, persist workflow outcomes, update business entities, and inspect system state.

Currently, executing database operations requires custom scripting in `PythonScriptComponent`, introducing duplicate connection logic, lack of type validation, and heightened security risks (e.g. SQL injection if parameters are not escaped).

The `DatabaseQueryComponent` introduces a native, declarative, and parameterized SQL query execution node for FlowBuild workflows.

## 2. Scope & Boundaries
- **In Scope**:
  - Implement `DatabaseQueryComponent` in `backend/src/backend/app/components/builtins/actions.py` and register in `backend/src/backend/app/components/builtins/__init__.py`.
  - Configurable inputs: `connection_string` (optional, falls back to `db_manager.engine`), `query` (raw SQL text), `params` (bound parameter dictionary), `fetch_mode` (`"all"`, `"one"`, `"none"`), `auto_commit` (boolean).
  - Outputs: `data` (list of dicts, single dict, or empty list), `row_count` (int), `columns` (list of column names).
  - Safe parameterized query execution with `sqlalchemy.text` and parameters dict to prevent SQL injection.
  - Asynchronous thread offloading via `asyncio.to_thread` to preserve event loop responsiveness.
  - UI integration in `CustomNode.vue` and `ComponentPalette.vue` using `Database` icon and Teal / Storage styling.
  - Comprehensive unit and integration tests in backend and frontend.
- **Out of Scope**:
  - Visual graphical query builders or ORM schema designers (which belong to a future visual SQL builder).
  - NoSQL / MongoDB engines (covered by future dedicated components).

## 3. High-Level Approach
- Follow strict SDD lifecycle: plan -> BDD spec -> atomic 7-column tasks -> TDD test suite -> component implementation -> frontend integration -> sensor audits -> verdict.

## 4. Dependencies & Prerequisites
- SQLAlchemy 2.0 (already installed and powering FlowBuild).
- `asyncio.to_thread` for non-blocking execution.
- `lucide-vue-next` (has `Database` icon).

## 5. Architectural Decision Records (ADRs)
- Relates to [ADR 0028: Database Query Component for SQL Execution and Storage](../../project/ADRs/0028-database-query-component.md).
