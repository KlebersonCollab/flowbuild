import pytest

from backend.app.components.builtins.logic import SwitchNodeComponent
from backend.app.components.builtins.triggers import ManualTriggerComponent
from backend.app.components.builtins.actions import PythonScriptComponent
from backend.app.components.registry import ComponentRegistry
from backend.app.engine.runner import FlowRunner
from backend.app.models.flow import EdgeModel, FlowModel, NodeModel


@pytest.mark.asyncio
async def test_switch_node_case_1_match():
    comp = SwitchNodeComponent(
        inputs={
            "input_data": {"status": "paid", "amount": 100},
            "expression": "data.get('status')",
            "case_1_value": "paid",
            "case_2_value": "pending",
            "case_3_value": "cancelled",
        }
    )
    result = await comp.execute()

    assert result["matched_case"] == "case_1"
    assert result["evaluated_value"] == "paid"
    assert result["case_1"] == {"status": "paid", "amount": 100}
    assert result["case_2"] is None
    assert result["case_3"] is None
    assert result["default_branch"] is None


@pytest.mark.asyncio
async def test_switch_node_case_2_match():
    comp = SwitchNodeComponent(
        inputs={
            "input_data": {"status": "pending", "amount": 50},
            "expression": "data.get('status')",
            "case_1_value": "paid",
            "case_2_value": "pending",
            "case_3_value": "cancelled",
        }
    )
    result = await comp.execute()

    assert result["matched_case"] == "case_2"
    assert result["evaluated_value"] == "pending"
    assert result["case_1"] is None
    assert result["case_2"] == {"status": "pending", "amount": 50}
    assert result["case_3"] is None
    assert result["default_branch"] is None


@pytest.mark.asyncio
async def test_switch_node_case_3_match():
    comp = SwitchNodeComponent(
        inputs={
            "input_data": {"status": "cancelled", "reason": "fraud"},
            "expression": "data.get('status')",
            "case_1_value": "paid",
            "case_2_value": "pending",
            "case_3_value": "cancelled",
        }
    )
    result = await comp.execute()

    assert result["matched_case"] == "case_3"
    assert result["evaluated_value"] == "cancelled"
    assert result["case_1"] is None
    assert result["case_2"] is None
    assert result["case_3"] == {"status": "cancelled", "reason": "fraud"}
    assert result["default_branch"] is None


@pytest.mark.asyncio
async def test_switch_node_default_fallback():
    comp = SwitchNodeComponent(
        inputs={
            "input_data": {"status": "unknown_event", "code": 999},
            "expression": "data.get('status')",
            "case_1_value": "paid",
            "case_2_value": "pending",
            "case_3_value": "cancelled",
        }
    )
    result = await comp.execute()

    assert result["matched_case"] == "default_branch"
    assert result["evaluated_value"] == "unknown_event"
    assert result["case_1"] is None
    assert result["case_2"] is None
    assert result["case_3"] is None
    assert result["default_branch"] == {"status": "unknown_event", "code": 999}


@pytest.mark.asyncio
async def test_flow_runner_switch_branch_skipping():
    registry = ComponentRegistry()
    registry.register(ManualTriggerComponent)
    registry.register(SwitchNodeComponent)
    registry.register(PythonScriptComponent)

    flow = FlowModel(
        id="flow_test_switch",
        name="Switch Multi-Branch Test",
        nodes=[
            NodeModel(
                id="node_trigger",
                type="ManualTriggerComponent",
                position={"x": 0, "y": 0},
                data={"inputs": {"initial_payload": {"status": "pending", "order_id": 101}}},
            ),
            NodeModel(
                id="node_switch",
                type="SwitchNodeComponent",
                position={"x": 200, "y": 0},
                data={
                    "inputs": {
                        "expression": "data.get('status')",
                        "case_1_value": "paid",
                        "case_2_value": "pending",
                        "case_3_value": "cancelled",
                    }
                },
            ),
            NodeModel(
                id="node_script_case1",
                type="PythonScriptComponent",
                position={"x": 400, "y": -100},
                data={"inputs": {"code": "def run(inputs):\n    return {'handled_by': 'case1'}\n"}},
            ),
            NodeModel(
                id="node_script_case2",
                type="PythonScriptComponent",
                position={"x": 400, "y": 0},
                data={"inputs": {"code": "def run(inputs):\n    return {'handled_by': 'case2', 'order': inputs.get('order_id')}\n"}},
            ),
            NodeModel(
                id="node_script_default",
                type="PythonScriptComponent",
                position={"x": 400, "y": 100},
                data={"inputs": {"code": "def run(inputs):\n    return {'handled_by': 'default'}\n"}},
            ),
        ],
        edges=[
            EdgeModel(
                id="edge_in",
                source="node_trigger",
                target="node_switch",
                source_handle="data",
                target_handle="input_data",
            ),
            EdgeModel(
                id="edge_case1",
                source="node_switch",
                target="node_script_case1",
                source_handle="case_1",
                target_handle="input_data",
            ),
            EdgeModel(
                id="edge_case2",
                source="node_switch",
                target="node_script_case2",
                source_handle="case_2",
                target_handle="input_data",
            ),
            EdgeModel(
                id="edge_default",
                source="node_switch",
                target="node_script_default",
                source_handle="default_branch",
                target_handle="input_data",
            ),
        ],
    )

    runner = FlowRunner(flow=flow, registry=registry)
    events = []
    async for event in runner.execute_stream():
        events.append(event)

    completed_ids = [e["node_id"] for e in events if e.get("event") == "node_completed"]
    skipped_ids = [e["node_id"] for e in events if e.get("event") == "node_skipped"]

    assert "node_trigger" in completed_ids
    assert "node_switch" in completed_ids
    assert "node_script_case2" in completed_ids

    # Unmatched branches must be skipped gracefully
    assert "node_script_case1" in skipped_ids
    assert "node_script_default" in skipped_ids

    # Result of matched branch
    case2_res = runner.context.results["node_script_case2"]
    assert case2_res["handled_by"] == "case2"
    assert case2_res["order"] == 101
