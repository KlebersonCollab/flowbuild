import pytest
from httpx import ASGITransport, AsyncClient

from backend.app.db import DatabaseManager
from backend.app.engine.runner import FlowRunner
from backend.app.main import app
from backend.app.models.flow import FlowModel, NodeModel


@pytest.fixture
def tmp_db(tmp_path):
    db_file = tmp_path / "test_folders_env.db"
    manager = DatabaseManager(db_path=str(db_file))
    manager.init_db()
    yield manager
    manager.close()


def test_flows_table_folder_and_environment_schema(tmp_db):
    # Create flows in different folders and environments
    f1 = tmp_db.create_flow(
        {
            "id": "flow-fin-dev",
            "name": "Financeiro Dev",
            "folder": "Financeiro",
            "environment": "dev",
            "version": "v1.0.0",
            "nodes": [],
            "edges": [],
        }
    )
    assert f1.folder == "Financeiro"
    assert f1.environment == "dev"
    assert f1.version == "v1.0.0"

    f2 = tmp_db.create_flow(
        {
            "id": "flow-mkt-dev",
            "name": "Marketing Dev",
            "folder": "Marketing",
            "environment": "dev",
            "nodes": [],
            "edges": [],
        }
    )
    assert f2.folder == "Marketing"
    assert f2.environment == "dev"

    f3 = tmp_db.create_flow(
        {
            "id": "flow-fin-qa",
            "name": "Financeiro QA",
            "folder": "Financeiro",
            "environment": "qa",
            "version": "v1.0.0",
            "source_flow_id": "flow-fin-dev",
            "nodes": [],
            "edges": [],
        }
    )
    assert f3.environment == "qa"
    assert f3.source_flow_id == "flow-fin-dev"

    # Default values test
    f_default = tmp_db.create_flow(
        {
            "id": "flow-default",
            "name": "Default Flow",
            "nodes": [],
            "edges": [],
        }
    )
    assert f_default.folder == "Geral"
    assert f_default.environment == "dev"
    assert f_default.version == "v1.0.0"
    assert f_default.source_flow_id is None

    # Filter by folder
    fin_flows = tmp_db.list_flows(folder="Financeiro")
    assert len(fin_flows) == 2
    assert {f.id for f in fin_flows} == {"flow-fin-dev", "flow-fin-qa"}

    # Filter by environment
    qa_flows = tmp_db.list_flows(environment="qa")
    assert len(qa_flows) == 1
    assert qa_flows[0].id == "flow-fin-qa"

    # Filter by both folder and environment
    fin_dev_flows = tmp_db.list_flows(folder="Financeiro", environment="dev")
    assert len(fin_dev_flows) == 1
    assert fin_dev_flows[0].id == "flow-fin-dev"


def test_variable_multi_environment_resolution_hierarchy(tmp_db):
    flow_id = "flow-test-123"

    # 4-tier resolution hierarchy:
    # 4. Global, environment='all'
    tmp_db.create_variable(
        key="BASE_URL",
        value="https://api.all.com",
        scope="global",
        environment="all",
    )
    tmp_db.create_variable(
        key="FALLBACK_KEY",
        value="global-all-value",
        scope="global",
        environment="all",
    )

    # 3. Global, environment='qa'
    tmp_db.create_variable(
        key="BASE_URL",
        value="https://api.qa.company",
        scope="global",
        environment="qa",
    )

    # 2. Flow-scoped, environment='all'
    tmp_db.create_variable(
        key="FLOW_VAR",
        value="flow-all-val",
        scope="flow",
        flow_id=flow_id,
        environment="all",
    )

    # 1. Flow-scoped, environment='qa'
    tmp_db.create_variable(
        key="FLOW_VAR",
        value="flow-qa-val",
        scope="flow",
        flow_id=flow_id,
        environment="qa",
    )

    # Resolution for environment='qa'
    qa_vars = tmp_db.get_all_resolved_variables(flow_id=flow_id, environment="qa")
    assert qa_vars["BASE_URL"] == "https://api.qa.company"  # Global QA overrides Global all
    assert qa_vars["FALLBACK_KEY"] == "global-all-value"     # Global all fallback
    assert qa_vars["FLOW_VAR"] == "flow-qa-val"              # Flow QA overrides Flow all

    # Resolution for environment='dev'
    dev_vars = tmp_db.get_all_resolved_variables(flow_id=flow_id, environment="dev")
    assert dev_vars["BASE_URL"] == "https://api.all.com"     # No dev override, so global all
    assert dev_vars["FLOW_VAR"] == "flow-all-val"            # No dev override, so flow all


