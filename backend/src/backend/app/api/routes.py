import json
import uuid
from collections.abc import AsyncGenerator
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import JSONResponse, StreamingResponse

from backend.app.components.registry import get_registry
from backend.app.db import db_manager
from backend.app.engine.dag_builder import DAGBuilder
from backend.app.engine.exceptions import CyclicGraphError
from backend.app.engine.runner import FlowRunner
from backend.app.models.flow import FlowModel

router = APIRouter(prefix="/api/v1")


@router.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok", "version": "0.2.0"}


@router.get("/components")
async def get_components_catalog() -> list[dict[str, Any]]:
    registry = get_registry()
    return registry.to_catalog()


# --- FLOW VALIDATION & DIRECT EXECUTION ---

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
    exec_id = f"exec-{uuid.uuid4().hex[:8]}"
    start_ts = datetime.now(timezone.utc).timestamp()

    db_manager.record_execution(
        execution_id=exec_id,
        flow_id=flow.id,
        trigger_type="manual",
        status="running",
    )

    runner = FlowRunner(flow)
    async for _ in runner.execute_stream():
        pass
    summary = runner.get_summary()

    duration_ms = (datetime.now(timezone.utc).timestamp() - start_ts) * 1000
    node_states = {
        nid: {
            "status": "completed" if nid in summary.get("results", {}) else "failed",
            "output": summary.get("results", {}).get(nid),
            "error": summary.get("errors", {}).get(nid),
        }
        for nid in [n.id for n in flow.nodes]
    }

    db_manager.update_execution_status(
        execution_id=exec_id,
        status=summary.get("status", "completed"),
        duration_ms=duration_ms,
        node_states=node_states,
    )

    return summary


@router.post("/flows/execute/stream")
async def execute_flow_stream(flow: FlowModel) -> StreamingResponse:
    exec_id = f"exec-{uuid.uuid4().hex[:8]}"
    start_ts = datetime.now(timezone.utc).timestamp()

    db_manager.record_execution(
        execution_id=exec_id,
        flow_id=flow.id,
        trigger_type="manual",
        status="running",
    )

    runner = FlowRunner(flow)

    async def event_generator() -> AsyncGenerator[str, None]:
        captured_node_states: dict[str, Any] = {}
        async for event in runner.execute_stream():
            if event.get("event") == "node_completed" and "node_id" in event:
                captured_node_states[event["node_id"]] = {
                    "status": "completed",
                    "output": event.get("output"),
                }
            elif event.get("event") == "node_failed" and "node_id" in event:
                captured_node_states[event["node_id"]] = {
                    "status": "failed",
                    "error": event.get("error"),
                }
            yield f"data: {json.dumps(event)}\n\n"

        duration_ms = (datetime.now(timezone.utc).timestamp() - start_ts) * 1000
        summary = runner.get_summary()
        db_manager.update_execution_status(
            execution_id=exec_id,
            status=summary.get("status", "completed"),
            duration_ms=duration_ms,
            node_states=captured_node_states,
        )

    return StreamingResponse(event_generator(), media_type="text/event-stream")


# --- FLOW PERSISTENCE CRUD ---

@router.get("/flows")
async def list_flows(active_only: bool = False) -> list[dict[str, Any]]:
    flows = db_manager.list_flows(active_only=active_only)
    return [f.model_dump() for f in flows]


@router.post("/flows", status_code=201)
async def create_flow(request_data: dict[str, Any]) -> dict[str, Any]:
    flow_dict = request_data.get("flow", request_data)
    is_active = request_data.get("is_active", True)
    record = db_manager.create_flow(flow_dict, is_active=is_active)
    return record.model_dump()


@router.get("/flows/{flow_id}")
async def get_flow(flow_id: str) -> dict[str, Any]:
    record = db_manager.get_flow(flow_id)
    if not record:
        raise HTTPException(status_code=404, detail="Flow not found")
    return record.model_dump()


@router.put("/flows/{flow_id}")
async def update_flow(flow_id: str, request_data: dict[str, Any]) -> dict[str, Any]:
    flow_dict = request_data.get("flow", request_data)
    is_active = request_data.get("is_active")
    record = db_manager.update_flow(flow_id, flow_dict, is_active=is_active)
    if not record:
        raise HTTPException(status_code=404, detail="Flow not found")
    return record.model_dump()


