import pytest
from httpx import ASGITransport, AsyncClient

from backend.app.db import db_manager
from backend.app.main import app


@pytest.fixture(autouse=True)
def setup_db():
    db_manager.init_db()


@pytest.mark.asyncio
async def test_webhook_api_key_header_success_and_unauthorized():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        flow = {
            "id": "flow-wh-apikey",
            "name": "Webhook API Key Flow",
            "nodes": [
                {
                    "id": "wh1",
                    "type": "WebhookTriggerComponent",
                    "position": {"x": 0, "y": 0},
                    "data": {
                        "inputs": {
                            "path": "/webhook/secure-header",
                            "method": "POST",
                            "auth_type": "api_key_header",
                            "auth_header_name": "X-API-Key",
                            "auth_token": "secret_key_123",
                        }
                    },
                },
                {
                    "id": "t1",
                    "type": "JsonTransformComponent",
                    "position": {"x": 200, "y": 0},
                    "data": {"inputs": {"expression": "payload"}},
                },
            ],
            "edges": [
                {"id": "e1", "source": "wh1", "sourceHandle": "data", "target": "t1", "targetHandle": "input_data"}
            ],
        }

        await client.post("/api/v1/flows", json={"flow": flow, "is_active": True})

        # 1. Missing header -> 401
        res_missing = await client.post("/api/v1/webhooks/secure-header", json={"msg": "hello"})
        assert res_missing.status_code == 401
        assert "X-API-Key" in res_missing.json()["detail"]

        # 2. Invalid key -> 401
        res_invalid = await client.post(
            "/api/v1/webhooks/secure-header",
            headers={"X-API-Key": "wrong_key"},
            json={"msg": "hello"},
        )
        assert res_invalid.status_code == 401

        # 3. Valid key -> 200
        res_valid = await client.post(
            "/api/v1/webhooks/secure-header",
            headers={"X-API-Key": "secret_key_123"},
            json={"msg": "hello"},
        )
        assert res_valid.status_code == 200
        assert res_valid.json()["status"] == "completed"


@pytest.mark.asyncio
async def test_webhook_custom_header_name():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        flow = {
            "id": "flow-wh-custom-hdr",
            "name": "Webhook Custom Header Flow",
            "nodes": [
                {
                    "id": "wh1",
                    "type": "WebhookTriggerComponent",
                    "position": {"x": 0, "y": 0},
                    "data": {
                        "inputs": {
                            "path": "/webhook/stripe-events",
                            "method": "POST",
                            "auth_type": "api_key_header",
                            "auth_header_name": "Stripe-Signature",
                            "auth_token": "t=123,v1=sig_xyz",
                        }
                    },
                }
            ],
            "edges": [],
        }

        await client.post("/api/v1/flows", json={"flow": flow, "is_active": True})

        # Correct custom header -> 200
        res_ok = await client.post(
            "/api/v1/webhooks/stripe-events",
            headers={"Stripe-Signature": "t=123,v1=sig_xyz"},
            json={"event": "charge.succeeded"},
        )
        assert res_ok.status_code == 200

        # Wrong custom header -> 401
        res_bad = await client.post(
            "/api/v1/webhooks/stripe-events",
            headers={"Stripe-Signature": "bad"},
            json={"event": "charge.succeeded"},
        )
        assert res_bad.status_code == 401


@pytest.mark.asyncio
async def test_webhook_bearer_token():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        flow = {
            "id": "flow-wh-bearer",
            "name": "Webhook Bearer Flow",
            "nodes": [
                {
                    "id": "wh1",
                    "type": "WebhookTriggerComponent",
                    "position": {"x": 0, "y": 0},
                    "data": {
                        "inputs": {
                            "path": "/webhook/bearer-lead",
                            "method": "POST",
                            "auth_type": "bearer",
                            "auth_token": "token_bearer_super_secret",
                        }
                    },
                }
            ],
            "edges": [],
        }

        await client.post("/api/v1/flows", json={"flow": flow, "is_active": True})

        # Correct Bearer token -> 200
        res_ok = await client.post(
            "/api/v1/webhooks/bearer-lead",
            headers={"Authorization": "Bearer token_bearer_super_secret"},
            json={"lead": "Alice"},
        )
        assert res_ok.status_code == 200

        # Wrong Bearer token -> 401
        res_bad = await client.post(
            "/api/v1/webhooks/bearer-lead",
            headers={"Authorization": "Bearer wrong_token"},
            json={"lead": "Alice"},
        )
        assert res_bad.status_code == 401


@pytest.mark.asyncio
async def test_webhook_api_key_query():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        flow = {
            "id": "flow-wh-query",
            "name": "Webhook Query Token Flow",
            "nodes": [
                {
                    "id": "wh1",
                    "type": "WebhookTriggerComponent",
                    "position": {"x": 0, "y": 0},
                    "data": {
                        "inputs": {
                            "path": "/webhook/query-sync",
                            "method": "GET",
                            "auth_type": "api_key_query",
                            "auth_query_param": "api_key",
                            "auth_token": "token_query_999",
                        }
                    },
                }
            ],
            "edges": [],
        }

        await client.post("/api/v1/flows", json={"flow": flow, "is_active": True})

        # Valid query param -> 200
        res_ok = await client.get("/api/v1/webhooks/query-sync?api_key=token_query_999&order_id=45")
        assert res_ok.status_code == 200

        # Invalid or missing query param -> 401
        res_bad = await client.get("/api/v1/webhooks/query-sync?order_id=45")
        assert res_bad.status_code == 401
        assert "api_key" in res_bad.json()["detail"]


@pytest.mark.asyncio
async def test_webhook_open_none_auth():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        flow = {
            "id": "flow-wh-open",
            "name": "Webhook Open Flow",
            "nodes": [
                {
                    "id": "wh1",
                    "type": "WebhookTriggerComponent",
                    "position": {"x": 0, "y": 0},
                    "data": {
                        "inputs": {
                            "path": "/webhook/public-notify",
                            "method": "POST",
                            "auth_type": "none",
                        }
                    },
                }
            ],
            "edges": [],
        }

        await client.post("/api/v1/flows", json={"flow": flow, "is_active": True})

        res = await client.post("/api/v1/webhooks/public-notify", json={"event": "ping"})
        assert res.status_code == 200
