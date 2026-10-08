import pytest
from backend.app.components.builtins.logic import TryCatchComponent
from backend.app.components.builtins.triggers import ManualTriggerComponent
from backend.app.components.builtins.actions import PythonScriptComponent
from backend.app.models.flow import FlowModel, NodeModel, EdgeModel
from backend.app.engine.runner import FlowRunner


@pytest.mark.asyncio
async def test_try_catch_success_path():
    comp = TryCatchComponent(
        inputs={
            "input_data": {"user_id": 42, "role": "admin"},
            "fallback_value": {"user_id": 0, "role": "guest"},
            "error_message": "",
        }
    )

    res = await comp.execute()

    assert res["has_error"] is False
    assert res["error_details"] == ""
    assert res["result"] == {"user_id": 42, "role": "admin"}
    assert res["success_branch"] == {"user_id": 42, "role": "admin"}
    assert res["error_branch"] is None


@pytest.mark.asyncio
async def test_try_catch_error_path():
    comp = TryCatchComponent(
        inputs={
            "input_data": {},
            "fallback_value": {"user_id": 0, "role": "guest"},
            "error_message": "Network timeout after 30s",
        }
    )

    res = await comp.execute()

    assert res["has_error"] is True
    assert res["error_details"] == "Network timeout after 30s"
    assert res["result"] == {"user_id": 0, "role": "guest"}
    assert res["success_branch"] is None
    assert res["error_branch"]["error"] == "Network timeout after 30s"
    assert res["error_branch"]["fallback"] == {"user_id": 0, "role": "guest"}


@pytest.mark.asyncio
async def test_try_catch_in_flow_runner_upstream_success():
    flow = FlowModel(
        id="flow_tc_success",
        name="TryCatch Success Flow",
        nodes=[
            NodeModel(
                id="trigger_1",
                type="ManualTriggerComponent",
                data={"inputs": {"initial_payload": {"balance": 1000}}},
            ),
            NodeModel(
                id="try_1",
                type="TryCatchComponent",
                data={
                    "inputs": {
                        "fallback_value": {"balance": 0},
                    }
                },
            ),
            NodeModel(
                id="on_success",
                type="PythonScriptComponent",
                data={"inputs": {"code": "def run(inputs):\n    return {'status': 'processed', 'data': inputs}\n"}},
            ),
            NodeModel(
                id="on_error",
                type="PythonScriptComponent",
                data={"inputs": {"code": "def run(inputs):\n    return {'alert_sent': True}\n"}},
            ),
        ],
        edges=[
            EdgeModel(id="e1", source="trigger_1", source_handle="data", target="try_1", target_handle="input_data"),
            EdgeModel(id="e2", source="try_1", source_handle="success_branch", target="on_success", target_handle="input_data"),
            EdgeModel(id="e3", source="try_1", source_handle="error_branch", target="on_error", target_handle="input_data"),
        ],
    )

    runner = FlowRunner(flow)
    summary = await runner.execute_flow()

    assert summary["status"] == "completed"
    assert "on_success" in summary["results"]
    assert summary["results"]["on_success"]["status"] == "processed"
    # on_error should be skipped due to inactive branch
    assert "on_error" not in summary["results"] or "on_error" in summary["skipped"]
    assert "on_error" in summary["skipped"]


@pytest.mark.asyncio
async def test_try_catch_in_flow_runner_intercepts_upstream_failure():
    flow = FlowModel(
        id="flow_tc_fail",
        name="TryCatch Intercept Flow",
        nodes=[
            NodeModel(
                id="trigger_1",
                type="ManualTriggerComponent",
                data={"inputs": {"initial_payload": {}}},
            ),
            NodeModel(
                id="failing_node",
                type="PythonScriptComponent",
                data={"inputs": {"code": "def run(inputs):\n    return 1 / 0\n"}},  # Deliberate ZeroDivisionError
            ),
            NodeModel(
                id="try_1",
                type="TryCatchComponent",
                data={
                    "inputs": {
                        "fallback_value": {"recovered": True, "value": 999},
                        "catch_upstream_errors": True,
                    }
                },
            ),
            NodeModel(
                id="on_success",
                type="PythonScriptComponent",
                data={"inputs": {"code": "def run(inputs):\n    return 'should_not_run'\n"}},
            ),
            NodeModel(
                id="on_error",
                type="PythonScriptComponent",
                data={"inputs": {"code": "def run(inputs):\n    return {'handled': True, 'err': inputs.get('error')}\n"}},
            ),
        ],
        edges=[
            EdgeModel(id="e1", source="trigger_1", source_handle="data", target="failing_node", target_handle="input_data"),
            EdgeModel(id="e2", source="failing_node", source_handle="result", target="try_1", target_handle="input_data"),
            EdgeModel(id="e3", source="try_1", source_handle="success_branch", target="on_success", target_handle="input_data"),
            EdgeModel(id="e4", source="try_1", source_handle="error_branch", target="on_error", target_handle="input_data"),
        ],
    )

    runner = FlowRunner(flow)
    summary = await runner.execute_flow()

    # Flow should finish as completed because TryCatch handled the error!
    assert summary["status"] == "completed"
    assert "try_1" in summary["results"]
    assert summary["results"]["try_1"]["has_error"] is True
    assert summary["results"]["try_1"]["result"] == {"recovered": True, "value": 999}

    # on_success skipped, on_error executed
    assert "on_success" in summary["skipped"]
    assert "on_error" in summary["results"]
    assert summary["results"]["on_error"]["handled"] is True


@pytest.mark.asyncio
async def test_try_catch_in_flow_runner_skip_when_catch_disabled():
    flow = FlowModel(
        id="flow_tc_no_catch",
        name="TryCatch Disabled Flow",
        nodes=[
            NodeModel(
                id="trigger_1",
                type="ManualTriggerComponent",
                data={"inputs": {"initial_payload": {}}},
            ),
            NodeModel(
                id="failing_node",
                type="PythonScriptComponent",
                data={"inputs": {"code": "def run(inputs):\n    raise ValueError('Critical failure')\n"}},
            ),
            NodeModel(
                id="try_1",
                type="TryCatchComponent",
                data={
                    "inputs": {
                        "fallback_value": {},
                        "catch_upstream_errors": False,
                    }
                },
            ),
        ],
        edges=[
            EdgeModel(id="e1", source="trigger_1", source_handle="data", target="failing_node", target_handle="input_data"),
            EdgeModel(id="e2", source="failing_node", source_handle="result", target="try_1", target_handle="input_data"),
        ],
    )

    runner = FlowRunner(flow)
    summary = await runner.execute_flow()

    assert summary["status"] == "failed"
    assert "try_1" in summary["skipped"]
