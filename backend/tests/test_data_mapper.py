import pytest
from backend.app.components.builtins.actions import DataMapperComponent
from backend.app.components.builtins.triggers import ManualTriggerComponent
from backend.app.models.flow import FlowModel, NodeModel, EdgeModel
from backend.app.engine.runner import FlowRunner


@pytest.mark.asyncio
async def test_data_mapper_single_object_nested():
    comp = DataMapperComponent(
        inputs={
            "input_data": {
                "user": {
                    "id": 101,
                    "profile": {
                        "firstName": "John",
                        "lastName": "Doe",
                    },
                }
            },
            "mapping": {
                "id": "user.id",
                "first_name": "user.profile.firstName",
                "last_name": "user.profile.lastName",
            },
        }
    )

    result = await comp.execute()

    assert result["mapped_count"] == 1
    assert result["output_data"] == {
        "id": 101,
        "first_name": "John",
        "last_name": "Doe",
    }


@pytest.mark.asyncio
async def test_data_mapper_array_with_items_path():
    comp = DataMapperComponent(
        inputs={
            "input_data": {
                "results": [
                    {"sku": "A1", "price": 10.5},
                    {"sku": "B2", "price": 20.0},
                ]
            },
            "items_path": "results",
            "mapping": {
                "product": "sku",
                "cost": "price",
            },
        }
    )

    result = await comp.execute()

    assert result["mapped_count"] == 2
    assert result["output_data"] == [
        {"product": "A1", "cost": 10.5},
        {"product": "B2", "cost": 20.0},
    ]


@pytest.mark.asyncio
async def test_data_mapper_array_indexing():
    comp = DataMapperComponent(
        inputs={
            "input_data": {
                "tags": ["admin", "developer"],
                "data": {"items": [100, 200]},
            },
            "mapping": {
                "first_tag": "tags.0",
                "second_tag": "tags.1",
                "first_val": "data.items.0",
            },
        }
    )

    result = await comp.execute()

    assert result["output_data"] == {
        "first_tag": "admin",
        "second_tag": "developer",
        "first_val": 100,
    }


@pytest.mark.asyncio
async def test_data_mapper_pass_unmapped():
    comp = DataMapperComponent(
        inputs={
            "input_data": {
                "id": 1,
                "status": "active",
                "old_title": "Manager",
            },
            "mapping": {
                "title": "old_title",
            },
            "pass_unmapped": True,
        }
    )

    result = await comp.execute()

    assert result["output_data"] == {
        "id": 1,
        "status": "active",
        "old_title": "Manager",
        "title": "Manager",
    }


@pytest.mark.asyncio
async def test_data_mapper_missing_paths():
    comp = DataMapperComponent(
        inputs={
            "input_data": {"a": 1},
            "mapping": {
                "b": "missing.deep.path",
                "c": "a",
            },
        }
    )

    result = await comp.execute()

    assert result["output_data"] == {
        "b": None,
        "c": 1,
    }


@pytest.mark.asyncio
async def test_data_mapper_in_flow_runner():
    flow = FlowModel(
        id="flow_mapper_1",
        name="Data Mapper Flow",
        nodes=[
            NodeModel(
                id="trigger_1",
                type="ManualTriggerComponent",
                data={
                    "inputs": {
                        "initial_payload": {
                            "payload": {
                                "client_name": "Acme Corp",
                                "tier": "enterprise",
                            }
                        }
                    }
                },
            ),
            NodeModel(
                id="mapper_1",
                type="DataMapperComponent",
                data={
                    "inputs": {
                        "mapping": {
                            "client": "payload.client_name",
                            "plan": "payload.tier",
                        },
                    }
                },
            ),
        ],
        edges=[
            EdgeModel(id="e1", source="trigger_1", source_handle="data", target="mapper_1", target_handle="input_data"),
        ],
    )

    runner = FlowRunner(flow)
    summary = await runner.execute_flow()

    assert summary["status"] == "completed"
    assert "mapper_1" in summary["results"]
    mapper_result = summary["results"]["mapper_1"]
    assert mapper_result["mapped_count"] == 1
    assert mapper_result["output_data"] == {
        "client": "Acme Corp",
        "plan": "enterprise",
    }
