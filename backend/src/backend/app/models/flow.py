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
    folder: str = "Geral"
    environment: str = "dev"
    version: str = "v1.0.0"
    source_flow_id: str | None = None
    nodes: list[NodeModel] = Field(default_factory=list)
    edges: list[EdgeModel] = Field(default_factory=list)


class FlowRecord(BaseModel):
    id: str
    name: str
    description: str = ""
    folder: str = "Geral"
    environment: str = "dev"
    version: str = "v1.0.0"
    source_flow_id: str | None = None
    is_active: bool = True
    flow_data: dict[str, Any] = Field(default_factory=dict)
    created_at: str = ""
    updated_at: str = ""


class FlowPromoteRequest(BaseModel):
    target_environment: str  # 'qa' or 'prd'
    target_version: str | None = None


class ExecutionRecord(BaseModel):
    id: str
    flow_id: str
    trigger_type: str = "manual"
    status: str = "running"
    started_at: str = ""
    completed_at: str | None = None
    duration_ms: float = 0.0
    error_message: str | None = None
    node_states: dict[str, Any] = Field(default_factory=dict)
    initial_payload: dict[str, Any] = Field(default_factory=dict)


class VariableRecord(BaseModel):
    id: str
    key: str
    value: str
    scope: str = "global"
    flow_id: str | None = None
    environment: str = "all"  # 'dev', 'qa', 'prd', 'all'
    is_secret: bool = False
    created_at: str = ""
    updated_at: str = ""


class VariableCreateRequest(BaseModel):
    key: str
    value: str
    scope: str = "global"
    flow_id: str | None = None
    environment: str = "all"
    is_secret: bool = False


class VariableUpdateRequest(BaseModel):
    value: str | None = None
    environment: str | None = None
    is_secret: bool | None = None

