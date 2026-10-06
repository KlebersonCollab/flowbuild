from typing import Any

import pytest
from httpx import ASGITransport, AsyncClient

from backend.app.main import app


@pytest.fixture
def test_app():
    return app


@pytest.mark.asyncio
async def test_health_check(test_app):
    async with AsyncClient(
        transport=ASGITransport(app=test_app), base_url="http://test"
    ) as client:
        resp = await client.get("/api/v1/health")
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ok"


@pytest.mark.asyncio
async def test_get_components_catalog(test_app):
    async with AsyncClient(
        transport=ASGITransport(app=test_app), base_url="http://test"
    ) as client:
        resp = await client.get("/api/v1/components")
        assert resp.status_code == 200
        catalog = resp.json()
        assert isinstance(catalog, list)
        names = [c["name"] for c in catalog]
        assert "ManualTriggerComponent" in names
        assert "HttpRequestComponent" in names
        assert "JsonTransformComponent" in names


@pytest.mark.asyncio
async def test_validate_flow_success(test_app, sample_flow_data: dict[str, Any]):
    async with AsyncClient(
        transport=ASGITransport(app=test_app), base_url="http://test"
    ) as client:
        resp = await client.post("/api/v1/flows/validate", json=sample_flow_data)
        assert resp.status_code == 200
        data = resp.json()
        assert data["valid"] is True
        assert len(data["topological_order"]) == 2


@pytest.mark.asyncio
async def test_validate_flow_cycle_detected(test_app):
    cyclic_flow = {
        "id": "flow-cycle",
        "name": "Cycle",
        "nodes": [
            {"id": "n1", "type": "ManualTriggerComponent"},
            {"id": "n2", "type": "JsonTransformComponent"},
        ],
        "edges": [
            {"id": "e1", "source": "n1", "target": "n2"},
            {"id": "e2", "source": "n2", "target": "n1"},
        ],
    }
    async with AsyncClient(
        transport=ASGITransport(app=test_app), base_url="http://test"
    ) as client:
        resp = await client.post("/api/v1/flows/validate", json=cyclic_flow)
        assert resp.status_code == 422
        data = resp.json()
        assert data["valid"] is False
        assert "Cycle detected" in data["error"]


@pytest.mark.asyncio
async def test_execute_flow_endpoint(test_app, sample_flow_data: dict[str, Any]):
    async with AsyncClient(
        transport=ASGITransport(app=test_app), base_url="http://test"
    ) as client:
        resp = await client.post("/api/v1/flows/execute", json=sample_flow_data)
        assert resp.status_code == 200
        summary = resp.json()
        assert summary["status"] == "completed"
        assert "node-trigger-1" in summary["results"]
        assert "node-transform-1" in summary["results"]
        assert summary["results"]["node-transform-1"] == "HELLO FLOWBUILD"


@pytest.mark.asyncio
async def test_variables_crud_endpoints(test_app):
    async with AsyncClient(
        transport=ASGITransport(app=test_app), base_url="http://test"
    ) as client:
        # 1. Create global variable
        resp = await client.post("/api/v1/variables", json={
            "key": "TEST_VAR",
            "value": "global_val",
            "scope": "global",
            "is_secret": False
        })
        assert resp.status_code == 201
        var_data = resp.json()
        assert var_data["key"] == "TEST_VAR"
        var_id = var_data["id"]

        # 2. List variables
        resp = await client.get("/api/v1/variables?scope=global")
        assert resp.status_code == 200
        items = resp.json()
        assert any(v["id"] == var_id for v in items)

        # 3. Create flow-scoped variable overriding global
        resp_flow = await client.post("/api/v1/variables", json={
            "key": "TEST_VAR",
            "value": "flow_override",
            "scope": "flow",
            "flow_id": "flow-test-api"
        })
        assert resp_flow.status_code == 201
        flow_var_id = resp_flow.json()["id"]

        # 4. Check resolved map
        resp_res = await client.get("/api/v1/variables/resolved?flow_id=flow-test-api")
        assert resp_res.status_code == 200
        assert resp_res.json()["TEST_VAR"] == "flow_override"

        # 5. Update variable
        resp_up = await client.put(f"/api/v1/variables/{var_id}", json={"value": "updated_val"})
        assert resp_up.status_code == 200
        assert resp_up.json()["value"] == "updated_val"

        # 6. Delete variables
        resp_del = await client.delete(f"/api/v1/variables/{var_id}")
        assert resp_del.status_code == 200
        assert resp_del.json()["deleted"] is True

        resp_del_flow = await client.delete(f"/api/v1/variables/{flow_var_id}")
        assert resp_del_flow.status_code == 200

