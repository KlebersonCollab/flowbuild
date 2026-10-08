# Specification: Database Query Component (ADR 0028)

## 1. User Stories
- **US-1**: As a workflow creator, I want to execute parameterized SQL `SELECT` queries against SQLite or PostgreSQL databases and receive rows as JSON dictionaries, so that subsequent nodes can process, filter, or notify with the returned data.
- **US-2**: As an automation engineer, I want to execute SQL mutations (`INSERT`, `UPDATE`, `DELETE`, `CREATE TABLE`) and obtain the affected `row_count` so that I can verify data ingestion without fetching heavy rows.
- **US-3**: As a security-conscious engineer, I want parameter binding via `:param` placeholders so that queries are immune to SQL injection attacks even when consuming dynamic inputs from upstream nodes.

## 2. Business Rules & Invariants
- **BR-1**: In `fetch_mode = "all"`:
  - Executes query and fetches all matching rows.
  - Output `data` is `list[dict[str, Any]]` where each row is a mapping from column name to value.
  - `row_count` is the length of `data`.
  - `columns` is the list of column names in the result cursor.
- **BR-2**: In `fetch_mode = "one"`:
  - Executes query and fetches the first row.
  - Output `data` is `dict[str, Any]` (or `None` if no matching rows).
  - `row_count` is 1 if a row was found, else 0.
  - `columns` is the list of column names.
- **BR-3**: In `fetch_mode = "none"`:
  - Executes query (typically DDL or DML: `INSERT`, `UPDATE`, `DELETE`).
  - Output `data` is empty list `[]`.
  - `row_count` is the cursor `rowcount` (number of affected rows).
  - `columns` is empty list `[]`.
- **BR-4**: Parameter binding:
  - Parameters passed in `params` dict are safely bound via `sqlalchemy.text(query)` execution.
  - No string concatenation or unsafe SQL interpolation is used for values.
- **BR-5**: Connection resolution:
  - If `connection_string` is empty or omitted, queries run against FlowBuild's configured database engine (`db_manager.engine`).
  - If a valid `connection_string` is provided, a dedicated connection is opened against that target database and closed upon completion.
- **BR-6**: Non-blocking concurrency:
  - Database execution runs in an isolated thread worker via `asyncio.to_thread` to prevent blocking the event loop.

## 3. Acceptance Criteria (BDD)

### Happy Path (Success Scenarios)
- **AC-1: Execute SELECT Query with Fetch Mode All**
  - **Given** an SQLite database with table `users` containing 2 rows (`Alice`, `Bob`)
  - **When** executing `query = "SELECT id, name FROM users ORDER BY id"` with `fetch_mode = "all"`
  - **Then** output `data` has length 2, `data[0]["name"] == "Alice"`, `row_count == 2`, and `columns == ["id", "name"]`.

- **AC-2: Execute SELECT Query with Bound Parameters**
  - **Given** table `users` with names `Alice` and `Bob`
  - **When** executing `query = "SELECT id, name FROM users WHERE name = :name"` with `params = {"name": "Bob"}` and `fetch_mode = "one"`
  - **Then** output `data["name"] == "Bob"`, `row_count == 1`, and `columns == ["id", "name"]`.

- **AC-3: Execute INSERT and UPDATE Mutation with Fetch Mode None**
  - **Given** table `logs`
  - **When** executing `INSERT INTO logs (message) VALUES (:msg)` with `params = {"msg": "hello"}` and `fetch_mode = "none"`
  - **Then** `row_count == 1` and `data == []`.

- **AC-4: Use Default FlowBuild Database when Connection String is Empty**
  - **Given** `connection_string = ""`
  - **When** executing `SELECT count(*) as total FROM flows`
  - **Then** query executes against `db_manager.engine` and returns the flow count without error.

### Edge Cases & Exceptions (Resilience)
- **AC-5: Query Yielding Zero Rows in Fetch Mode One**
  - **Given** `query = "SELECT * FROM users WHERE name = :name"` with `params = {"name": "NonExistent"}` and `fetch_mode = "one"`
  - **When** the component executes
  - **Then** output `data` is `None`, `row_count == 0`, and no exception is thrown.

- **AC-6: Malformed SQL Syntax Graceful Handling**
  - **Given** `query = "SELECT INVALID SYNTAX FROM"`
  - **When** the component executes
  - **Then** a descriptive `ValueError` or `RuntimeError` is raised indicating query syntax failure.

## 4. Test Data & Boundary Matrix
| Parameter / Field | Valid Inputs (Happy) | Invalid / Boundary Inputs (Edge) |
|---|---|---|
| `connection_string` | `""`, `"sqlite:///:memory:"` | invalid URI format |
| `query` | `"SELECT 1"`, `"INSERT INTO ..."` | `""`, malformed SQL syntax |
| `params` | `{"id": 1, "status": "active"}` | `{}`, `None` |
| `fetch_mode` | `"all"`, `"one"`, `"none"` | unknown string (defaults to `"all"`) |
| `auto_commit` | `True`, `False` | `None` |

## 5. Verification Sensors
| Sensor | Command / Target | Success Threshold |
|---|---|---|
| Pytest Unit & Integration | `backend/.venv/Scripts/pytest backend/tests/test_database_query.py` | 100% pass (6+ tests) |
| Full Pytest Suite | `backend/.venv/Scripts/pytest backend/tests/` | 100% pass (138+ tests) |
| Vitest Frontend Suite | `npx vitest run tests/database_query.test.ts` | 100% pass (4+ tests) |
| Frontend Typecheck & Build | `npm run build` | Clean exit 0 |
| Pre-Commit Spec Drift Sensor | `node .agents/scripts/check-spec-drift.js` | 0 drift detected |
| SDD Integrity Sensor | `node .agents/scripts/verify-sdd-integrity.js` | 100% integrity |
