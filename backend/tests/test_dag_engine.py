from typing import Any, ClassVar

import pytest

from backend.app.components.base import BaseComponent
from backend.app.components.inputs import BaseInput, IntInput, StrInput
from backend.app.components.outputs import Output
from backend.app.components.registry import ComponentRegistry
from backend.app.engine.dag_builder import DAGBuilder
from backend.app.engine.exceptions import CyclicGraphError
from backend.app.engine.runner import FlowRunner
from backend.app.models.flow import EdgeModel, FlowModel, NodeModel


class StepProducer(BaseComponent):
    name = "StepProducer"
    inputs: ClassVar[list[BaseInput]] = [
        IntInput(name="start_num", default=10),
    ]
    outputs: ClassVar[list[Output]] = [
        Output(name="value", type="int", method="produce"),
    ]

    async def produce(self) -> dict[str, Any]:
        return {"value": self.get_inputs()["start_num"]}


class StepDoubler(BaseComponent):
    name = "StepDoubler"
    inputs: ClassVar[list[BaseInput]] = [
        IntInput(name="value", default=0),
    ]
    outputs: ClassVar[list[Output]] = [
        Output(name="doubled", type="int", method="double_val"),
    ]

    async def double_val(self) -> dict[str, Any]:
        return {"doubled": self.get_inputs()["value"] * 2}


class StepFailing(BaseComponent):
    name = "StepFailing"
    inputs: ClassVar[list[BaseInput]] = [
        StrInput(name="msg", default=""),
    ]
    outputs: ClassVar[list[Output]] = [
        Output(name="res", type="str", method="fail"),
    ]

    async def fail(self) -> dict[str, Any]:
        raise ValueError("Simulated step failure")


@pytest.fixture
def mock_registry() -> ComponentRegistry:
    reg = ComponentRegistry()
    reg.register(StepProducer)
    reg.register(StepDoubler)
    reg.register(StepFailing)
    return reg


def test_topological_sort_linear():
    flow = FlowModel(
        id="flow-1",
        name="Linear Flow",
        nodes=[
            NodeModel(id="node-1", type="StepProducer"),
            NodeModel(id="node-2", type="StepDoubler"),
            NodeModel(id="node-3", type="StepDoubler"),
        ],
        edges=[
            EdgeModel(id="e-1", source="node-1", target="node-2"),
            EdgeModel(id="e-2", source="node-2", target="node-3"),
        ],
    )
    builder = DAGBuilder(flow)
    order = builder.get_topological_order()
    assert order == ["node-1", "node-2", "node-3"]


def test_topological_sort_diamond():
    flow = FlowModel(
        id="flow-diamond",
        name="Diamond Flow",
        nodes=[
            NodeModel(id="n-root", type="StepProducer"),
            NodeModel(id="n-left", type="StepDoubler"),
            NodeModel(id="n-right", type="StepDoubler"),
            NodeModel(id="n-join", type="StepDoubler"),
        ],
        edges=[
            EdgeModel(id="e-1", source="n-root", target="n-left"),
            EdgeModel(id="e-2", source="n-root", target="n-right"),
            EdgeModel(id="e-3", source="n-left", target="n-join"),
            EdgeModel(id="e-4", source="n-right", target="n-join"),
        ],
    )
    builder = DAGBuilder(flow)
    order = builder.get_topological_order()
    assert order[0] == "n-root"
    assert order[-1] == "n-join"
    assert set(order[1:3]) == {"n-left", "n-right"}


def test_cycle_detection_raises_error():
    flow = FlowModel(
        id="flow-cyclic",
        name="Cyclic Flow",
        nodes=[
            NodeModel(id="n-1", type="StepProducer"),
            NodeModel(id="n-2", type="StepDoubler"),
        ],
        edges=[
            EdgeModel(id="e-1", source="n-1", target="n-2"),
            EdgeModel(id="e-2", source="n-2", target="n-1"),
        ],
    )
    builder = DAGBuilder(flow)
    with pytest.raises(CyclicGraphError):
        builder.get_topological_order()


@pytest.mark.asyncio
async def test_flow_runner_execution_and_data_passing(mock_registry: ComponentRegistry):
    flow = FlowModel(
        id="flow-run-1",
        name="Run Flow",
        nodes=[
            NodeModel(id="p1", type="StepProducer", data={"inputs": {"start_num": 5}}),
            NodeModel(id="d1", type="StepDoubler"),
        ],
        edges=[
            EdgeModel(
                id="e1",
                source="p1",
                source_handle="value",
                target="d1",
                target_handle="value",
            ),
        ],
    )

    runner = FlowRunner(flow, registry=mock_registry)
    events = []
    async for event in runner.execute_stream():
        events.append(event)

    summary = runner.get_summary()
    assert summary["status"] == "completed"
    assert summary["results"]["p1"]["value"] == 5
    assert summary["results"]["d1"]["doubled"] == 10
    assert any(e["event"] == "node_completed" and e["node_id"] == "d1" for e in events)


@pytest.mark.asyncio
async def test_flow_runner_failure_isolation(mock_registry: ComponentRegistry):
    flow = FlowModel(
        id="flow-fail",
        name="Failing Flow",
        nodes=[
            NodeModel(id="fail-node", type="StepFailing"),
            NodeModel(id="downstream", type="StepDoubler"),
        ],
        edges=[
            EdgeModel(id="e-fail", source="fail-node", target="downstream"),
        ],
    )

    runner = FlowRunner(flow, registry=mock_registry)
    async for _ in runner.execute_stream():
        pass

    summary = runner.get_summary()
    assert summary["status"] == "failed"
    assert "fail-node" in summary["errors"]
    assert "Simulated step failure" in summary["errors"]["fail-node"]
    assert "downstream" not in summary["results"]
