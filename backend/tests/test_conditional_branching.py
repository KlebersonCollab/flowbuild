import pytest
from httpx import ASGITransport, AsyncClient

from backend.app.db import db_manager
from backend.app.engine.runner import FlowRunner
from backend.app.main import app
from backend.app.models.flow import FlowModel


@pytest.fixture(autouse=True)
def setup_db():
    db_manager.init_db()


@pytest.mark.asyncio
async def test_conditional_branch_true_branch_runs_false_branch_skipped():
    flow_data = {
        "id": "flow-cond-true",
        "name": "Conditional Flow True",
        "nodes": [
            {
                "id": "trig",
                "type": "ManualTriggerComponent",
                "position": {"x": 0, "y": 0},
                "data": {"inputs": {"initial_payload": {"amount": 250}}},
            },
            {
                "id": "cond",
                "type": "IfConditionComponent",
                "position": {"x": 200, "y": 0},
                "data": {"inputs": {"expression": "data.get('amount', 0) > 100"}},
            },
            {
                "id": "act_true",
                "type": "JsonTransformComponent",
                "position": {"x": 400, "y": -100},
                "data": {"inputs": {"expression": "dict(tier='VIP', amount=payload.get('amount'))"}},
            },
            {
                "id": "act_false",
                "type": "JsonTransformComponent",
                "position": {"x": 400, "y": 100},
                "data": {"inputs": {"expression": "dict(tier='STANDARD', amount=payload.get('amount'))"}},
            },
            {
                "id": "act_false_downstream",
                "type": "JsonTransformComponent",
                "position": {"x": 600, "y": 100},
                "data": {"inputs": {"expression": "dict(processed=True)"}},
            },
        ],
        "edges": [
            {"id": "e1", "source": "trig", "sourceHandle": "data", "target": "cond", "targetHandle": "input_data"},
            {"id": "e2", "source": "cond", "sourceHandle": "true_branch", "target": "act_true", "targetHandle": "input_data"},
            {"id": "e3", "source": "cond", "sourceHandle": "false_branch", "target": "act_false", "targetHandle": "input_data"},
            {"id": "e4", "source": "act_false", "sourceHandle": "output_data", "target": "act_false_downstream", "targetHandle": "input_data"},
        ],
    }

    flow = FlowModel.model_validate(flow_data)
    runner = FlowRunner(flow, require_trigger=True)

    events = []
    async for event in runner.execute_stream():
        events.append(event)

    summary = runner.get_summary()

    # Flow must succeed
    assert summary["status"] == "completed"
    assert "act_true" in summary["results"]
    assert summary["results"]["act_true"]["tier"] == "VIP"

    # Inactive branch nodes must be skipped, NOT executed
    assert "act_false" not in summary["results"]
    assert "act_false_downstream" not in summary["results"]

    # Verify skipped events were emitted
    skipped_node_ids = [e["node_id"] for e in events if e.get("event") == "node_skipped"]
    assert "act_false" in skipped_node_ids
    assert "act_false_downstream" in skipped_node_ids


@pytest.mark.asyncio
async def test_conditional_branch_false_branch_runs_true_branch_skipped():
    flow_data = {
        "id": "flow-cond-false",
        "name": "Conditional Flow False",
        "nodes": [
            {
                "id": "trig",
                "type": "ManualTriggerComponent",
                "position": {"x": 0, "y": 0},
                "data": {"inputs": {"initial_payload": {"amount": 50}}},
            },
            {
                "id": "cond",
                "type": "IfConditionComponent",
                "position": {"x": 200, "y": 0},
                "data": {"inputs": {"expression": "data.get('amount', 0) > 100"}},
            },
            {
                "id": "act_true",
                "type": "JsonTransformComponent",
                "position": {"x": 400, "y": -100},
                "data": {"inputs": {"expression": "dict(tier='VIP')"}},
            },
            {
                "id": "act_false",
                "type": "JsonTransformComponent",
                "position": {"x": 400, "y": 100},
                "data": {"inputs": {"expression": "dict(tier='STANDARD')"}},
            },
        ],
        "edges": [
            {"id": "e1", "source": "trig", "sourceHandle": "data", "target": "cond", "targetHandle": "input_data"},
            {"id": "e2", "source": "cond", "sourceHandle": "true_branch", "target": "act_true", "targetHandle": "input_data"},
            {"id": "e3", "source": "cond", "sourceHandle": "false_branch", "target": "act_false", "targetHandle": "input_data"},
        ],
    }

    flow = FlowModel.model_validate(flow_data)
    runner = FlowRunner(flow, require_trigger=True)

    events = []
    async for event in runner.execute_stream():
        events.append(event)

    summary = runner.get_summary()

    assert summary["status"] == "completed"
    assert "act_false" in summary["results"]
    assert summary["results"]["act_false"]["tier"] == "STANDARD"
    assert "act_true" not in summary["results"]

    skipped_node_ids = [e["node_id"] for e in events if e.get("event") == "node_skipped"]
    assert "act_true" in skipped_node_ids
