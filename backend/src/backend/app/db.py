import json
import os
import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy import (
    Boolean,
    Column,
    Float,
    MetaData,
    String,
    Table,
    Text,
    create_engine,
    delete,
    insert,
    select,
    update,
)

from backend.app.models.flow import ExecutionRecord, FlowRecord, VariableRecord


class DatabaseManager:
    def __init__(self, database_url: str | None = None, db_path: str | None = None):
        self._db_path = db_path or "flowbuild.db"
        if database_url:
            self.database_url = database_url
        elif db_path:
            self.database_url = f"sqlite:///{db_path}"
        else:
            self.database_url = os.getenv("DATABASE_URL", "sqlite:///flowbuild.db")

        # SQLite-specific connection arguments
        engine_kwargs: dict[str, Any] = {}
        if self.database_url.startswith("sqlite"):
            engine_kwargs["connect_args"] = {"check_same_thread": False, "timeout": 30.0}

        self.engine = create_engine(self.database_url, **engine_kwargs)
        self.metadata = MetaData()

        # Define Schema Tables
        self.flows_table = Table(
            "flows",
            self.metadata,
            Column("id", String(64), primary_key=True),
            Column("name", String(255), nullable=False),
            Column("description", Text, default=""),
            Column("folder", String(64), default="Geral"),
            Column("environment", String(32), default="dev"),
            Column("version", String(32), default="v1.0.0"),
            Column("source_flow_id", String(64), nullable=True),
            Column("is_active", Boolean, default=True),
            Column("is_draft", Boolean, default=False),
            Column("flow_data", Text, nullable=False),
            Column("created_at", String(64), nullable=False),
            Column("updated_at", String(64), nullable=False),
        )

        self.executions_table = Table(
            "executions",
            self.metadata,
            Column("id", String(64), primary_key=True),
            Column("flow_id", String(64), nullable=False),
            Column("trigger_type", String(64), default="manual"),
            Column("status", String(64), default="running"),
            Column("started_at", String(64), nullable=False),
            Column("completed_at", String(64), nullable=True),
            Column("duration_ms", Float, default=0.0),
            Column("error_message", Text, nullable=True),
            Column("node_states", Text, nullable=False),
            Column("initial_payload", Text, default="{}"),
        )

        self.variables_table = Table(
            "variables",
            self.metadata,
            Column("id", String(64), primary_key=True),
            Column("key", String(128), nullable=False),
            Column("value", Text, nullable=False),
            Column("scope", String(32), default="global"),  # 'global' or 'flow'
            Column("flow_id", String(64), nullable=True),
            Column("environment", String(32), default="all"),  # 'dev', 'qa', 'prd', 'all'
            Column("is_secret", Boolean, default=False),
            Column("created_at", String(64), nullable=False),
            Column("updated_at", String(64), nullable=False),
        )

    @property
    def db_path(self) -> str:
        return self._db_path

    @db_path.setter
    def db_path(self, val: str) -> None:
        self._db_path = val
        self.database_url = f"sqlite:///{val}"
        self.engine = create_engine(
            self.database_url,
            connect_args={"check_same_thread": False, "timeout": 30.0},
        )

    def init_db(self) -> None:
        self.metadata.create_all(self.engine)
        if self.database_url.startswith("sqlite"):
            with self.engine.connect() as conn:
                conn.exec_driver_sql("PRAGMA journal_mode=WAL;")
                conn.exec_driver_sql("PRAGMA busy_timeout=30000;")
                
                # Soft schema migration for SQLite
                try:
                    cols_flows = [c[1] for c in conn.exec_driver_sql("PRAGMA table_info(flows);").fetchall()]
                    if cols_flows:
                        if "folder" not in cols_flows:
                            conn.exec_driver_sql("ALTER TABLE flows ADD COLUMN folder VARCHAR(64) DEFAULT 'Geral';")
                        if "environment" not in cols_flows:
                            conn.exec_driver_sql("ALTER TABLE flows ADD COLUMN environment VARCHAR(32) DEFAULT 'dev';")
                        if "version" not in cols_flows:
                            conn.exec_driver_sql("ALTER TABLE flows ADD COLUMN version VARCHAR(32) DEFAULT 'v1.0.0';")
                        if "source_flow_id" not in cols_flows:
                            conn.exec_driver_sql("ALTER TABLE flows ADD COLUMN source_flow_id VARCHAR(64);")
                        if "is_draft" not in cols_flows:
                            conn.exec_driver_sql("ALTER TABLE flows ADD COLUMN is_draft BOOLEAN DEFAULT 0;")
                    
                    cols_vars = [c[1] for c in conn.exec_driver_sql("PRAGMA table_info(variables);").fetchall()]
                    if cols_vars:
                        if "environment" not in cols_vars:
                            conn.exec_driver_sql("ALTER TABLE variables ADD COLUMN environment VARCHAR(32) DEFAULT 'all';")
                except Exception:
                    pass

                conn.commit()

    def close(self) -> None:
        self.engine.dispose()

    # --- FLOW CRUD ---

    def create_flow(
        self,
        flow_data: dict[str, Any],
        is_active: bool = True,
        is_draft: bool | None = None,
    ) -> FlowRecord:
        now = datetime.now(timezone.utc).isoformat()
        flow_id = flow_data.get("id") or f"flow-{uuid.uuid4().hex[:8]}"
        name = flow_data.get("name", "Untitled Flow")
        description = flow_data.get("description", "")
        folder = flow_data.get("folder", "Geral")
        environment = flow_data.get("environment", "dev")
        version = flow_data.get("version", "v1.0.0")
        source_flow_id = flow_data.get("source_flow_id")
        is_draft_val = flow_data.get("is_draft", False) if is_draft is None else is_draft

        # Fail-safe: if saving into dev but ID carries a foreign environment suffix and source_flow_id exists
        if environment == "dev" and source_flow_id and (flow_id.endswith("-qa") or flow_id.endswith("-prd")):
            flow_id = source_flow_id
            source_flow_id = None

        flow_data_persisted = dict(flow_data)
        flow_data_persisted["id"] = flow_id
        flow_data_persisted["folder"] = folder
        flow_data_persisted["environment"] = environment
        flow_data_persisted["version"] = version
        flow_data_persisted["is_draft"] = is_draft_val
        if source_flow_id:
            flow_data_persisted["source_flow_id"] = source_flow_id
        elif "source_flow_id" in flow_data_persisted:
            flow_data_persisted.pop("source_flow_id", None)

        with self.engine.begin() as conn:
            # Delete if exists (UPSERT semantics)
            conn.execute(delete(self.flows_table).where(self.flows_table.c.id == flow_id))
            conn.execute(
                insert(self.flows_table).values(
                    id=flow_id,
                    name=name,
                    description=description,
                    folder=folder,
                    environment=environment,
                    version=version,
                    source_flow_id=source_flow_id,
                    is_active=is_active,
                    is_draft=is_draft_val,
                    flow_data=json.dumps(flow_data_persisted),
                    created_at=now,
                    updated_at=now,
                )
            )

        return FlowRecord(
            id=flow_id,
            name=name,
            description=description,
            folder=folder,
            environment=environment,
            version=version,
            source_flow_id=source_flow_id,
            is_active=is_active,
            is_draft=is_draft_val,
            flow_data=flow_data_persisted,
            created_at=now,
            updated_at=now,
        )

    def get_flow(self, flow_id: str) -> FlowRecord | None:
        with self.engine.connect() as conn:
            stmt = select(self.flows_table).where(self.flows_table.c.id == flow_id)
            row = conn.execute(stmt).mappings().fetchone()
            if not row:
                return None
            return FlowRecord(
                id=row["id"],
                name=row["name"],
                description=row["description"] or "",
                folder=row["folder"] or "Geral",
                environment=row["environment"] or "dev",
                version=row["version"] or "v1.0.0",
                source_flow_id=row["source_flow_id"],
                is_active=bool(row["is_active"]),
                is_draft=bool(row.get("is_draft", False)),
                flow_data=json.loads(row["flow_data"]),
                created_at=row["created_at"],
                updated_at=row["updated_at"],
            )

    def list_flows(
        self,
        active_only: bool = False,
        folder: str | None = None,
        environment: str | None = None,
    ) -> list[FlowRecord]:
        stmt = select(self.flows_table)
        if active_only:
            stmt = stmt.where(self.flows_table.c.is_active.is_(True))
        if folder:
            stmt = stmt.where(self.flows_table.c.folder == folder)
        if environment:
            stmt = stmt.where(self.flows_table.c.environment == environment)
        stmt = stmt.order_by(self.flows_table.c.updated_at.desc())

        results: list[FlowRecord] = []
        with self.engine.connect() as conn:
            rows = conn.execute(stmt).mappings().fetchall()
            for row in rows:
                results.append(
                    FlowRecord(
                        id=row["id"],
                        name=row["name"],
                        description=row["description"] or "",
                        folder=row["folder"] or "Geral",
                        environment=row["environment"] or "dev",
                        version=row["version"] or "v1.0.0",
                        source_flow_id=row["source_flow_id"],
                        is_active=bool(row["is_active"]),
                        is_draft=bool(row.get("is_draft", False)),
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
        folder = flow_data.get("folder", existing.folder)
        environment = flow_data.get("environment", existing.environment)
        version = flow_data.get("version", existing.version)
        source_flow_id = flow_data.get("source_flow_id", existing.source_flow_id)
        active_val = existing.is_active if is_active is None else is_active
        draft_val = flow_data.get("is_draft", existing.is_draft)

        flow_data_persisted = dict(flow_data)
        flow_data_persisted["folder"] = folder
        flow_data_persisted["environment"] = environment
        flow_data_persisted["version"] = version
        flow_data_persisted["is_draft"] = draft_val
        if source_flow_id:
            flow_data_persisted["source_flow_id"] = source_flow_id

        with self.engine.begin() as conn:
            conn.execute(
                update(self.flows_table)
                .where(self.flows_table.c.id == flow_id)
                .values(
                    name=name,
                    description=description,
                    folder=folder,
                    environment=environment,
                    version=version,
                    source_flow_id=source_flow_id,
                    is_active=active_val,
                    is_draft=draft_val,
                    flow_data=json.dumps(flow_data_persisted),
                    updated_at=now,
                )
            )

        return self.get_flow(flow_id)

    def promote_flow(
        self,
        source_flow_id: str,
        target_environment: str,
        target_version: str | None = None,
    ) -> FlowRecord | None:
        source_flow = self.get_flow(source_flow_id)
        if not source_flow:
            return None

        # Determine target version
        if target_version:
            version = target_version
        else:
            try:
                clean = source_flow.version.lstrip("v")
                parts = clean.split(".")
                major = parts[0]
                minor = int(parts[1]) + 1 if len(parts) > 1 else 1
                patch = parts[2] if len(parts) > 2 else "0"
                version = f"v{major}.{minor}.{patch}"
            except Exception:
                version = "v1.1.0"

        # Check if flow already exists in target environment for this source
        with self.engine.connect() as conn:
            stmt = select(self.flows_table).where(
                (self.flows_table.c.source_flow_id == source_flow_id)
                & (self.flows_table.c.environment == target_environment)
            )
            existing_row = conn.execute(stmt).mappings().fetchone()

        target_id = existing_row["id"] if existing_row else f"{source_flow_id}-{target_environment}"

        now = datetime.now(timezone.utc).isoformat()
        flow_data_copy = dict(source_flow.flow_data)
        flow_data_copy["id"] = target_id
        flow_data_copy["name"] = source_flow.name
        flow_data_copy["description"] = source_flow.description
        flow_data_copy["folder"] = source_flow.folder
        flow_data_copy["environment"] = target_environment
        flow_data_copy["version"] = version
        flow_data_copy["source_flow_id"] = source_flow_id

        with self.engine.begin() as conn:
            conn.execute(delete(self.flows_table).where(self.flows_table.c.id == target_id))
            conn.execute(
                insert(self.flows_table).values(
                    id=target_id,
                    name=source_flow.name,
                    description=source_flow.description,
                    folder=source_flow.folder,
                    environment=target_environment,
                    version=version,
                    source_flow_id=source_flow_id,
                    is_active=True,
                    flow_data=json.dumps(flow_data_copy),
                    created_at=existing_row["created_at"] if existing_row else now,
                    updated_at=now,
                )
            )

        return self.get_flow(target_id)

    def delete_flow(self, flow_id: str) -> bool:
        with self.engine.begin() as conn:
            res = conn.execute(delete(self.flows_table).where(self.flows_table.c.id == flow_id))
            return res.rowcount > 0

    # --- EXECUTION HISTORY ---

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

        with self.engine.begin() as conn:
            conn.execute(
                insert(self.executions_table).values(
                    id=execution_id,
                    flow_id=flow_id,
                    trigger_type=trigger_type,
                    status=status,
                    started_at=now,
                    node_states=node_states_json,
                    initial_payload=initial_payload_json,
                )
            )

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
        values: dict[str, Any] = {
            "status": status,
            "completed_at": now,
            "duration_ms": duration_ms,
            "error_message": error_message,
        }
        if node_states is not None:
            values["node_states"] = json.dumps(node_states)

        with self.engine.begin() as conn:
            conn.execute(
                update(self.executions_table)
                .where(self.executions_table.c.id == execution_id)
                .values(**values)
            )

        return self.get_execution(execution_id)  # type: ignore

    def get_execution(self, execution_id: str) -> ExecutionRecord | None:
        with self.engine.connect() as conn:
            stmt = select(self.executions_table).where(self.executions_table.c.id == execution_id)
            row = conn.execute(stmt).mappings().fetchone()
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
        stmt = select(self.executions_table)
        if flow_id:
            stmt = stmt.where(self.executions_table.c.flow_id == flow_id)
        stmt = stmt.order_by(self.executions_table.c.started_at.desc()).limit(limit)

        results: list[ExecutionRecord] = []
        with self.engine.connect() as conn:
            rows = conn.execute(stmt).mappings().fetchall()
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

    # --- VARIABLES CRUD & HIERARCHY RESOLUTION ---

    def create_variable(
        self,
        key: str,
        value: str,
        scope: str = "global",
        flow_id: str | None = None,
        is_secret: bool = False,
        environment: str = "all",
    ) -> VariableRecord:
        now = datetime.now(timezone.utc).isoformat()
        var_id = f"var-{uuid.uuid4().hex[:8]}"

        with self.engine.begin() as conn:
            conn.execute(
                insert(self.variables_table).values(
                    id=var_id,
                    key=key,
                    value=value,
                    scope=scope,
                    flow_id=flow_id if scope == "flow" else None,
                    environment=environment,
                    is_secret=is_secret,
                    created_at=now,
                    updated_at=now,
                )
            )

        return VariableRecord(
            id=var_id,
            key=key,
            value=value,
            scope=scope,
            flow_id=flow_id if scope == "flow" else None,
            environment=environment,
            is_secret=is_secret,
            created_at=now,
            updated_at=now,
        )

    def get_variable(self, var_id: str) -> VariableRecord | None:
        with self.engine.connect() as conn:
            stmt = select(self.variables_table).where(self.variables_table.c.id == var_id)
            row = conn.execute(stmt).mappings().fetchone()
            if not row:
                return None
            return VariableRecord(
                id=row["id"],
                key=row["key"],
                value=row["value"],
                scope=row["scope"],
                flow_id=row["flow_id"],
                environment=row["environment"] or "all",
                is_secret=bool(row["is_secret"]),
                created_at=row["created_at"],
                updated_at=row["updated_at"],
            )

    def list_variables(
        self,
        scope: str | None = None,
        flow_id: str | None = None,
        environment: str | None = None,
    ) -> list[VariableRecord]:
        stmt = select(self.variables_table)
        if scope:
            stmt = stmt.where(self.variables_table.c.scope == scope)
            if scope == "flow" and flow_id:
                stmt = stmt.where(self.variables_table.c.flow_id == flow_id)
        elif flow_id:
            # When flow_id is specified without explicit scope: return global vars AND this flow's vars
            stmt = stmt.where(
                (self.variables_table.c.scope == "global")
                | (
                    (self.variables_table.c.scope == "flow")
                    & (self.variables_table.c.flow_id == flow_id)
                )
            )
        if environment:
            stmt = stmt.where(self.variables_table.c.environment.in_([environment, "all"]))

        stmt = stmt.order_by(self.variables_table.c.key.asc())

        results: list[VariableRecord] = []
        with self.engine.connect() as conn:
            rows = conn.execute(stmt).mappings().fetchall()
            for row in rows:
                results.append(
                    VariableRecord(
                        id=row["id"],
                        key=row["key"],
                        value=row["value"],
                        scope=row["scope"],
                        flow_id=row["flow_id"],
                        environment=row["environment"] or "all",
                        is_secret=bool(row["is_secret"]),
                        created_at=row["created_at"],
                        updated_at=row["updated_at"],
                    )
                )
        return results

    def resolve_variable_value(
        self,
        key: str,
        flow_id: str | None = None,
        environment: str = "dev",
    ) -> str | None:
        """Resolves variable value using 4-tier hierarchy."""
        all_resolved = self.get_all_resolved_variables(flow_id=flow_id, environment=environment)
        return all_resolved.get(key)

    def get_all_resolved_variables(
        self,
        flow_id: str | None = None,
        environment: str = "dev",
    ) -> dict[str, str]:
        """Returns dict of all resolved variables following the 4-tier hierarchy:
        1. Flow-scoped variable for environment
        2. Flow-scoped variable for 'all'
        3. Global variable for environment
        4. Global variable for 'all'
        """
        stmt = select(self.variables_table)
        if flow_id:
            stmt = stmt.where(
                (self.variables_table.c.scope == "global")
                | (
                    (self.variables_table.c.scope == "flow")
                    & (self.variables_table.c.flow_id == flow_id)
                )
            )
        else:
            stmt = stmt.where(self.variables_table.c.scope == "global")

        with self.engine.connect() as conn:
            rows = conn.execute(stmt).mappings().fetchall()

        resolved_map: dict[str, str] = {}

        # 4. Global with environment in ('all', None, '')
        for r in rows:
            if r["scope"] == "global" and (r["environment"] in ("all", None, "")):
                resolved_map[r["key"]] = r["value"]

        # 3. Global with environment == environment
        for r in rows:
            if r["scope"] == "global" and r["environment"] == environment:
                resolved_map[r["key"]] = r["value"]

        # 2. Flow with environment in ('all', None, '')
        if flow_id:
            for r in rows:
                if r["scope"] == "flow" and r["flow_id"] == flow_id and (r["environment"] in ("all", None, "")):
                    resolved_map[r["key"]] = r["value"]

        # 1. Flow with environment == environment (highest priority)
        if flow_id:
            for r in rows:
                if r["scope"] == "flow" and r["flow_id"] == flow_id and r["environment"] == environment:
                    resolved_map[r["key"]] = r["value"]

        return resolved_map

    def update_variable(
        self,
        var_id: str,
        value: str | None = None,
        environment: str | None = None,
        is_secret: bool | None = None,
    ) -> VariableRecord | None:
        existing = self.get_variable(var_id)
        if not existing:
            return None

        now = datetime.now(timezone.utc).isoformat()
        values: dict[str, Any] = {"updated_at": now}
        if value is not None:
            values["value"] = value
        if environment is not None:
            values["environment"] = environment
        if is_secret is not None:
            values["is_secret"] = is_secret

        with self.engine.begin() as conn:
            conn.execute(
                update(self.variables_table)
                .where(self.variables_table.c.id == var_id)
                .values(**values)
            )

        return self.get_variable(var_id)

    def delete_variable(self, var_id: str) -> bool:
        with self.engine.begin() as conn:
            res = conn.execute(delete(self.variables_table).where(self.variables_table.c.id == var_id))
            return res.rowcount > 0

    def upsert_variable(
        self,
        key: str,
        value: str,
        scope: str = "flow",
        flow_id: str | None = None,
        environment: str = "all",
        is_secret: bool = False,
    ) -> VariableRecord:
        now = datetime.now(timezone.utc).isoformat()
        target_flow_id = flow_id if scope == "flow" else None
        target_env = environment or "all"

        stmt = select(self.variables_table).where(
            self.variables_table.c.key == key,
            self.variables_table.c.scope == scope,
        )
        if scope == "flow":
            if target_flow_id is not None:
                stmt = stmt.where(self.variables_table.c.flow_id == target_flow_id)
            else:
                stmt = stmt.where(self.variables_table.c.flow_id.is_(None))
        else:
            stmt = stmt.where(self.variables_table.c.flow_id.is_(None))

        if target_env in ("all", None, ""):
            stmt = stmt.where(
                (self.variables_table.c.environment == "all")
                | (self.variables_table.c.environment.is_(None))
                | (self.variables_table.c.environment == "")
            )
        else:
            stmt = stmt.where(self.variables_table.c.environment == target_env)

        with self.engine.begin() as conn:
            existing = conn.execute(stmt).mappings().fetchone()
            if existing:
                var_id = existing["id"]
                conn.execute(
                    update(self.variables_table)
                    .where(self.variables_table.c.id == var_id)
                    .values(value=value, updated_at=now, is_secret=is_secret)
                )
            else:
                var_id = f"var-{uuid.uuid4().hex[:8]}"
                conn.execute(
                    insert(self.variables_table).values(
                        id=var_id,
                        key=key,
                        value=value,
                        scope=scope,
                        flow_id=target_flow_id,
                        environment=target_env,
                        is_secret=is_secret,
                        created_at=now,
                        updated_at=now,
                    )
                )

        return self.get_variable(var_id)  # type: ignore[return-value]


# Global singleton instance for the app
db_manager = DatabaseManager()
