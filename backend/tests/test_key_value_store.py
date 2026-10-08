import pytest
from backend.app.components.builtins.actions import KeyValueStoreComponent
from backend.app.components.builtins.triggers import ManualTriggerComponent
from backend.app.db import db_manager
from backend.app.models.flow import FlowModel, NodeModel, EdgeModel
from backend.app.engine.runner import FlowRunner


@pytest.fixture(autouse=True)
def setup_kv_table():
    db_manager.init_db()
    # Clean up test namespaces before tests
    with db_manager.engine.begin() as conn:
        conn.execute(db_manager.kv_store_table.delete().where(db_manager.kv_store_table.c.namespace.like("test_%")))


@pytest.mark.asyncio
async def test_key_value_store_set_and_get():
    # SET operation
    comp_set = KeyValueStoreComponent(
        inputs={
            "operation": "set",
            "key": "user_session",
            "value": {"theme": "dark", "lang": "pt"},
            "namespace": "test_app",
        }
    )
    res_set = await comp_set.execute()
    assert res_set["key"] == "user_session"
    assert res_set["result"] == {"theme": "dark", "lang": "pt"}
    assert res_set["found"] is False  # Didn't exist before

    # GET operation
    comp_get = KeyValueStoreComponent(
        inputs={
            "operation": "get",
            "key": "user_session",
            "namespace": "test_app",
        }
    )
    res_get = await comp_get.execute()
    assert res_get["key"] == "user_session"
    assert res_get["result"] == {"theme": "dark", "lang": "pt"}
    assert res_get["found"] is True


@pytest.mark.asyncio
async def test_key_value_store_increment():
    comp_inc1 = KeyValueStoreComponent(
        inputs={
            "operation": "increment",
            "key": "counter_test",
            "amount": 5,
            "namespace": "test_metrics",
        }
    )
    res_inc1 = await comp_inc1.execute()
    assert res_inc1["result"] == 5

    comp_inc2 = KeyValueStoreComponent(
        inputs={
            "operation": "increment",
            "key": "counter_test",
            "amount": 3,
            "namespace": "test_metrics",
        }
    )
    res_inc2 = await comp_inc2.execute()
    assert res_inc2["result"] == 8
    assert res_inc2["previous_value"] == 5


@pytest.mark.asyncio
async def test_key_value_store_fallback_default():
    comp_get = KeyValueStoreComponent(
        inputs={
            "operation": "get",
            "key": "non_existent_key",
            "namespace": "test_app",
            "default_value": "fallback_123",
        }
    )
    res = await comp_get.execute()
    assert res["found"] is False
    assert res["result"] == "fallback_123"


@pytest.mark.asyncio
async def test_key_value_store_delete():
    # Set key first
    comp_set = KeyValueStoreComponent(
        inputs={
            "operation": "set",
            "key": "temp_flag",
            "value": True,
            "namespace": "test_app",
        }
    )
    await comp_set.execute()

    # Delete key
    comp_del = KeyValueStoreComponent(
        inputs={
            "operation": "delete",
            "key": "temp_flag",
            "namespace": "test_app",
        }
    )
    res_del = await comp_del.execute()
    assert res_del["result"] is True
    assert res_del["found"] is True

    # Delete non-existent key
    res_del2 = await comp_del.execute()
    assert res_del2["result"] is False
    assert res_del2["found"] is False


@pytest.mark.asyncio
async def test_key_value_store_namespace_isolation():
    # Set same key under ns_a and ns_b
    comp_a = KeyValueStoreComponent(
        inputs={"operation": "set", "key": "env_mode", "value": "dev", "namespace": "test_ns_a"}
    )
    await comp_a.execute()

    comp_b = KeyValueStoreComponent(
        inputs={"operation": "set", "key": "env_mode", "value": "prd", "namespace": "test_ns_b"}
    )
    await comp_b.execute()

    # Get from ns_a
    comp_get_a = KeyValueStoreComponent(
        inputs={"operation": "get", "key": "env_mode", "namespace": "test_ns_a"}
    )
    res_a = await comp_get_a.execute()
    assert res_a["result"] == "dev"

    # Get from ns_b
    comp_get_b = KeyValueStoreComponent(
        inputs={"operation": "get", "key": "env_mode", "namespace": "test_ns_b"}
    )
    res_b = await comp_get_b.execute()
    assert res_b["result"] == "prd"


@pytest.mark.asyncio
async def test_key_value_store_in_flow_runner():
    flow = FlowModel(
        id="flow_kv_test",
        name="KV Test Flow",
        nodes=[
            NodeModel(
                id="trigger_1",
                type="ManualTriggerComponent",
                data={
                    "inputs": {
                        "initial_payload": {
                            "order_id": "ORD-999",
                            "status": "APPROVED",
                        }
                    }
                },
            ),
            NodeModel(
                id="kv_save",
                type="KeyValueStoreComponent",
                data={
                    "inputs": {
                        "operation": "set",
                        "key": "last_order",
                        "namespace": "test_flow",
                    }
                },
            ),
        ],
        edges=[
            EdgeModel(
                id="e1",
                source="trigger_1",
                source_handle="data",
                target="kv_save",
                target_handle="value",
            ),
        ],
    )

    runner = FlowRunner(flow)
    summary = await runner.execute_flow()

    assert summary["status"] == "completed"
    assert "kv_save" in summary["results"]
    assert summary["results"]["kv_save"]["result"]["order_id"] == "ORD-999"
    assert summary["results"]["kv_save"]["result"]["status"] == "APPROVED"
