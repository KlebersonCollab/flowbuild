import pytest
from backend.app.components.builtins.actions import CsvParserComponent
from backend.app.components.builtins.triggers import ManualTriggerComponent
from backend.app.models.flow import FlowModel, NodeModel, EdgeModel
from backend.app.engine.runner import FlowRunner


@pytest.mark.asyncio
async def test_csv_parser_parse_mode_with_headers():
    comp = CsvParserComponent(
        inputs={
            "mode": "parse",
            "csv_data": "id,name,role\n1,Alice,Engineer\n2,Bob,Designer\n",
            "delimiter": ",",
            "has_headers": True,
        }
    )

    res = await comp.execute()

    assert res["row_count"] == 2
    assert res["headers"] == ["id", "name", "role"]
    assert res["data"] == [
        {"id": "1", "name": "Alice", "role": "Engineer"},
        {"id": "2", "name": "Bob", "role": "Designer"},
    ]


@pytest.mark.asyncio
async def test_csv_parser_parse_custom_delimiter_and_quotes():
    comp = CsvParserComponent(
        inputs={
            "mode": "parse",
            "csv_data": 'code;description\nA1;"Item with; semicolon"\nB2;Standard item\n',
            "delimiter": ";",
            "has_headers": True,
        }
    )

    res = await comp.execute()

    assert res["row_count"] == 2
    assert res["headers"] == ["code", "description"]
    assert res["data"][0]["description"] == "Item with; semicolon"
    assert res["data"][1]["code"] == "B2"


@pytest.mark.asyncio
async def test_csv_parser_generate_mode():
    comp = CsvParserComponent(
        inputs={
            "mode": "generate",
            "json_data": [
                {"name": "Server 1", "status": "UP"},
                {"name": "Server 2", "status": "DOWN"},
            ],
            "delimiter": ",",
        }
    )

    res = await comp.execute()

    assert res["row_count"] == 2
    assert res["headers"] == ["name", "status"]
    csv_str = res["data"]
    assert "name,status" in csv_str
    assert "Server 1,UP" in csv_str
    assert "Server 2,DOWN" in csv_str


@pytest.mark.asyncio
async def test_csv_parser_generate_mode_custom_headers():
    comp = CsvParserComponent(
        inputs={
            "mode": "generate",
            "json_data": [
                {"age": 30, "name": "Charlie", "city": "NYC"},
            ],
            "custom_headers": "name,city",
        }
    )

    res = await comp.execute()

    assert res["row_count"] == 1
    assert res["headers"] == ["name", "city"]
    csv_str = res["data"]
    assert "name,city" in csv_str
    assert "Charlie,NYC" in csv_str
    assert "age" not in csv_str


@pytest.mark.asyncio
async def test_csv_parser_empty_input():
    # Empty in parse mode
    comp_parse = CsvParserComponent(inputs={"mode": "parse", "csv_data": ""})
    res_parse = await comp_parse.execute()
    assert res_parse["row_count"] == 0
    assert res_parse["data"] == []

    # Empty in generate mode
    comp_gen = CsvParserComponent(inputs={"mode": "generate", "json_data": []})
    res_gen = await comp_gen.execute()
    assert res_gen["row_count"] == 0
    assert res_gen["data"] == ""


@pytest.mark.asyncio
async def test_csv_parser_in_flow_runner():
    flow = FlowModel(
        id="flow_csv_1",
        name="CSV Parser Flow",
        nodes=[
            NodeModel(
                id="trigger_1",
                type="ManualTriggerComponent",
                data={
                    "inputs": {
                        "initial_payload": {
                            "csv_text": "dept,budget\nEng,500000\nDesign,150000\n"
                        }
                    }
                },
            ),
            NodeModel(
                id="csv_1",
                type="CsvParserComponent",
                data={
                    "inputs": {
                        "mode": "parse",
                        "delimiter": ",",
                    }
                },
            ),
        ],
        edges=[
            EdgeModel(id="e1", source="trigger_1", source_handle="data", target="csv_1", target_handle="csv_data"),
        ],
    )

    runner = FlowRunner(flow)
    summary = await runner.execute_flow()

    assert summary["status"] == "completed"
    assert "csv_1" in summary["results"]
    csv_res = summary["results"]["csv_1"]
    assert csv_res["row_count"] == 2
    assert csv_res["data"][0]["dept"] == "Eng"
    assert csv_res["data"][1]["budget"] == "150000"
