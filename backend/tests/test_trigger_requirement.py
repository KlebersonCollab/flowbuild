import json
import pytest
from httpx import ASGITransport, AsyncClient

from backend.app.engine.runner import FlowRunner
from backend.app.main import app
from backend.app.models.flow import EdgeModel, FlowModel, NodeModel


@pytest.fixture
def test_app():
    return app


@pytest.mark.asyncio
async def test_flow_runner_fails_without_trigger_when_required():
    flow = FlowModel(
        id="flow-no-trigger",
        name="No Trigger Flow",
        nodes=[
            NodeModel(
                id="node-action",
                type="JsonTransformComponent",
                data={"inputs": {"expression": "'hello'"}},
            )
        ],
        edges=[],
    )
    runner = FlowRunner(flow, require_trigger=True)
    events = [event async for event in runner.execute_stream()]

    failed_event = next((e for e in events if e.get("event") == "flow_failed"), None)
    assert failed_event is not None
    assert "Trigger" in failed_event.get("error", "")
    assert runner.context.status == "failed"


@pytest.mark.asyncio
async def test_flow_runner_succeeds_with_trigger():
    flow = FlowModel(
        id="flow-with-trigger",
        name="With Trigger Flow",
        nodes=[
            NodeModel(
                id="node-trig",
                type="ManualTriggerComponent",
                data={"inputs": {"initial_payload": {"greeting": "oi"}}},
            ),
            NodeModel(
                id="node-action",
                type="JsonTransformComponent",
                data={"inputs": {"expression": "payload['greeting']"}},
            ),
        ],
        edges=[
            EdgeModel(
                id="edge-1",
                source="node-trig",
                sourceHandle="data",
                target="node-action",
                targetHandle="input_data",
            )
        ],
    )
    runner = FlowRunner(flow, require_trigger=True)
    summary = await runner.execute_flow()
    assert summary["status"] == "completed"
    assert "node-trig" in summary["results"]
    assert "node-action" in summary["results"]


@pytest.mark.asyncio
async def test_stream_api_endpoint_blocks_flow_without_trigger(test_app):
    flow_data = {
        "id": "flow-api-no-trigger",
        "name": "API No Trigger",
        "nodes": [
            {
                "id": "node-only-action",
                "type=" : "JsonTransformComponent",
                "type": "JsonTransformComponent",
                "data": {"inputs": {"expression": "123"}},
            }
        ],
        "edges": [],
    }
    async with AsyncClient(
        transport=ASGITransport(app=test_app), base_url="http://test"
    ) as client:
        resp = await client.post("/api/v1/flows/execute/stream", json=flow_data)
        assert resp.status_code == 200
        content = resp.text
        assert "flow_failed" in content
        assert "Trigger" in content
