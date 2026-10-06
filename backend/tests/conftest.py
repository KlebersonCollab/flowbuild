
import pytest

from backend.app.components.builtins import register_all_builtins


@pytest.fixture(autouse=True)
def setup_builtins():
    register_all_builtins()


@pytest.fixture
def sample_flow_data() -> dict:
    return {
        "id": "flow-test-1",
        "name": "Sample Test Flow",
        "nodes": [
            {
                "id": "node-trigger-1",
                "type": "ManualTriggerComponent",
                "position": {"x": 100, "y": 100},
                "data": {"inputs": {"initial_payload": {"message": "hello flowbuild"}}}
            },
            {
                "id": "node-transform-1",
                "type": "JsonTransformComponent",
                "position": {"x": 350, "y": 100},
                "data": {"inputs": {"expression": "payload['message'].upper()"}}
            }
        ],
        "edges": [
            {
                "id": "edge-1",
                "source": "node-trigger-1",
                "sourceHandle": "data",
                "target": "node-transform-1",
                "targetHandle": "input_data"
            }
        ]
    }
