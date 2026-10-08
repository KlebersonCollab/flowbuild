import asyncio
import time
import pytest

from backend.app.components.builtins.logic import DelayComponent
from backend.app.components.builtins.triggers import ManualTriggerComponent
from backend.app.components.builtins.actions import PythonScriptComponent
from backend.app.components.registry import ComponentRegistry
from backend.app.engine.runner import FlowRunner
from backend.app.models.flow import EdgeModel, FlowModel, NodeModel


@pytest.mark.asyncio
async def test_delay_component_seconds_execution():
    comp = DelayComponent(inputs={"delay": 0.05, "unit": "seconds", "input_data": {"user": "Alice"}})
    start = time.perf_counter()
    output = await comp.execute()
    elapsed = time.perf_counter() - start

    assert elapsed >= 0.04
    assert output["data"] == {"user": "Alice"}
    assert output["waited_seconds"] == 0.05
    assert output["unit"] == "seconds"
    assert await comp.get_data() == {"user": "Alice"}
    assert await comp.get_waited_seconds() == 0.05


@pytest.mark.asyncio
async def test_delay_component_milliseconds_execution():
    comp = DelayComponent(inputs={"delay": 50, "unit": "milliseconds", "input_data": [1, 2, 3]})
    start = time.perf_counter()
    output = await comp.execute()
    elapsed = time.perf_counter() - start

    assert elapsed >= 0.04
    assert output["data"] == [1, 2, 3]
    assert pytest.approx(output["waited_seconds"], 0.001) == 0.05


@pytest.mark.asyncio
async def test_delay_component_minutes_conversion():
    comp = DelayComponent(inputs={"delay": 0.001, "unit": "minutes", "input_data": "sample"})
    start = time.perf_counter()
    output = await comp.execute()
    elapsed = time.perf_counter() - start

    assert elapsed >= 0.05
    assert output["data"] == "sample"
    assert pytest.approx(output["waited_seconds"], 0.001) == 0.06


@pytest.mark.asyncio
async def test_delay_component_zero_and_negative():
    comp_zero = DelayComponent(inputs={"delay": 0, "unit": "seconds", "input_data": {"val": 1}})
    res_zero = await comp_zero.execute()
    assert res_zero["waited_seconds"] == 0.0
    assert res_zero["data"] == {"val": 1}

    comp_neg = DelayComponent(inputs={"delay": -5, "unit": "seconds", "input_data": {"val": 2}})
    res_neg = await comp_neg.execute()
    assert res_neg["waited_seconds"] == 0.0
    assert res_neg["data"] == {"val": 2}


@pytest.mark.asyncio
async def test_flow_runner_delay_pipeline():
    registry = ComponentRegistry()
    registry.register(ManualTriggerComponent)
    registry.register(DelayComponent)
    registry.register(PythonScriptComponent)

    flow = FlowModel(
        id="flow_test_delay",
        name="Delay Pipeline Test",
        nodes=[
            NodeModel(
                id="node_trigger",
                type="ManualTriggerComponent",
                position={"x": 0, "y": 0},
                data={"inputs": {"initial_payload": {"status": "started", "items": [10, 20]}}},
            ),
            NodeModel(
                id="node_delay",
                type="DelayComponent",
                position={"x": 200, "y": 0},
                data={"inputs": {"delay": 0.05, "unit": "seconds"}},
            ),
            NodeModel(
                id="node_script",
                type="PythonScriptComponent",
                position={"x": 400, "y": 0},
                data={
                    "inputs": {
                        "code": "def run(inputs):\n    return {'received': inputs, 'count': len(inputs.get('items', []))}\n"
                    }
                },
            ),
        ],
        edges=[
            EdgeModel(
                id="edge_1",
                source="node_trigger",
                target="node_delay",
                source_handle="data",
                target_handle="input_data",
            ),
            EdgeModel(
                id="edge_2",
                source="node_delay",
                target="node_script",
                source_handle="data",
                target_handle="input_data",
            ),
        ],
    )

    runner = FlowRunner(flow=flow, registry=registry)
    events = []
    start = time.perf_counter()
    async for event in runner.execute_stream():
        events.append(event)
    total_time = time.perf_counter() - start

    assert total_time >= 0.04
    completed_events = [e for e in events if e.get("event") == "node_completed"]
    assert len(completed_events) == 3

    delay_output = runner.context.results["node_delay"]
    assert delay_output["data"] == {"status": "started", "items": [10, 20]}
    assert delay_output["waited_seconds"] == 0.05

    script_output = runner.context.results["node_script"]
    assert script_output["count"] == 2
    assert script_output["received"] == {"status": "started", "items": [10, 20]}


@pytest.mark.asyncio
async def test_flow_runner_delay_variable_interpolation():
    registry = ComponentRegistry()
    registry.register(ManualTriggerComponent)
    registry.register(DelayComponent)

    flow = FlowModel(
        id="flow_test_delay_var",
        name="Delay Variable Test",
        nodes=[
            NodeModel(
                id="node_trigger",
                type="ManualTriggerComponent",
                position={"x": 0, "y": 0},
                data={"inputs": {}},
            ),
            NodeModel(
                id="node_delay",
                type="DelayComponent",
                position={"x": 200, "y": 0},
                data={"inputs": {"delay": "{{WAIT_DURATION}}", "unit": "seconds"}},
            ),
        ],
        edges=[
            EdgeModel(
                id="edge_1",
                source="node_trigger",
                target="node_delay",
            ),
        ],
    )

    runner = FlowRunner(
        flow=flow,
        registry=registry,
        variables={"WAIT_DURATION": 0.04},
    )

    start = time.perf_counter()
    async for _ in runner.execute_stream():
        pass
    elapsed = time.perf_counter() - start

    assert elapsed >= 0.03
    delay_output = runner.context.results["node_delay"]
    assert delay_output["waited_seconds"] == 0.04
