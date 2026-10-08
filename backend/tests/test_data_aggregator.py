import pytest
from backend.app.components.builtins.actions import DataAggregatorComponent
from backend.app.components.builtins.triggers import ManualTriggerComponent
from backend.app.models.flow import FlowModel, NodeModel, EdgeModel
from backend.app.engine.runner import FlowRunner


@pytest.mark.asyncio
async def test_data_aggregator_sum_and_summary():
    comp = DataAggregatorComponent(
        inputs={
            "items": [
                {"price": 10},
                {"price": 25.5},
                {"price": 14.5},
            ],
            "field": "price",
            "operation": "sum",
        }
    )

    res = await comp.execute()

    assert res["result"] == 50.0
    assert res["count"] == 3
    assert res["summary"]["sum"] == 50.0
    assert abs(res["summary"]["avg"] - 16.6666) < 0.01
    assert res["summary"]["min"] == 10.0
    assert res["summary"]["max"] == 25.5


@pytest.mark.asyncio
async def test_data_aggregator_all_operations_primitive_list():
    comp = DataAggregatorComponent(
        inputs={
            "items": [5, 10, 15],
            "operation": "all",
        }
    )

    res = await comp.execute()

    assert res["count"] == 3
    assert res["result"]["sum"] == 30.0
    assert res["result"]["avg"] == 10.0
    assert res["result"]["min"] == 5.0
    assert res["result"]["max"] == 15.0


@pytest.mark.asyncio
async def test_data_aggregator_group_by():
    comp = DataAggregatorComponent(
        inputs={
            "items": [
                {"dept": "Sales", "salary": 3000},
                {"dept": "Dev", "salary": 5000},
                {"dept": "Sales", "salary": 4000},
            ],
            "field": "salary",
            "group_by": "dept",
            "operation": "sum",
        }
    )

    res = await comp.execute()

    assert res["count"] == 3
    grouped = res["result"]
    assert "Sales" in grouped
    assert "Dev" in grouped
    assert grouped["Sales"]["sum"] == 7000.0
    assert grouped["Sales"]["count"] == 2
    assert grouped["Sales"]["avg"] == 3500.0
    assert grouped["Dev"]["sum"] == 5000.0
    assert grouped["Dev"]["count"] == 1


@pytest.mark.asyncio
async def test_data_aggregator_concat():
    comp = DataAggregatorComponent(
        inputs={
            "items": [
                {"tag": "alpha"},
                {"tag": "beta"},
                {"tag": "gamma"},
            ],
            "field": "tag",
            "operation": "concat",
            "delimiter": " | ",
        }
    )

    res = await comp.execute()

    assert res["result"] == "alpha | beta | gamma"
    assert res["count"] == 3


@pytest.mark.asyncio
async def test_data_aggregator_null_and_missing_safety():
    comp = DataAggregatorComponent(
        inputs={
            "items": [
                {"v": 10},
                {"v": None},
                {"v": "not_a_number"},
                {"v": "20"},
                {},
            ],
            "field": "v",
            "operation": "sum",
        }
    )

    res = await comp.execute()

    assert res["result"] == 30.0
    assert res["count"] == 2
    assert res["summary"]["sum"] == 30.0
    assert res["summary"]["avg"] == 15.0


@pytest.mark.asyncio
async def test_data_aggregator_in_flow_runner():
    flow = FlowModel(
        id="flow_agg_1",
        name="Data Aggregator Flow",
        nodes=[
            NodeModel(
                id="trigger_1",
                type="ManualTriggerComponent",
                data={
                    "inputs": {
                        "initial_payload": {
                            "orders": [
                                {"amount": 100},
                                {"amount": 250},
                                {"amount": 50},
                            ]
                        }
                    }
                },
            ),
            NodeModel(
                id="agg_1",
                type="DataAggregatorComponent",
                data={
                    "inputs": {
                        "items_path": "orders",
                        "field": "amount",
                        "operation": "avg",
                    }
                },
            ),
        ],
        edges=[
            EdgeModel(id="e1", source="trigger_1", source_handle="data", target="agg_1", target_handle="items"),
        ],
    )

    runner = FlowRunner(flow)
    summary = await runner.execute_flow()

    assert summary["status"] == "completed"
    assert "agg_1" in summary["results"]
    agg_res = summary["results"]["agg_1"]
    assert agg_res["count"] == 3
    assert agg_res["result"] == 133.33333333333334
    assert agg_res["summary"]["sum"] == 400.0
