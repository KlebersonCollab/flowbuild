from typing import ClassVar

import pytest

from backend.app.components.base import BaseComponent
from backend.app.components.inputs import (
    BaseInput,
    BoolInput,
    CodeInput,
    DictInput,
    IntInput,
    SelectInput,
    StrInput,
)
from backend.app.components.outputs import Output
from backend.app.components.registry import ComponentRegistry
from backend.app.components.builtins.actions import JsonTransformComponent


class MockEchoComponent(BaseComponent):
    name = "MockEchoComponent"
    display_name = "Mock Echo"
    category = "Test"
    description = "Echos the provided input"

    inputs: ClassVar[list[BaseInput]] = [
        StrInput(name="text", label="Text Message", required=True),
        IntInput(name="times", label="Repeat Times", default=1),
        BoolInput(name="uppercase", label="Uppercase", default=False),
        SelectInput(name="mode", label="Mode", options=["fast", "slow"], default="fast"),
        DictInput(name="metadata", label="Metadata", default={}),
        CodeInput(name="post_processor", label="Python Script", default=""),
    ]

    outputs: ClassVar[list[Output]] = [
        Output(name="result", label="Result Text", type="str", method="run_echo"),
    ]

    async def run_echo(self) -> str:
        data = self.get_inputs()
        msg = data["text"] * data["times"]
        return msg.upper() if data["uppercase"] else msg


def test_input_descriptors_serialization():
    str_in = StrInput(name="query", label="Query String", placeholder="type here...", required=True)
    d = str_in.to_dict()
    assert d["name"] == "query"
    assert d["type"] == "str"
    assert d["label"] == "Query String"
    assert d["placeholder"] == "type here..."
    assert d["required"] is True
    assert d["is_handle"] is True

    sel_in = SelectInput(name="method", label="HTTP Method", options=["GET", "POST"], default="GET")
    d_sel = sel_in.to_dict()
    assert d_sel["type"] == "select"
    assert d_sel["options"] == ["GET", "POST"]
    assert d_sel["default"] == "GET"


def test_output_descriptor_serialization():
    out = Output(name="output_payload", label="Payload", type="dict", method="execute")
    d = out.to_dict()
    assert d["name"] == "output_payload"
    assert d["label"] == "Payload"
    assert d["type"] == "dict"


def test_component_definition_schema():
    schema = MockEchoComponent.get_schema()
    assert schema["name"] == "MockEchoComponent"
    assert schema["displayName"] == "Mock Echo"
    assert schema["category"] == "Test"
    assert len(schema["inputs"]) == 6
    assert len(schema["outputs"]) == 1
    assert schema["outputs"][0]["name"] == "result"


@pytest.mark.asyncio
async def test_component_execution():
    comp = MockEchoComponent(inputs={"text": "hello ", "times": 2, "uppercase": True})
    result = await comp.execute()
    assert result == "HELLO HELLO "


def test_registry_registration_and_retrieval():
    registry = ComponentRegistry()
    registry.register(MockEchoComponent)

    comp_cls = registry.get("MockEchoComponent")
    assert comp_cls is MockEchoComponent

    catalog = registry.to_catalog()
    assert len(catalog) == 1
    assert catalog[0]["name"] == "MockEchoComponent"


@pytest.mark.asyncio
async def test_json_transform_with_isinstance_and_rich_builtins():
    """Verifies that JsonTransformComponent evaluates expressions with isinstance, sum, max, etc."""
    comp = JsonTransformComponent(
        inputs={
            "input_data": [
                {"name": "repo-a", "stars": 100},
                {"name": "repo-b", "stars": 250},
                "not-a-dict",
                42,
            ],
            "expression": "dict(total=len(payload), valid=[r.get('name') for r in payload if isinstance(r, dict)], max_stars=max([r.get('stars', 0) for r in payload if isinstance(r, dict)]))",
        }
    )
    result = await comp.transform()
    assert result["total"] == 4
    assert result["valid"] == ["repo-a", "repo-b"]
    assert result["max_stars"] == 250
