import pytest
import tempfile
import os
from unittest.mock import patch, AsyncMock
import httpx

from backend.app.db import DatabaseManager
from backend.app.models.flow import FlowModel, NodeModel, EdgeModel
from backend.app.engine.runner import FlowRunner
from backend.app.components.builtins.variables import VariableComponent
from backend.app.components.builtins.actions import HttpRequestComponent
from backend.app.components.registry import ComponentRegistry


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
async def test_variable_component_direct():
    # 1. With explicitly injected _variables map
    comp = VariableComponent(inputs={
        "variable_name": "API_KEY",
        "default_value": "fallback",
        "_variables": {"API_KEY": "secret-12345"}
    })
    res = await comp.execute()
    assert res == {"value": "secret-12345"}
    assert await comp.get_value() == "secret-12345"

    # 2. With missing variable, falls back to default_value
    comp_fallback = VariableComponent(inputs={
        "variable_name": "NON_EXISTENT",
        "default_value": "default-fallback",
        "_variables": {}
    })
    res_fallback = await comp_fallback.execute()
    assert res_fallback == {"value": "default-fallback"}


@pytest.mark.asyncio
async def test_variable_component_with_db(temp_db):
    temp_db.create_variable(key="SERVER_PORT", value="8080", scope="global")
    temp_db.create_variable(key="SERVER_PORT", value="9090", scope="flow", flow_id="flow-special")

    # Flow special should get 9090
    with patch("backend.app.db.db_manager", temp_db):
        comp = VariableComponent(inputs={
            "variable_name": "SERVER_PORT",
            "_flow_id": "flow-special"
        })
        res = await comp.execute()
        assert res["value"] == "9090"

        # Another flow should get global 8080
        comp_other = VariableComponent(inputs={
            "variable_name": "SERVER_PORT",
            "_flow_id": "flow-other"
        })
        res_other = await comp_other.execute()
        assert res_other["value"] == "8080"


@pytest.mark.asyncio
async def test_flow_runner_template_interpolation():
    registry = ComponentRegistry()
    registry.register(HttpRequestComponent)

    flow = FlowModel(
        id="flow-interp-1",
        name="Interpolation Test Flow",
        nodes=[
            NodeModel(
                id="http-1",
                type="HttpRequestComponent",
                data={
                    "inputs": {
                        "url": "https://{{DOMAIN}}/api/{{VERSION}}/users",
                        "method": "GET",
                        "headers": {
                            "Authorization": "Bearer {{API_TOKEN}}",
                            "X-Scope": "{{flow.ENVIRONMENT}}"
                        }
                    }
                }
            )
        ],
        edges=[]
    )

    runner = FlowRunner(
        flow=flow,
        registry=registry,
        variables={
            "DOMAIN": "api.example.com",
            "VERSION": "v2",
            "API_TOKEN": "my-secret-token",
            "ENVIRONMENT": "production"
        }
    )

    # Inspect resolved inputs directly
    resolved_inputs = runner._resolve_node_inputs("http-1")
    assert resolved_inputs["url"] == "https://api.example.com/api/v2/users"
    assert resolved_inputs["headers"]["Authorization"] == "Bearer my-secret-token"
    assert resolved_inputs["headers"]["X-Scope"] == "production"

    # Mock httpx to test end-to-end execution
    mock_resp = AsyncMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"success": True}

    with patch("httpx.AsyncClient.request", return_value=mock_resp) as mock_request:
        summary = await runner.execute_flow()
        assert summary["status"] == "completed"
        assert mock_request.called
        call_kwargs = mock_request.call_args.kwargs
        assert call_kwargs["url"] == "https://api.example.com/api/v2/users"
        assert call_kwargs["headers"]["Authorization"] == "Bearer my-secret-token"
        assert call_kwargs["headers"]["X-Scope"] == "production"


@pytest.mark.asyncio
async def test_flow_runner_variable_hierarchy_with_db(temp_db):
    temp_db.create_variable(key="BASE_URL", value="https://api.global.com", scope="global")
    temp_db.create_variable(key="BASE_URL", value="https://api.flow1.com", scope="flow", flow_id="flow-hierarchy-1")

    registry = ComponentRegistry()
    registry.register(HttpRequestComponent)

    flow1 = FlowModel(
        id="flow-hierarchy-1",
        name="Flow 1 Hierarchy",
        nodes=[
            NodeModel(
                id="http-1",
                type="HttpRequestComponent",
                data={"inputs": {"url": "{{BASE_URL}}/items", "method": "GET"}}
            )
        ]
    )

    flow2 = FlowModel(
        id="flow-hierarchy-2",
        name="Flow 2 Hierarchy",
        nodes=[
            NodeModel(
                id="http-1",
                type="HttpRequestComponent",
                data={"inputs": {"url": "{{BASE_URL}}/items", "method": "GET"}}
            )
        ]
    )

    runner1 = FlowRunner(flow=flow1, registry=registry, db_manager=temp_db)
    runner2 = FlowRunner(flow=flow2, registry=registry, db_manager=temp_db)

    inp1 = runner1._resolve_node_inputs("http-1")
    inp2 = runner2._resolve_node_inputs("http-1")

    # Flow 1 has flow-scoped override
    assert inp1["url"] == "https://api.flow1.com/items"
    # Flow 2 falls back to global variable
    assert inp2["url"] == "https://api.global.com/items"