@router.delete("/flows/{flow_id}")
async def delete_flow(flow_id: str) -> dict[str, Any]:
    deleted = db_manager.delete_flow(flow_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Flow not found")
    return {"deleted": True, "id": flow_id}


# --- WEBHOOK ROUTER ---

@router.post("/webhooks/{webhook_path:path}")
async def trigger_webhook(webhook_path: str, request: Request) -> dict[str, Any]:
    # Normalize webhook path
    clean_path = webhook_path.strip("/")
    try:
        body = await request.json()
    except Exception:
        body = {}

    headers = dict(request.headers)

    active_flows = db_manager.list_flows(active_only=True)
    target_flow = None
    target_node_id = None

    for flow_rec in active_flows:
        flow_dict = flow_rec.flow_data
        for node in flow_dict.get("nodes", []):
            if node.get("type") == "WebhookTriggerComponent":
                node_inputs = node.get("data", {}).get("inputs", {})
                configured_path = node_inputs.get("path", "").strip("/")
                # Match e.g. "webhook/lead" or "lead"
                if configured_path == clean_path or configured_path.endswith(clean_path):
                    target_flow = flow_dict
                    target_node_id = node.get("id")
                    break
        if target_flow:
            break

    if not target_flow:
        raise HTTPException(status_code=404, detail=f"No active webhook flow found matching path '{webhook_path}'")

    # Inject incoming body into webhook trigger node
    for node in target_flow.get("nodes", []):
        if node.get("id") == target_node_id:
            if "data" not in node:
                node["data"] = {}
            if "inputs" not in node["data"]:
                node["data"]["inputs"] = {}
            node["data"]["inputs"]["payload"] = body

    flow_model = FlowModel.model_validate(target_flow)
    runner = FlowRunner(flow_model)
    await runner.execute_flow()
    summary = runner.get_summary()

    # Record execution
    exec_id = f"exec-wh-{uuid.uuid4().hex[:8]}"
    db_manager.record_execution(
        execution_id=exec_id,
        flow_id=flow_model.id,
        trigger_type="webhook",
        status=summary.get("status", "completed"),
        initial_payload=body,
        node_states={
            nid: {
                "status": "completed" if nid in summary.get("results", {}) else "failed",
                "output": summary.get("results", {}).get(nid),
            }
            for nid in [n.id for n in flow_model.nodes]
        },
    )

    return summary


# --- EXECUTIONS & RETRY ENGINE (FREEZE / UNFREEZE) ---

@router.get("/executions")
async def list_executions(flow_id: str | None = None, limit: int = 50) -> list[dict[str, Any]]:
    records = db_manager.list_executions(flow_id=flow_id, limit=limit)
    return [r.model_dump() for r in records]


@router.get("/executions/{execution_id}")
async def get_execution_detail(execution_id: str) -> dict[str, Any]:
    record = db_manager.get_execution(execution_id)
    if not record:
        raise HTTPException(status_code=404, detail="Execution record not found")
    return record.model_dump()


@router.post("/executions/{execution_id}/retry")
async def retry_execution(
    execution_id: str,
    mode: str = Query("freeze", pattern="^(freeze|unfreeze)$"),
) -> dict[str, Any]:
    exec_rec = db_manager.get_execution(execution_id)
    if not exec_rec:
        raise HTTPException(status_code=404, detail="Execution record not found")

    flow_rec = db_manager.get_flow(exec_rec.flow_id)
    if not flow_rec:
        raise HTTPException(status_code=404, detail=f"Flow '{exec_rec.flow_id}' not found for retry")

    flow_model = FlowModel.model_validate(flow_rec.flow_data)

    frozen_results: dict[str, Any] = {}
    if mode == "freeze":
        # Inject previously successful node outputs into runner
        for nid, nstate in exec_rec.node_states.items():
            if isinstance(nstate, dict) and nstate.get("status") == "completed" and "output" in nstate:
                frozen_results[nid] = nstate["output"]

    runner = FlowRunner(flow_model, frozen_results=frozen_results if mode == "freeze" else None)
    await runner.execute_flow()
    summary = runner.get_summary()

    # Record retry result
    new_exec_id = f"exec-retry-{uuid.uuid4().hex[:8]}"
    db_manager.record_execution(
        execution_id=new_exec_id,
        flow_id=flow_model.id,
        trigger_type=f"retry_{mode}",
        status=summary.get("status", "completed"),
        initial_payload=exec_rec.initial_payload,
        node_states={
            nid: {
                "status": "completed" if nid in summary.get("results", {}) else "failed",
                "output": summary.get("results", {}).get(nid),
                "error": summary.get("errors", {}).get(nid),
            }
            for nid in [n.id for n in flow_model.nodes]
        },
    )

    return summary
