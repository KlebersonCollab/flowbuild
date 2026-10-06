import json
from collections.abc import AsyncGenerator
from typing import Any

from fastapi import APIRouter
from fastapi.responses import JSONResponse, StreamingResponse

from backend.app.components.registry import get_registry
from backend.app.engine.dag_builder import DAGBuilder
from backend.app.engine.exceptions import CyclicGraphError
from backend.app.engine.runner import FlowRunner
from backend.app.models.flow import FlowModel

router = APIRouter(prefix="/api/v1")


@router.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok", "version": "0.1.0"}


@router.get("/components")
async def get_components_catalog() -> list[dict[str, Any]]:
    registry = get_registry()
    return registry.to_catalog()


@router.post("/flows/validate")
async def validate_flow(flow: FlowModel) -> JSONResponse:
    try:
        builder = DAGBuilder(flow)
        topological_order = builder.get_topological_order()
        return JSONResponse(
            status_code=200,
            content={"valid": True, "topological_order": topological_order},
        )
    except CyclicGraphError as exc:
        return JSONResponse(
            status_code=422,
            content={"valid": False, "error": str(exc)},
        )


@router.post("/flows/execute")
async def execute_flow(flow: FlowModel) -> dict[str, Any]:
    runner = FlowRunner(flow)
    async for _ in runner.execute_stream():
        pass
    return runner.get_summary()


@router.post("/flows/execute/stream")
async def execute_flow_stream(flow: FlowModel) -> StreamingResponse:
    runner = FlowRunner(flow)

    async def event_generator() -> AsyncGenerator[str, None]:
        async for event in runner.execute_stream():
            yield f"data: {json.dumps(event)}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
