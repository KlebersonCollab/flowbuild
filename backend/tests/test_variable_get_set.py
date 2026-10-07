import pytest
from backend.app.components.builtins.triggers import ManualTriggerComponent
from backend.app.components.builtins.variables import VariableComponent
from backend.app.db import DatabaseManager
from backend.app.engine.runner import FlowRunner
from backend.app.models.flow import EdgeModel, FlowModel, NodeModel


@pytest.fixture
def temp_db(tmp_path):
    db_file = tmp_path / "test_variables_get_set.db"
    db_url = f"sqlite:///{db_file}"
    mgr = DatabaseManager(database_url=db_url)
    mgr.init_db()
    yield mgr
    mgr.close()


@pytest.mark.asyncio
async def test_variable_component_get_mode(temp_db):
    # Seed a variable
    temp_db.create_variable(key="API_KEY", value="secret_123", scope="global")

    # Mode get
    comp = VariableComponent(
        inputs={
            "mode": "get",
            "variable_name": "API_KEY",
            "_db_manager": temp_db,
        }
    )
    res = await comp.execute()
    assert res["value"] == "secret_123"
    assert res["variable_name"] == "API_KEY"
    assert res["success"] is True


@pytest.mark.asyncio
async def test_variable_component_get_default_fallback(temp_db):
    comp = VariableComponent(
        inputs={
            "mode": "get",
            "variable_name": "NON_EXISTENT",
            "default_value": "fallback_val",
            "_db_manager": temp_db,
        }
    )
    res = await comp.execute()
    assert res["value"] == "fallback_val"


@pytest.mark.asyncio
async def test_variable_component_set_mode_and_persistence(temp_db):
    comp = VariableComponent(
        inputs={
            "mode": "set",
            "variable_name": "AUTH_TOKEN",
            "value": "bearer_jwt_token_456",
            "scope": "flow",
            "persist": True,
            "_flow_id": "flow-auth-1",
            "_environment": "dev",
            "_db_manager": temp_db,
        }
    )
    res = await comp.execute()
    assert res["value"] == "bearer_jwt_token_456"
    assert res["variable_name"] == "AUTH_TOKEN"
    assert res["success"] is True

    # Check persistence in db
    saved_val = temp_db.resolve_variable_value("AUTH_TOKEN", flow_id="flow-auth-1", environment="dev")
    assert saved_val == "bearer_jwt_token_456"

    # Upsert test: set again with new token
    comp_update = VariableComponent(
        inputs={
            "mode": "set",
            "variable_name": "AUTH_TOKEN",
            "value": "renewed_token_789",
            "scope": "flow",
            "persist": True,
            "_flow_id": "flow-auth-1",
            "_environment": "dev",
            "_db_manager": temp_db,
        }
    )
    res_update = await comp_update.execute()
    assert res_update["value"] == "renewed_token_789"

    updated_val = temp_db.resolve_variable_value("AUTH_TOKEN", flow_id="flow-auth-1", environment="dev")
    assert updated_val == "renewed_token_789"


@pytest.mark.asyncio
async def test_variable_component_set_global_scope(temp_db):
    comp = VariableComponent(
        inputs={
            "mode": "set",
            "variable_name": "GLOBAL_CONFIG",
            "value": "active_v2",
            "scope": "global",
            "persist": True,
            "_environment": "all",
            "_db_manager": temp_db,
        }
    )
    await comp.execute()

    # Another flow should be able to resolve it
    val = temp_db.resolve_variable_value("GLOBAL_CONFIG", flow_id="other-flow-99")
    assert val == "active_v2"


@pytest.mark.asyncio
async def test_flow_runner_propagates_set_variable_downstream(temp_db, monkeypatch):
    from backend.app import db as app_db
    monkeypatch.setattr(app_db, "db_manager", temp_db)

    # Build flow: Trigger -> SetVariable ("JWT_TOKEN" = "my_dynamic_token") -> GetVariable ("JWT_TOKEN")
    flow = FlowModel(
        id="flow-dynamic-token",
        name="Dynamic Token Flow",
        nodes=[
            NodeModel(id="trigger", type="ManualTriggerComponent", data={}),
            NodeModel(
                id="set_var",
                type="VariableComponent",
                data={
                    "inputs": {
                        "mode": "set",
                        "variable_name": "JWT_TOKEN",
                        "value": "my_dynamic_token",
                        "scope": "flow",
                        "persist": True,
                    }
                },
            ),
            NodeModel(
                id="get_var",
                type="VariableComponent",
                data={
                    "inputs": {
                        "mode": "get",
                        "variable_name": "JWT_TOKEN",
                    }
                },
            ),
        ],
        edges=[
            EdgeModel(id="e1", source="trigger", target="set_var"),
            EdgeModel(id="e2", source="set_var", target="get_var"),
        ],
    )

    runner = FlowRunner(flow)
    events = []
    async for event in runner.execute_stream():
        events.append(event)

    completed_events = [e for e in events if e.get("event") == "node_completed"]
    assert len(completed_events) == 3

    get_var_output = next(e["output"] for e in completed_events if e["node_id"] == "get_var")
    assert get_var_output["value"] == "my_dynamic_token"
    assert get_var_output["success"] is True
