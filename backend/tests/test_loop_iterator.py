import pytest
from backend.app.components.builtins.logic import LoopIteratorComponent
from backend.app.components.builtins.triggers import ManualTriggerComponent
from backend.app.models.flow import FlowModel, NodeModel, EdgeModel
from backend.app.engine.runner import FlowRunner


@pytest.mark.asyncio
async def test_loop_iterator_basic_chunking():
    comp = LoopIteratorComponent(
        inputs={
            "items": [1, 2, 3, 4, 5],
            "batch_size": 2,
            "batch_index": 0,
        }
    )

    res = await comp.execute()

    assert res["total_items"] == 5
    assert res["total_batches"] == 3
    assert res["current_batch"] == [1, 2]
    assert res["has_more"] is True
    assert res["batches"] == [[1, 2], [3, 4], [5]]
    assert res["batch_info"]["batch_index"] == 0
    assert res["batch_info"]["start_index"] == 0
    assert res["batch_info"]["end_index"] == 2


@pytest.mark.asyncio
async def test_loop_iterator_batch_index_navigation():
    comp = LoopIteratorComponent(
        inputs={
            "items": ["a", "b", "c", "d"],
            "batch_size": 2,
            "batch_index": 1,
        }
    )

    res = await comp.execute()

    assert res["current_batch"] == ["c", "d"]
    assert res["has_more"] is False
    assert res["batch_info"]["batch_index"] == 1


@pytest.mark.asyncio
async def test_loop_iterator_items_path_extraction():
    comp = LoopIteratorComponent(
        inputs={
            "items": {
                "payload": {
                    "records": [{"id": 101}, {"id": 102}, {"id": 103}]
                }
            },
            "items_path": "payload.records",
            "batch_size": 2,
            "batch_index": 0,
        }
    )

    res = await comp.execute()

    assert res["total_items"] == 3
    assert res["total_batches"] == 2
    assert res["current_batch"] == [{"id": 101}, {"id": 102}]
    assert res["has_more"] is True


@pytest.mark.asyncio
async def test_loop_iterator_max_batches_limit():
    comp = LoopIteratorComponent(
        inputs={
            "items": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            "batch_size": 2,
            "max_batches": 3,
            "batch_index": 0,
        }
    )

    res = await comp.execute()

    assert res["total_batches"] == 3
    assert len(res["batches"]) == 3
    assert res["batches"] == [[1, 2], [3, 4], [5, 6]]


@pytest.mark.asyncio
async def test_loop_iterator_out_of_range_and_empty():
    # Out of range batch_index
    comp_oob = LoopIteratorComponent(
        inputs={
            "items": [1, 2],
            "batch_size": 2,
            "batch_index": 5,
        }
    )
    res_oob = await comp_oob.execute()
    assert res_oob["current_batch"] == []
    assert res_oob["has_more"] is False

    # Empty collection
    comp_empty = LoopIteratorComponent(inputs={"items": []})
    res_empty = await comp_empty.execute()
    assert res_empty["total_items"] == 0
    assert res_empty["total_batches"] == 0
    assert res_empty["current_batch"] == []
    assert res_empty["has_more"] is False


@pytest.mark.asyncio
async def test_loop_iterator_clamped_batch_size():
    # Batch size <= 0 clamps to 1
    comp = LoopIteratorComponent(
        inputs={
            "items": ["x", "y"],
            "batch_size": 0,
            "batch_index": 0,
        }
    )
    res = await comp.execute()
    assert res["total_batches"] == 2
    assert res["current_batch"] == ["x"]


@pytest.mark.asyncio
async def test_loop_iterator_in_flow_runner():
    flow = FlowModel(
        id="flow_loop_iter_1",
        name="Loop Iterator Flow",
        nodes=[
            NodeModel(
                id="trigger_1",
                type="ManualTriggerComponent",
                data={
                    "inputs": {
                        "initial_payload": {
                            "user_ids": [10, 20, 30, 40, 50]
                        }
                    }
                },
            ),
            NodeModel(
                id="iterator_1",
                type="LoopIteratorComponent",
                data={
                    "inputs": {
                        "batch_size": 3,
                        "batch_index": 0,
                    }
                },
            ),
        ],
        edges=[
            EdgeModel(
                id="e1",
                source="trigger_1",
                source_handle="data",
                target="iterator_1",
                target_handle="items",
            ),
        ],
    )

    runner = FlowRunner(flow)
    summary = await runner.execute_flow()

    assert summary["status"] == "completed"
    assert "iterator_1" in summary["results"]
    it_res = summary["results"]["iterator_1"]
    assert it_res["total_items"] == 5
    assert it_res["total_batches"] == 2
    assert it_res["current_batch"] == [10, 20, 30]
    assert it_res["has_more"] is True
