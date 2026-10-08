import pytest

from backend.app.components.builtins.actions import DataFilterComponent, PythonScriptComponent
from backend.app.components.builtins.triggers import ManualTriggerComponent
from backend.app.components.registry import ComponentRegistry
from backend.app.engine.runner import FlowRunner
from backend.app.models.flow import EdgeModel, FlowModel, NodeModel


@pytest.mark.asyncio
async def test_data_filter_equals_and_counts():
    items = [
        {"id": 1, "status": "active", "tier": "gold"},
        {"id": 2, "status": "inactive", "tier": "silver"},
        {"id": 3, "status": "active", "tier": "bronze"},
    ]
    comp = DataFilterComponent(
        inputs={
            "input_data": items,
            "field": "status",
            "operator": "equals",
            "value": "active",
        }
    )
    res = await comp.execute()

    assert res["count"] == 2
    assert res["total_count"] == 3
    assert len(res["filtered_items"]) == 2
    assert len(res["discarded_items"]) == 1
    assert [i["id"] for i in res["filtered_items"]] == [1, 3]
    assert res["discarded_items"][0]["id"] == 2


@pytest.mark.asyncio
async def test_data_filter_numeric_comparisons():
    items = [
        {"product": "A", "price": 10},
        {"product": "B", "price": 50},
        {"product": "C", "price": 100},
    ]
    # greater_than
    comp_gt = DataFilterComponent(
        inputs={
            "input_data": items,
            "field": "price",
            "operator": "greater_than",
            "value": "40",
        }
    )
    res_gt = await comp_gt.execute()
    assert [i["product"] for i in res_gt["filtered_items"]] == ["B", "C"]

    # less_or_equal
    comp_lte = DataFilterComponent(
        inputs={
            "input_data": items,
            "field": "price",
            "operator": "less_or_equal",
            "value": "50",
        }
    )
    res_lte = await comp_lte.execute()
    assert [i["product"] for i in res_lte["filtered_items"]] == ["A", "B"]


@pytest.mark.asyncio
async def test_data_filter_contains_and_empty():
    items = [
        {"name": "Alice", "tags": ["admin", "staff"], "note": ""},
        {"name": "Bob", "tags": ["client"], "note": "VIP client"},
        {"name": "Charlie", "tags": [], "note": None},
    ]
    # contains
    comp_contains = DataFilterComponent(
        inputs={
            "input_data": items,
            "field": "tags",
            "operator": "contains",
            "value": "admin",
        }
    )
    res_contains = await comp_contains.execute()
    assert len(res_contains["filtered_items"]) == 1
    assert res_contains["filtered_items"][0]["name"] == "Alice"

    # is_empty
    comp_empty = DataFilterComponent(
        inputs={
            "input_data": items,
            "field": "note",
            "operator": "is_empty",
        }
    )
    res_empty = await comp_empty.execute()
    assert len(res_empty["filtered_items"]) == 2
    assert [i["name"] for i in res_empty["filtered_items"]] == ["Alice", "Charlie"]


@pytest.mark.asyncio
async def test_data_filter_items_path_extraction():
    payload = {
        "status": "success",
        "results": {
            "users": [
                {"id": 1, "enabled": True},
                {"id": 2, "enabled": False},
            ]
        },
    }
    comp = DataFilterComponent(
        inputs={
            "input_data": payload,
            "items_path": "results.users",
            "field": "enabled",
            "operator": "equals",
            "value": "true",
        }
    )
    res = await comp.execute()
    assert res["count"] == 1
    assert res["filtered_items"][0]["id"] == 1


@pytest.mark.asyncio
async def test_data_filter_custom_expression():
    items = [
        {"sku": "P1", "qty": 10, "cost": 5},
        {"sku": "P2", "qty": 2, "cost": 100},
        {"sku": "P3", "qty": 0, "cost": 20},
    ]
    comp = DataFilterComponent(
        inputs={
            "input_data": items,
            "operator": "expression",
            "custom_expression": "item.get('qty', 0) * item.get('cost', 0) >= 50",
        }
    )
    res = await comp.execute()
    assert [i["sku"] for i in res["filtered_items"]] == ["P1", "P2"]


@pytest.mark.asyncio
async def test_flow_runner_data_filter_pipeline():
    registry = ComponentRegistry()
    registry.register(ManualTriggerComponent)
    registry.register(DataFilterComponent)
    registry.register(PythonScriptComponent)

    flow = FlowModel(
        id="flow_test_data_filter",
        name="Data Filter Pipeline Test",
        nodes=[
            NodeModel(
                id="node_trigger",
                type="ManualTriggerComponent",
                position={"x": 0, "y": 0},
                data={
                    "inputs": {
                        "initial_payload": {
                            "orders": [
                                {"id": "ord_1", "status": "approved", "total": 120},
                                {"id": "ord_2", "status": "rejected", "total": 45},
                                {"id": "ord_3", "status": "approved", "total": 350},
                            ]
                        }
                    }
                },
            ),
            NodeModel(
                id="node_filter",
                type="DataFilterComponent",
                position={"x": 200, "y": 0},
                data={
                    "inputs": {
                        "items_path": "orders",
                        "field": "status",
                        "operator": "equals",
                        "value": "approved",
                    }
                },
            ),
            NodeModel(
                id="node_script",
                type="PythonScriptComponent",
                position={"x": 400, "y": 0},
                data={
                    "inputs": {
                        "code": "def run(inputs):\n    items = inputs if isinstance(inputs, list) else inputs.get('filtered_items', [])\n    return {'approved_count': len(items), 'sum': sum(i['total'] for i in items)}\n"
                    }
                },
            ),
        ],
        edges=[
            EdgeModel(
                id="edge_1",
                source="node_trigger",
                target="node_filter",
                source_handle="data",
                target_handle="input_data",
            ),
            EdgeModel(
                id="edge_2",
                source="node_filter",
                target="node_script",
                source_handle="filtered_items",
                target_handle="input_data",
            ),
        ],
    )

    runner = FlowRunner(flow=flow, registry=registry)
    async for _ in runner.execute_stream():
        pass

    filter_res = runner.context.results["node_filter"]
    assert filter_res["count"] == 2
    assert filter_res["total_count"] == 3

    script_res = runner.context.results["node_script"]
    assert script_res["approved_count"] == 2
    assert script_res["sum"] == 470
