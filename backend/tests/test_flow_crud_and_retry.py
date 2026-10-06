import pytest
from httpx import ASGITransport, AsyncClient
from backend.app.main import app
from backend.app.db import db_manager

@pytest.fixture(autouse=True)
def setup_test_db(tmp_path, monkeypatch):
    test_db_path = str(tmp_path / "test_api_flowbuild.db")
    monkeypatch.setattr(db_manager, "db_path", test_db_path)
    db_manager.init_db()

@pytest.mark.asyncio
async def test_flow_crud_api():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        flow_payload = {
            "id": "crud-flow-1",
            "name": "Integration Test Flow",
            "description": "Flow for CRUD endpoint tests",
            "nodes": [
                {
                    "id": "n1",
                    "type": "ManualTriggerComponent",
                    "position": {"x": 100, "y": 100},
                    "data": {"inputs": {"initial_payload": {"value": 10}}}
                }
            ],
            "edges": []
        }

        # 1. Create Flow
        res_create = await client.post("/api/v1/flows", json={"flow": flow_payload, "is_active": True})
        assert res_create.status_code == 201
        created_data = res_create.json()
        assert created_data["id"] == "crud-flow-1"
        assert created_data["is_active"] is True

        # 2. List Flows
        res_list = await client.get("/api/v1/flows")
        assert res_list.status_code == 200
        flows_list = res_list.json()
        assert any(f["id"] == "crud-flow-1" for f in flows_list)

        # 3. Get Flow by ID
        res_get = await client.get("/api/v1/flows/crud-flow-1")
        assert res_get.status_code == 200
        assert res_get.json()["name"] == "Integration Test Flow"

        # 4. Update Flow (toggle is_active to False)
        flow_payload["name"] = "Renamed Flow"
        res_update = await client.put("/api/v1/flows/crud-flow-1", json={"flow": flow_payload, "is_active": False})
        assert res_update.status_code == 200
        updated_data = res_update.json()
        assert updated_data["name"] == "Renamed Flow"
        assert updated_data["is_active"] is False

        # 5. Delete Flow
        res_delete = await client.delete("/api/v1/flows/crud-flow-1")
        assert res_delete.status_code == 200
        assert res_delete.json()["deleted"] is True

        # Verify not found
        res_get_deleted = await client.get("/api/v1/flows/crud-flow-1")
        assert res_get_deleted.status_code == 404

@pytest.mark.asyncio
async def test_webhook_trigger_route():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Create active flow with WebhookTriggerComponent
        webhook_flow = {
            "id": "flow-webhook-auto",
            "name": "Webhook Flow",
            "nodes": [
                {
                    "id": "wh1",
                    "type": "WebhookTriggerComponent",
                    "position": {"x": 0, "y": 0},
                    "data": {"inputs": {"path": "/webhook/payment-received"}}
                },
                {
                    "id": "t1",
                    "type": "JsonTransformComponent",
                    "position": {"x": 200, "y": 0},
                    "data": {"inputs": {"expression": "{'status': 'received', 'invoice': payload.get('invoice_id')}"}}
                }
            ],
            "edges": [
                {"id": "e1", "source": "wh1", "sourceHandle": "data", "target": "t1", "targetHandle": "input_data"}
            ]
        }

        # Save active flow
        await client.post("/api/v1/flows", json={"flow": webhook_flow, "is_active": True})

        # Trigger webhook
        wh_res = await client.post(
            "/api/v1/webhooks/payment-received",
            json={"invoice_id": "INV-9988", "amount": 250.0}
        )
        assert wh_res.status_code == 200
        data = wh_res.json()
        assert data["status"] == "completed"
        assert data["results"]["t1"]["invoice"] == "INV-9988"

@pytest.mark.asyncio
async def test_freeze_vs_unfreeze_retry():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        flow = {
            "id": "flow-retry-test",
            "name": "Retry Flow",
            "nodes": [
                {
                    "id": "n1",
                    "type": "ManualTriggerComponent",
                    "position": {"x": 0, "y": 0},
                    "data": {"inputs": {"initial_payload": {"start": 100}}}
                },
                {
                    "id": "n2",
                    "type": "JsonTransformComponent",
                    "position": {"x": 200, "y": 0},
                    "data": {"inputs": {"expression": "payload['start'] * 2"}}
                }
            ],
            "edges": [
                {"id": "e1", "source": "n1", "sourceHandle": "data", "target": "n2", "targetHandle": "input_data"}
            ]
        }

        # 1. Execute flow initially
        exec_res = await client.post("/api/v1/flows/execute", json=flow)
        assert exec_res.status_code == 200
        first_summary = exec_res.json()
        assert first_summary["status"] == "completed"

        # Record mock failure in execution history
        db_manager.record_execution(
            execution_id="exec-failed-1",
            flow_id="flow-retry-test",
            status="failed",
            node_states={
                "n1": {"status": "completed", "output": {"start": 100}},
                "n2": {"status": "failed", "error": "Simulated error"}
            },
            initial_payload={"start": 100}
        )
        db_manager.create_flow(flow, is_active=True)

        # 2. Test Freeze Retry: Re-runs injecting frozen output for n1
        freeze_res = await client.post("/api/v1/executions/exec-failed-1/retry?mode=freeze")
        assert freeze_res.status_code == 200
        freeze_data = freeze_res.json()
        assert freeze_data["status"] == "completed"
        assert freeze_data["results"]["n2"] == 200

        # 3. Test Unfreeze Retry: Re-runs from scratch
        unfreeze_res = await client.post("/api/v1/executions/exec-failed-1/retry?mode=unfreeze")
        assert unfreeze_res.status_code == 200
        unfreeze_data = unfreeze_res.json()
        assert unfreeze_data["status"] == "completed"
        assert unfreeze_data["results"]["n2"] == 200
