# ADR 0028: Database Query Component for SQL Execution and Storage

## Status
Accepted

## Date
2026-10-07

## Context
Workflows in FlowBuild frequently require interacting with relational databases to fetch operational data, persist processed results, log metrics, or query application states.

Currently, database interactions require custom code in `PythonScriptComponent` with manual connection string handling, manual driver imports, and repetitive boilerplate.

A dedicated `DatabaseQueryComponent` provides native, declarative SQL execution directly within FlowBuild workflows, supporting:
1. Queries against the built-in FlowBuild database engine (`SQLite` / `PostgreSQL` via `db_manager.engine`) or any custom external SQLAlchemy-supported database connection string.
2. Parameterized SQL queries using `text(query)` with dictionary parameter binding (`:param_name`), preventing SQL injection attacks while seamlessly accepting dynamic values from upstream nodes.
3. Configurable result modes (`"all"`, `"one"`, `"none"`) to support both `SELECT` queries returning serialized row collections and mutation operations (`INSERT`, `UPDATE`, `DELETE`, `CREATE TABLE`) returning affected row metrics.
4. Non-blocking asynchronous execution via `asyncio.to_thread` to maintain event loop performance during blocking database I/O.

## Decision
1. **Component Design (`DatabaseQueryComponent`)**:
   - Class name: `DatabaseQueryComponent`
   - Display name: `"Database Query"`
   - Category: `"Storage"`
   - Description: `"Executes parameterized SQL queries against SQLite, PostgreSQL, or external databases using SQLAlchemy."`
   - Icon: `"database"`
2. **Inputs**:
   - `connection_string` (`StrInput`, default=""): Optional database connection URL (e.g. `sqlite:///custom.db`, `postgresql://user:pass@host/db`). When empty, uses FlowBuild's active database engine (`db_manager.engine`).
   - `query` (`CodeInput` / `StrInput`, required=True, default="SELECT 1 as result"): Raw SQL statement with `:name` style parameter placeholders.
   - `params` (`DictInput`, default={}): Key-value dictionary of parameter bindings mapped to SQL placeholders.
   - `fetch_mode` (`SelectInput`, options=`["all", "one", "none"]`, default=`"all"`): Row fetching behavior (`"all"`: list of dicts, `"one"`: first row as dict or None, `"none"`: mutation without row fetch).
   - `auto_commit` (`BoolInput`, default=True): Automatically commit transaction on mutation queries.
3. **Outputs**:
   - `data` (`Output`, type="any"): Query result rows (list of row mappings for `"all"`, single row mapping for `"one"`, or empty list for `"none"`).
   - `row_count` (`Output`, type="int"): Number of returned rows for SELECT, or affected row count for mutations (`rowcount`).
   - `columns` (`Output`, type="list"): List of column names in the result set (empty list for mutations).
4. **Execution Semantics & Resilience**:
   - Thread isolation: Database execution runs inside `asyncio.to_thread` to avoid blocking the FastAPI event loop.
   - Connection caching & lifecycle: Default queries reuse `db_manager.engine`; custom connection strings dynamically create a cached or ephemeral engine.
   - SQL Injection protection: Queries are compiled with `sqlalchemy.text` and parameters are strictly passed through SQLAlchemy's parameterized binding mechanisms.
   - Error handling: Catches `SQLAlchemyError` exceptions and raises informative exceptions capturing the error reason.
5. **Frontend Canvas & Palette Integration**:
   - Palette & Canvas: Register `DatabaseQueryComponent` under category `"Storage"`.
   - Visual mapping: Uses `Database` icon from `lucide-vue-next` with Teal / Storage styling (`text-teal-400 bg-teal-500/10 border-teal-500/30`, badge `bg-teal-500/15 text-teal-300 border-teal-500/30`, dot `bg-teal-400`).

## Consequences
- **Positive**: Native, injection-safe SQL query execution directly on the canvas without custom Python scripts.
- **Flexibility**: Works instantly with zero setup on the local SQLite/Postgres FlowBuild database, or connects to external databases with a standard connection string.
- **Safety**: Safe parameterized binding prevents SQL injection; thread offloading prevents event loop starvation.
- **Backwards Compatibility**: 100% additive; no breaking changes.
