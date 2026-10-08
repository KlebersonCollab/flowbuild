import pytest
import sqlite3
import tempfile
import os
from backend.app.components.builtins.actions import DatabaseQueryComponent
from backend.app.components.builtins.triggers import ManualTriggerComponent
from backend.app.models.flow import FlowModel, NodeModel, EdgeModel
from backend.app.engine.runner import FlowRunner


@pytest.fixture
def temp_sqlite_db():
    temp_dir = tempfile.mkdtemp()
    db_file = os.path.join(temp_dir, "test_query.db")
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE products (id INTEGER PRIMARY KEY, name TEXT, price REAL, in_stock INTEGER)")
    cursor.execute("INSERT INTO products (name, price, in_stock) VALUES ('Laptop', 1200.50, 1)")
    cursor.execute("INSERT INTO products (name, price, in_stock) VALUES ('Mouse', 25.00, 1)")
    cursor.execute("INSERT INTO products (name, price, in_stock) VALUES ('Desk', 350.00, 0)")
    conn.commit()
    conn.close()
    yield f"sqlite:///{db_file}"
    try:
        os.remove(db_file)
        os.rmdir(temp_dir)
    except Exception:
        pass


@pytest.mark.asyncio
async def test_database_query_select_all(temp_sqlite_db):
    comp = DatabaseQueryComponent(
        inputs={
            "connection_string": temp_sqlite_db,
            "query": "SELECT id, name, price FROM products ORDER BY id ASC",
            "params": {},
            "fetch_mode": "all",
        }
    )

    res = await comp.execute()

    assert res["row_count"] == 3
    assert res["columns"] == ["id", "name", "price"]
    assert len(res["data"]) == 3
    assert res["data"][0]["name"] == "Laptop"
    assert res["data"][0]["price"] == 1200.50
    assert res["data"][1]["name"] == "Mouse"


@pytest.mark.asyncio
async def test_database_query_select_one_with_params(temp_sqlite_db):
    comp = DatabaseQueryComponent(
        inputs={
            "connection_string": temp_sqlite_db,
            "query": "SELECT id, name, price FROM products WHERE name = :product_name",
            "params": {"product_name": "Mouse"},
            "fetch_mode": "one",
        }
    )

    res = await comp.execute()

    assert res["row_count"] == 1
    assert res["columns"] == ["id", "name", "price"]
    assert res["data"]["name"] == "Mouse"
    assert res["data"]["price"] == 25.00


@pytest.mark.asyncio
async def test_database_query_select_one_not_found(temp_sqlite_db):
    comp = DatabaseQueryComponent(
        inputs={
            "connection_string": temp_sqlite_db,
            "query": "SELECT id, name FROM products WHERE name = :product_name",
            "params": {"product_name": "Keyboard"},
            "fetch_mode": "one",
        }
    )

    res = await comp.execute()

    assert res["row_count"] == 0
    assert res["data"] is None


@pytest.mark.asyncio
async def test_database_query_insert_mutation(temp_sqlite_db):
    comp = DatabaseQueryComponent(
        inputs={
            "connection_string": temp_sqlite_db,
            "query": "INSERT INTO products (name, price, in_stock) VALUES (:name, :price, :in_stock)",
            "params": {"name": "Monitor", "price": 450.00, "in_stock": 1},
            "fetch_mode": "none",
            "auto_commit": True,
        }
    )

    res = await comp.execute()

    assert res["row_count"] == 1
    assert res["data"] == []

    # Verify insertion with another query
    verify_comp = DatabaseQueryComponent(
        inputs={
            "connection_string": temp_sqlite_db,
            "query": "SELECT count(*) as total FROM products WHERE name = 'Monitor'",
            "fetch_mode": "one",
        }
    )
    verify_res = await verify_comp.execute()
    assert verify_res["data"]["total"] == 1


@pytest.mark.asyncio
async def test_database_query_default_db_fallback():
    # Empty connection string falls back to FlowBuild db_manager.engine
    comp = DatabaseQueryComponent(
        inputs={
            "connection_string": "",
            "query": "SELECT 42 as answer",
            "fetch_mode": "one",
        }
    )

    res = await comp.execute()

    assert res["row_count"] == 1
    assert res["data"]["answer"] == 42


@pytest.mark.asyncio
async def test_database_query_syntax_error():
    comp = DatabaseQueryComponent(
        inputs={
            "connection_string": "",
            "query": "SELECT FROM INVALID SYNTAX",
            "fetch_mode": "all",
        }
    )

    with pytest.raises(Exception) as exc_info:
        await comp.execute()

    assert "syntax" in str(exc_info.value).lower() or "operationalerror" in str(exc_info.value).lower() or "error" in str(exc_info.value).lower()


@pytest.mark.asyncio
async def test_database_query_in_flow_runner(temp_sqlite_db):
    flow = FlowModel(
        id="flow_db_query_1",
        name="DB Query Flow",
        nodes=[
            NodeModel(
                id="trigger_1",
                type="ManualTriggerComponent",
                data={
                    "inputs": {
                        "initial_payload": {
                            "query_params": {"target_stock": 1}
                        }
                    }
                },
            ),
            NodeModel(
                id="query_1",
                type="DatabaseQueryComponent",
                data={
                    "inputs": {
                        "connection_string": temp_sqlite_db,
                        "query": "SELECT name, price FROM products WHERE in_stock = :target_stock ORDER BY price DESC",
                        "fetch_mode": "all",
                    }
                },
            ),
        ],
        edges=[
            EdgeModel(
                id="e1",
                source="trigger_1",
                source_handle="data",
                target="query_1",
                target_handle="params",
            ),
        ],
    )

    runner = FlowRunner(flow)
    summary = await runner.execute_flow()

    assert summary["status"] == "completed"
    assert "query_1" in summary["results"]
    q_res = summary["results"]["query_1"]
    assert q_res["row_count"] == 2
    assert q_res["data"][0]["name"] == "Laptop"
    assert q_res["data"][1]["name"] == "Mouse"
