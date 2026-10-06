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
