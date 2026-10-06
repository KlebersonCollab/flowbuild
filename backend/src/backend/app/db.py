import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Any, Generator

from backend.app.models.flow import ExecutionRecord, FlowRecord


class DatabaseManager:
    def __init__(self, db_path: str = "flowbuild.db"):
        self.db_path = db_path

    @contextmanager
    def _connection(self) -> Generator[sqlite3.Connection, None, None]:
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL;")
        try:
            yield conn
        finally:
            conn.close()

    def init_db(self) -> None:
        with self._connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS flows (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT DEFAULT '',
                    is_active INTEGER DEFAULT 1,
                    flow_data TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS executions (
                    id TEXT PRIMARY KEY,
                    flow_id TEXT NOT NULL,
                    trigger_type TEXT DEFAULT 'manual',
                    status TEXT DEFAULT 'running',
                    started_at TEXT NOT NULL,
                    completed_at TEXT,
                    duration_ms REAL DEFAULT 0.0,
                    error_message TEXT,
                    node_states TEXT NOT NULL,
                    initial_payload TEXT DEFAULT '{}'
                );
            """)
            conn.commit()

    def create_flow(
        self,
        flow_data: dict[str, Any],
        is_active: bool = True,
    ) -> FlowRecord:
        now = datetime.now(timezone.utc).isoformat()
        flow_id = flow_data.get("id") or f"flow-{int(datetime.now().timestamp())}"
        name = flow_data.get("name", "Untitled Flow")
        description = flow_data.get("description", "")

        with self._connection() as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO flows (id, name, description, is_active, flow_data, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    flow_id,
                    name,
                    description,
                    1 if is_active else 0,
                    json.dumps(flow_data),
                    now,
                    now,
                ),
            )
            conn.commit()

        return FlowRecord(
            id=flow_id,
            name=name,
            description=description,
            is_active=is_active,
            flow_data=flow_data,
            created_at=now,
            updated_at=now,
        )

    def get_flow(self, flow_id: str) -> FlowRecord | None:
        with self._connection() as conn:
            row = conn.execute("SELECT * FROM flows WHERE id = ?", (flow_id,)).fetchone()
            if not row:
                return None
            return FlowRecord(
                id=row["id"],
                name=row["name"],
                description=row["description"] or "",
                is_active=bool(row["is_active"]),
                flow_data=json.loads(row["flow_data"]),
                created_at=row["created_at"],
                updated_at=row["updated_at"],
            )

    def list_flows(self, active_only: bool = False) -> list[FlowRecord]:
        query = "SELECT * FROM flows"
        params: list[Any] = []
        if active_only:
            query += " WHERE is_active = 1"
        query += " ORDER BY updated_at DESC"

        results: list[FlowRecord] = []
        with self._connection() as conn:
            rows = conn.execute(query, params).fetchall()
            for row in rows:
                results.append(
                    FlowRecord(
                        id=row["id"],
                        name=row["name"],
                        description=row["description"] or "",
                        is_active=bool(row["is_active"]),
                        flow_data=json.loads(row["flow_data"]),
                        created_at=row["created_at"],
                        updated_at=row["updated_at"],
                    )
                )
        return results

    def update_flow(
        self,
        flow_id: str,
        flow_data: dict[str, Any],
        is_active: bool | None = None,
    ) -> FlowRecord | None:
        existing = self.get_flow(flow_id)
        if not existing:
            return None

        now = datetime.now(timezone.utc).isoformat()
        name = flow_data.get("name", existing.name)
        description = flow_data.get("description", existing.description)
        active_val = existing.is_active if is_active is None else is_active

        with self._connection() as conn:
            conn.execute(
                """
                UPDATE flows
                SET name = ?, description = ?, is_active = ?, flow_data = ?, updated_at = ?
                WHERE id = ?
                """,
                (
                    name,
                    description,
                    1 if active_val else 0,
                    json.dumps(flow_data),
                    now,
                    flow_id,
                ),
            )
            conn.commit()

        return self.get_flow(flow_id)

    def delete_flow(self, flow_id: str) -> bool:
        with self._connection() as conn:
            cur = conn.execute("DELETE FROM flows WHERE id = ?", (flow_id,))
            conn.commit()
            return cur.rowcount > 0

    def record_execution(
        self,
        execution_id: str,
        flow_id: str,
        trigger_type: str = "manual",
        status: str = "running",
        node_states: dict[str, Any] | None = None,
        initial_payload: dict[str, Any] | None = None,
    ) -> ExecutionRecord:
        now = datetime.now(timezone.utc).isoformat()
        node_states_json = json.dumps(node_states or {})
        initial_payload_json = json.dumps(initial_payload or {})

        with self._connection() as conn:
            conn.execute(
                """
                INSERT INTO executions (
                    id, flow_id, trigger_type, status, started_at,
                    node_states, initial_payload
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    execution_id,
                    flow_id,
                    trigger_type,
                    status,
                    now,
                    node_states_json,
                    initial_payload_json,
                ),
            )
            conn.commit()

        return ExecutionRecord(
            id=execution_id,
            flow_id=flow_id,
            trigger_type=trigger_type,
            status=status,
            started_at=now,
            node_states=node_states or {},
            initial_payload=initial_payload or {},
        )

    def update_execution_status(
        self,
        execution_id: str,
        status: str,
        duration_ms: float = 0.0,
        error_message: str | None = None,
        node_states: dict[str, Any] | None = None,
    ) -> ExecutionRecord:
        now = datetime.now(timezone.utc).isoformat()

        with self._connection() as conn:
            if node_states is not None:
                conn.execute(
                    """
                    UPDATE executions
                    SET status = ?, completed_at = ?, duration_ms = ?, error_message = ?, node_states = ?
                    WHERE id = ?
                    """,
                    (
                        status,
                        now,
                        duration_ms,
                        error_message,
                        json.dumps(node_states),
                        execution_id,
                    ),
                )
            else:
                conn.execute(
                    """
                    UPDATE executions
                    SET status = ?, completed_at = ?, duration_ms = ?, error_message = ?
                    WHERE id = ?
                    """,
                    (
                        status,
                        now,
                        duration_ms,
                        error_message,
                        execution_id,
                    ),
                )
            conn.commit()

        return self.get_execution(execution_id)  # type: ignore

    def get_execution(self, execution_id: str) -> ExecutionRecord | None:
        with self._connection() as conn:
            row = conn.execute("SELECT * FROM executions WHERE id = ?", (execution_id,)).fetchone()
            if not row:
                return None
            return ExecutionRecord(
                id=row["id"],
                flow_id=row["flow_id"],
                trigger_type=row["trigger_type"],
                status=row["status"],
                started_at=row["started_at"],
                completed_at=row["completed_at"],
                duration_ms=row["duration_ms"] or 0.0,
                error_message=row["error_message"],
                node_states=json.loads(row["node_states"]),
                initial_payload=json.loads(row["initial_payload"] or "{}"),
            )

    def list_executions(
        self,
        flow_id: str | None = None,
        limit: int = 50,
    ) -> list[ExecutionRecord]:
        query = "SELECT * FROM executions"
        params: list[Any] = []
        if flow_id:
            query += " WHERE flow_id = ?"
            params.append(flow_id)
        query += " ORDER BY started_at DESC LIMIT ?"
        params.append(limit)

        results: list[ExecutionRecord] = []
        with self._connection() as conn:
            rows = conn.execute(query, params).fetchall()
            for row in rows:
                results.append(
                    ExecutionRecord(
                        id=row["id"],
                        flow_id=row["flow_id"],
                        trigger_type=row["trigger_type"],
                        status=row["status"],
                        started_at=row["started_at"],
                        completed_at=row["completed_at"],
                        duration_ms=row["duration_ms"] or 0.0,
                        error_message=row["error_message"],
                        node_states=json.loads(row["node_states"]),
                        initial_payload=json.loads(row["initial_payload"] or "{}"),
                    )
                )
        return results


# Global singleton instance for the app
db_manager = DatabaseManager()
