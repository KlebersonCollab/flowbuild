import pytest
from backend.app.components.builtins.variables import VariableComponent
from backend.app.db import DatabaseManager


@pytest.fixture
def temp_db(tmp_path):
    db_file = tmp_path / "test_variables_environment.db"
    db_url = f"sqlite:///{db_file}"
    mgr = DatabaseManager(database_url=db_url)
    mgr.init_db()
    yield mgr
    mgr.close()


@pytest.mark.asyncio
async def test_variable_component_environment_current_mode(temp_db):
    # Flow running in 'qa' environment with environment='current' (default)
    comp = VariableComponent(
        inputs={
            "mode": "set",
            "variable_name": "ENV_AWARE_KEY",
            "value": "qa_value_123",
            "scope": "flow",
            "environment": "current",
            "persist": True,
            "_flow_id": "flow-qa-1",
            "_environment": "qa",
            "_db_manager": temp_db,
        }
    )
    res = await comp.execute()
    assert res["value"] == "qa_value_123"
    assert res["variable_name"] == "ENV_AWARE_KEY"
    assert res["success"] is True

    # Resolving in 'qa' environment matches
    val_qa = temp_db.resolve_variable_value("ENV_AWARE_KEY", flow_id="flow-qa-1", environment="qa")
    assert val_qa == "qa_value_123"

    # Resolving in 'dev' environment falls back to None (since saved specifically to QA)
    val_dev = temp_db.resolve_variable_value("ENV_AWARE_KEY", flow_id="flow-qa-1", environment="dev")
    assert val_dev is None


@pytest.mark.asyncio
async def test_variable_component_environment_explicit_all(temp_db):
    # Flow running in 'dev', but explicitly saving to 'all'
    comp = VariableComponent(
        inputs={
            "mode": "set",
            "variable_name": "SHARED_GLOBAL_KEY",
            "value": "shared_value_456",
            "scope": "global",
            "environment": "all",
            "persist": True,
            "_environment": "dev",
            "_db_manager": temp_db,
        }
    )
    await comp.execute()

    # Accessible in dev, qa, and prd
    assert temp_db.resolve_variable_value("SHARED_GLOBAL_KEY", environment="dev") == "shared_value_456"
    assert temp_db.resolve_variable_value("SHARED_GLOBAL_KEY", environment="qa") == "shared_value_456"
    assert temp_db.resolve_variable_value("SHARED_GLOBAL_KEY", environment="prd") == "shared_value_456"


@pytest.mark.asyncio
async def test_variable_component_environment_explicit_prd(temp_db):
    # Flow running in 'dev' setting a token specifically for 'prd'
    comp = VariableComponent(
        inputs={
            "mode": "set",
            "variable_name": "TARGET_PROD_URL",
            "value": "https://api.production.com",
            "scope": "global",
            "environment": "prd",
            "persist": True,
            "_environment": "dev",
            "_db_manager": temp_db,
        }
    )
    await comp.execute()

    # In PRD it resolves to the prod URL
    assert temp_db.resolve_variable_value("TARGET_PROD_URL", environment="prd") == "https://api.production.com"
    # In DEV it does not resolve
    assert temp_db.resolve_variable_value("TARGET_PROD_URL", environment="dev") is None


@pytest.mark.asyncio
async def test_variable_component_get_mode_explicit_environment(temp_db):
    # Seed DEV and QA with different values
    temp_db.create_variable(key="ENDPOINT", value="http://qa.internal", scope="global", environment="qa")
    temp_db.create_variable(key="ENDPOINT", value="http://dev.internal", scope="global", environment="dev")

    # Node in DEV flow explicitly requesting QA endpoint
    comp = VariableComponent(
        inputs={
            "mode": "get",
            "variable_name": "ENDPOINT",
            "environment": "qa",
            "_environment": "dev",
            "_db_manager": temp_db,
        }
    )
    res = await comp.execute()
    assert res["value"] == "http://qa.internal"
    assert res["success"] is True
