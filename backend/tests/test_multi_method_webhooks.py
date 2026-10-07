import pytest
from httpx import ASGITransport, AsyncClient

from backend.app.db import db_manager
from backend.app.main import app


@pytest.fixture(autouse=True)
def setup_db():
    db_manager.init_db()


@pytest.mark.asyncio
async def test_webhook_get_with_query_params():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        flow = {
            "id": "flow-wh-get",
            "name": "Webhook GET Flow",
            "nodes": [
                {
                    "id": "wh1",
                    "type": "WebhookTriggerComponent",
                    "position": {"x": 0, "y": 0},
                    "data": {"inputs": {"path": "/webhook/verify-lead", "method": "GET"}},
                },
                {
                    "id": "t1",
                    "type": "JsonTransformComponent",
                    "position": {"x": 200, "y": 0},
                    "data": {"inputs": {"expression": "{'code': payload.get('code'), 'origin': payload.get('source')}"}},
                },
            ],
            "edges": [
                {"id": "e1", "source": "wh1", "sourceHandle": "data", "target": "t1", "targetHandle": "input_data"}
            ],
        }

        # Save and activate flow
        await client.post("/api/v1/flows", json={"flow": flow, "is_active": True})

        # Trigger via GET with query parameters
        res = await client.get("/api/v1/webhooks/verify-lead?code=CHALLENGE_99&source=external")
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "completed"
        assert data["results"]["t1"]["code"] == "CHALLENGE_99"
        assert data["results"]["t1"]["origin"] == "external"


@pytest.mark.asyncio
async def test_webhook_post_with_json_body():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        flow = {
            "id": "flow-wh-post",
            "name": "Webhook POST Flow",
            "nodes": [
                {
                    "id": "wh1",
                    "type": "WebhookTriggerComponent",
                    "position": {"x": 0, "y": 0},
                    "data": {"inputs": {"path": "/webhook/create-item", "method": "POST"}},
                },
                {
                    "id": "t1",
                    "type": "JsonTransformComponent",
                    "position": {"x": 200, "y": 0},
                    "data": {"inputs": {"expression": "payload['item_id'] * 10"}},
                },
            ],
            "edges": [
                {"id": "e1", "source": "wh1", "sourceHandle": "data", "target": "t1", "targetHandle": "input_data"}
            ],
        }

        await client.post("/api/v1/flows", json={"flow": flow, "is_active": True})

        # Trigger via POST
        res = await client.post("/api/v1/webhooks/create-item", json={"item_id": 5})
        assert res.status_code == 200
        data = res.json()
        assert data["status"] == "completed"
        assert data["results"]["t1"] == 50


@pytest.mark.asyncio
async def test_webhook_method_mismatch_returns_405():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        flow = {
            "id": "flow-wh-post-only",
            "name": "Webhook POST Only Flow",
            "nodes": [
                {
                    "id": "wh1",
                    "type": "WebhookTriggerComponent",
                    "position": {"x": 0, "y": 0},
                    "data": {"inputs": {"path": "/webhook/strict-post", "method": "POST"}},
                }
            ],
            "edges": [],
        }

        await client.post("/api/v1/flows", json={"flow": flow, "is_active": True})

        # Trigger via GET when POST is expected
        res = await client.get("/api/v1/webhooks/strict-post")
        assert res.status_code == 405
        assert "POST" in res.json()["detail"]
        assert "GET" in res.json()["detail"]


@pytest.mark.asyncio
async def test_webhook_any_method_accepts_all_methods():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        flow = {
            "id": "flow-wh-any",
            "name": "Webhook Any Method Flow",
            "nodes": [
                {
                    "id": "wh1",
                    "type": "WebhookTriggerComponent",
                    "position": {"x": 0, "y": 0},
                    "data": {"inputs": {"path": "/webhook/flexible", "method": "ANY"}},
                },
                {
                    "id": "t1",
                    "type": "JsonTransformComponent",
                    "position": {"x": 200, "y": 0},
                    "data": {"inputs": {"expression": "payload.get('action', 'none')"}},
                },
            ],
            "edges": [
                {"id": "e1", "source": "wh1", "sourceHandle": "data", "target": "t1", "targetHandle": "input_data"}
            ],
        }

        await client.post("/api/v1/flows", json={"flow": flow, "is_active": True})

        # 1. GET
        res_get = await client.get("/api/v1/webhooks/flexible?action=read")
        assert res_get.status_code == 200
        assert res_get.json()["results"]["t1"] == "read"

        # 2. POST
        res_post = await client.post("/api/v1/webhooks/flexible", json={"action": "write"})
        assert res_post.status_code == 200
        assert res_post.json()["results"]["t1"] == "write"

        # 3. PUT
        res_put = await client.put("/api/v1/webhooks/flexible", json={"action": "update"})
        assert res_put.status_code == 200
        assert res_put.json()["results"]["t1"] == "update"

        # 4. DELETE
        res_del = await client.delete("/api/v1/webhooks/flexible?action=destroy")
        assert res_del.status_code == 200
        assert res_del.json()["results"]["t1"] == "destroy"
