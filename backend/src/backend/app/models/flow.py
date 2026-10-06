from typing import Any

from pydantic import BaseModel, Field


class NodePosition(BaseModel):
    x: float = 0.0
    y: float = 0.0

class NodeData(BaseModel):
    inputs: dict[str, Any] = Field(default_factory=dict)
    label: str | None = None

class NodeModel(BaseModel):
    id: str
    type: str
    position: dict[str, float] | NodePosition = Field(default_factory=dict)
    data: dict[str, Any] = Field(default_factory=dict)

class EdgeModel(BaseModel):
    id: str
    source: str
    source_handle: str | None = Field(default=None, alias="sourceHandle")
    target: str
    target_handle: str | None = Field(default=None, alias="targetHandle")

    model_config = {
        "populate_by_name": True,
    }

class FlowModel(BaseModel):
    id: str
    name: str
    description: str = ""
    nodes: list[NodeModel] = Field(default_factory=list)
    edges: list[EdgeModel] = Field(default_factory=list)
