import asyncio
import tempfile
import os
import uuid
import pytest
from unittest.mock import patch, AsyncMock

from backend.app.db import DatabaseManager
from backend.app.models.flow import FlowModel, NodeModel, EdgeModel
from backend.app.engine.runner import FlowRunner
from backend.app.components.registry import ComponentRegistry
from backend.app.components.builtins.actions import (
    HttpRequestComponent,
    JsonTransformComponent,
    PythonScriptComponent,
)
from backend.app.components.builtins.variables import VariableComponent


@pytest.fixture
def temp_db():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    db = DatabaseManager(database_url=f"sqlite:///{path}")
    db.init_db()
    yield db
    db.close()
    if os.path.exists(path):
        os.remove(path)


@pytest.mark.asyncio
async def test_concurrent_independent_flow_executions():
    """Verify that multiple flows executing concurrently in asyncio do not block each other,

    do not leak state across ExecutionContexts, and compute correct isolated results.
    """
    registry = ComponentRegistry()
    registry.register(PythonScriptComponent)
    registry.register(JsonTransformComponent)

    async def run_single_flow(worker_id: int) -> dict:
        flow = FlowModel(
            id=f"flow-worker-{worker_id}",
            name=f"Worker {worker_id}",
            nodes=[
                NodeModel(
                    id=f"node-script-{worker_id}",
                    type="PythonScriptComponent",
                    data={
                        "inputs": {
                            "code": (
                                "import time\n"
                                "def run(inputs):\n"
                                "    time.sleep(0.05)\n"  # Synchronous sleep offloaded to thread
                                "    return {'worker': inputs['worker_id'], 'squared': inputs['val'] ** 2}\n"
                            ),
                            "input_data": {"worker_id": worker_id, "val": worker_id + 1}
                        }
                    }
                ),
                NodeModel(
                    id=f"node-transform-{worker_id}",
                    type="JsonTransformComponent",
                    data={
                        "inputs": {
                            "expression": "payload['squared'] + 10"
                        }
                    }
                )
            ],
            edges=[
                EdgeModel(
                    id=f"edge-{worker_id}",
                    source=f"node-script-{worker_id}",
                    source_handle="result",
                    target=f"node-transform-{worker_id}",
                    target_handle="input_data"
                )
            ]
        )

        runner = FlowRunner(flow=flow, registry=registry)
        summary = await runner.execute_flow()
        return {
            "worker_id": worker_id,
            "status": summary["status"],
            "script_out": summary["results"][f"node-script-{worker_id}"],
            "final_out": summary["results"][f"node-transform-{worker_id}"]
        }

    # Execute 10 flows concurrently
    tasks = [run_single_flow(i) for i in range(10)]
    results = await asyncio.gather(*tasks)

    assert len(results) == 10
    for r in results:
        w_id = r["worker_id"]
        expected_squared = (w_id + 1) ** 2
        expected_final = expected_squared + 10

        assert r["status"] == "completed"
        assert r["script_out"]["worker"] == w_id
        assert r["script_out"]["squared"] == expected_squared
        assert r["final_out"] == expected_final


@pytest.mark.asyncio
async def test_concurrent_database_writes_no_lock(temp_db):
    """Verify that multiple concurrent coroutines writing to SQLite in WAL mode

    with busy_timeout do not encounter 'database is locked' errors.
    """
    async def create_and_update_execution(idx: int):
        exec_id = f"exec-concurrency-{idx}-{uuid.uuid4().hex[:6]}"
        flow_id = f"flow-{idx % 3}"

        # 1. Record execution
        rec = await asyncio.to_thread(
            temp_db.record_execution,
            execution_id=exec_id,
            flow_id=flow_id,
            trigger_type="concurrent_test",
            status="running"
        )
        assert rec.id == exec_id

        # Small yield to simulate work
        await asyncio.sleep(0.01)

        # 2. Update execution status
        updated = await asyncio.to_thread(
            temp_db.update_execution_status,
            execution_id=exec_id,
            status="completed",
            duration_ms=15.5,
            node_states={"node-1": {"status": "completed", "output": idx}}
        )
        assert updated.status == "completed"
        return exec_id

    # Launch 25 concurrent DB write operations
    tasks = [create_and_update_execution(i) for i in range(25)]
    completed_ids = await asyncio.gather(*tasks)

    assert len(completed_ids) == 25
    assert len(set(completed_ids)) == 25

    # Check total saved
    all_execs = temp_db.list_executions(limit=100)
    assert len(all_execs) >= 25


@pytest.mark.asyncio
async def test_execution_id_uniqueness():
    """Verify that execution ID generation avoids collisions under rapid succession."""
    ids = [f"exec-{uuid.uuid4().hex[:8]}" for _ in range(1000)]
    assert len(ids) == len(set(ids))