def test_flow_promotion_db_logic(tmp_db):
    # Create dev flow
    dev_flow = tmp_db.create_flow(
        {
            "id": "flow-sales",
            "name": "Sales Pipeline",
            "folder": "Vendas",
            "environment": "dev",
            "version": "v1.0.0",
            "nodes": [
                {
                    "id": "node-1",
                    "type": "DataTransformerComponent",
                    "data": {"inputs": {"template": "order-1"}},
                }
            ],
            "edges": [],
        }
    )

    # Promote to QA
    qa_flow = tmp_db.promote_flow(
        source_flow_id=dev_flow.id,
        target_environment="qa",
        target_version="v1.1.0",
    )
    assert qa_flow is not None
    assert qa_flow.environment == "qa"
    assert qa_flow.version == "v1.1.0"
    assert qa_flow.folder == "Vendas"
    assert qa_flow.source_flow_id == dev_flow.id
    assert qa_flow.flow_data["nodes"][0]["id"] == "node-1"

    # Promoting again to QA should update existing QA flow record
    qa_flow_v2 = tmp_db.promote_flow(
        source_flow_id=dev_flow.id,
        target_environment="qa",
        target_version="v1.2.0",
    )
    assert qa_flow_v2.id == qa_flow.id
    assert qa_flow_v2.version == "v1.2.0"

    # Promote QA flow to PRD
    prd_flow = tmp_db.promote_flow(
        source_flow_id=qa_flow.id,
        target_environment="prd",
        target_version="v2.0.0",
    )
    assert prd_flow.environment == "prd"
    assert prd_flow.version == "v2.0.0"
    assert prd_flow.source_flow_id == qa_flow.id


@pytest.mark.asyncio
async def test_flow_runner_environment_resolution():
    flow = FlowModel(
        id="flow-runner-env",
        name="Env Runner",
        environment="qa",
        nodes=[
            NodeModel(
                id="http-1",
                type="HttpRequestComponent",
                data={
                    "inputs": {
                        "url": "https://{{API_URL}}/users",
                        "auth_token": "{{API_KEY}}",
                    }
                },
            )
        ],
        edges=[],
    )

    class MockDB:
        def get_all_resolved_variables(self, flow_id, environment="dev"):
            if environment == "qa":
                return {
                    "API_URL": "qa.api.com",
                    "API_KEY": "qa-secret-key",
                }
            return {
                "API_URL": "dev.api.com",
                "API_KEY": "dev-secret-key",
            }

    runner = FlowRunner(flow=flow, db_manager=MockDB(), environment="qa")
    resolved_inputs = runner._resolve_node_inputs("http-1")
    assert resolved_inputs["url"] == "https://qa.api.com/users"
    assert resolved_inputs["auth_token"] == "qa-secret-key"


@pytest.mark.asyncio
async def test_api_routes_folders_and_environments():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        # Create flow in folder 'Financeiro' and env 'dev'
        res = await ac.post(
            "/api/v1/flows",
            json={
                "id": "api-fin-1",
                "name": "Financeiro Workflow",
                "folder": "Financeiro",
                "environment": "dev",
                "version": "v1.0.0",
                "nodes": [],
                "edges": [],
            },
        )
        assert res.status_code == 201
        created = res.json()
        assert created["folder"] == "Financeiro"
        assert created["environment"] == "dev"

        # List with folder filter
        res_list = await ac.get("/api/v1/flows?folder=Financeiro")
        assert res_list.status_code == 200
        flows = res_list.json()
        assert any(f["id"] == "api-fin-1" for f in flows)

        # Promote to QA
        res_promote = await ac.post(
            "/api/v1/flows/api-fin-1/promote",
            json={"target_environment": "qa", "target_version": "v1.1.0"},
        )
        assert res_promote.status_code == 200
        promoted = res_promote.json()
        assert promoted["environment"] == "qa"
        assert promoted["version"] == "v1.1.0"
        assert promoted["source_flow_id"] == "api-fin-1"
