import pytest
import tempfile
import os
from backend.app.db import DatabaseManager
from backend.app.models import FlowRecord, ExecutionRecord

@pytest.fixture
def temp_db():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    db = DatabaseManager(db_path=path)
    db.init_db()
    yield db
    if os.path.exists(path):
        os.remove(path)

def test_flow_crud_operations(temp_db):
    flow_payload = {
        "id": "flow-test-1",
        "name": "Test Flow",
        "description": "A flow for testing persistence",
        "nodes": [{"id": "n1", "type": "ManualTriggerComponent", "position": {"x": 0, "y": 0}, "data": {}}],
        "edges": []
    }

    # 1. Create flow
    created = temp_db.create_flow(flow_payload, is_active=True)
    assert created.id == "flow-test-1"
    assert created.name == "Test Flow"
    assert created.is_active is True

    # 2. Get flow
    fetched = temp_db.get_flow("flow-test-1")
    assert fetched is not None
    assert fetched.name == "Test Flow"
    assert len(fetched.flow_data["nodes"]) == 1

    # 3. List flows
    flows = temp_db.list_flows()
    assert len(flows) == 1
    assert flows[0].id == "flow-test-1"

    # 4. Update flow
    flow_payload["name"] = "Updated Flow"
    updated = temp_db.update_flow("flow-test-1", flow_payload, is_active=False)
    assert updated.name == "Updated Flow"
    assert updated.is_active is False

    # 5. Delete flow
    deleted = temp_db.delete_flow("flow-test-1")
    assert deleted is True
    assert temp_db.get_flow("flow-test-1") is None

def test_execution_history_and_snapshots(temp_db):
    # 1. Record execution
    exec_record = temp_db.record_execution(
        execution_id="exec-101",
        flow_id="flow-1",
        trigger_type="manual",
        status="running",
        node_states={"node-1": {"status": "running"}},
        initial_payload={"param": 42}
    )
    assert exec_record.id == "exec-101"
    assert exec_record.status == "running"

    # 2. Update execution completed with full node snapshots
    completed = temp_db.update_execution_status(
        execution_id="exec-101",
        status="completed",
        duration_ms=125,
        node_states={
            "node-1": {"status": "completed", "output": {"data": "hello"}},
            "node-2": {"status": "completed", "output": {"result": "world"}}
        }
    )
    assert completed.status == "completed"
    assert completed.duration_ms == 125
    assert "node-2" in completed.node_states

    # 3. Retrieve executions for flow
    history = temp_db.list_executions(flow_id="flow-1")
    assert len(history) == 1
    assert history[0].id == "exec-101"

    # 4. Get execution detail
    detail = temp_db.get_execution("exec-101")
    assert detail is not None
    assert detail.node_states["node-1"]["output"]["data"] == "hello"
