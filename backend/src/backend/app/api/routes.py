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
from backend.app.models.flow import (
    FlowModel,
    FlowPromoteRequest,
    VariableCreateRequest,
    VariableUpdateRequest,
)

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

    runner = FlowRunner(flow, environment=flow.environment, require_trigger=True)
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

    runner = FlowRunner(flow, environment=flow.environment, require_trigger=True)

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
async def list_flows(
    active_only: bool = False,
    folder: str | None = None,
    environment: str | None = None,
) -> list[dict[str, Any]]:
    flows = db_manager.list_flows(active_only=active_only, folder=folder, environment=environment)
    return [f.model_dump() for f in flows]


@router.post("/flows", status_code=201)
async def create_flow(request_data: dict[str, Any]) -> dict[str, Any]:
    flow_dict = request_data.get("flow", request_data)
    is_active = request_data.get("is_active", True)
    is_draft = request_data.get("is_draft", flow_dict.get("is_draft", False))
    record = db_manager.create_flow(flow_dict, is_active=is_active, is_draft=is_draft)
    return record.model_dump()


@router.post("/flows/{flow_id}/promote")
async def promote_flow(flow_id: str, req: FlowPromoteRequest) -> dict[str, Any]:
    record = db_manager.promote_flow(
        source_flow_id=flow_id,
        target_environment=req.target_environment,
        target_version=req.target_version,
    )
    if not record:
        raise HTTPException(status_code=404, detail="Flow not found")
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

@router.api_route("/webhooks/{webhook_path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def trigger_webhook(webhook_path: str, request: Request) -> dict[str, Any]:
    # Normalize webhook path
    clean_path = webhook_path.strip("/")
    req_method = request.method.upper()
    query_params = dict(request.query_params)

    body: dict[str, Any] = {}
    if req_method in ["POST", "PUT", "PATCH", "DELETE"]:
        try:
            raw_body = await request.json()
            if isinstance(raw_body, dict):
                body = raw_body
            elif raw_body is not None:
                body = {"data": raw_body}
        except Exception:
            body = {}

    # If body is empty, ingest query params as payload
    if not body and query_params:
        body = dict(query_params)

    headers = dict(request.headers)

    active_flows = db_manager.list_flows(active_only=True)
    target_flow = None
    target_node_id = None
    target_node_inputs: dict[str, Any] = {}
    matched_path_found = False
    expected_method = None

    for flow_rec in active_flows:
        flow_dict = flow_rec.flow_data
        for node in flow_dict.get("nodes", []):
            if node.get("type") == "WebhookTriggerComponent":
                node_inputs = node.get("data", {}).get("inputs", {})
                configured_path = node_inputs.get("path", "").strip("/")
                # Match e.g. "webhook/lead" or "lead"
                if configured_path == clean_path or configured_path.endswith(clean_path):
                    matched_path_found = True
                    configured_method = (node_inputs.get("method") or "POST").upper()
                    expected_method = configured_method
                    if configured_method in ["ANY", "*"] or configured_method == req_method:
                        target_flow = flow_dict
                        target_node_id = node.get("id")
                        target_node_inputs = node_inputs
                        break
        if target_flow:
            break

    if not target_flow:
        if matched_path_found:
            raise HTTPException(
                status_code=405,
                detail=f"Webhook configured to accept {expected_method}, but received {req_method}",
            )
        raise HTTPException(status_code=404, detail=f"No active webhook flow found matching path '{webhook_path}'")

    # Authenticate webhook request
    auth_type = target_node_inputs.get("auth_type", "none")
    auth_token = target_node_inputs.get("auth_token") or target_node_inputs.get("secret_token") or ""

    if auth_type == "api_key_header":
        header_name = target_node_inputs.get("auth_header_name") or "X-API-Key"
        client_key = request.headers.get(header_name) or request.headers.get(header_name.lower())
        if not client_key or client_key != auth_token:
            raise HTTPException(
                status_code=401,
                detail=f"Unauthorized: Invalid or missing API key in '{header_name}' header",
            )

    elif auth_type == "bearer":
        auth_header = request.headers.get("authorization") or request.headers.get("Authorization") or ""
        expected_bearer = f"Bearer {auth_token}".strip()
        if not auth_header or not auth_header.startswith("Bearer ") or auth_header.strip() != expected_bearer:
            raise HTTPException(
                status_code=401,
                detail="Unauthorized: Invalid or missing Bearer token in 'Authorization' header",
            )

    elif auth_type == "api_key_query":
        query_param_name = target_node_inputs.get("auth_query_param") or "api_key"
        client_key = request.query_params.get(query_param_name)
        if not client_key or client_key != auth_token:
            raise HTTPException(
                status_code=401,
                detail=f"Unauthorized: Invalid or missing query parameter '{query_param_name}'",
            )

    # Inject incoming body into webhook trigger node
    for node in target_flow.get("nodes", []):
        if node.get("id") == target_node_id:
            if "data" not in node:
                node["data"] = {}
            if "inputs" not in node["data"]:
                node["data"]["inputs"] = {}
            node["data"]["inputs"]["payload"] = body
            node["data"]["inputs"]["_headers"] = headers
            node["data"]["inputs"]["_method"] = req_method

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


# --- VARIABLES CRUD & RESOLUTION ---

@router.get("/variables")
async def list_variables(
    scope: str | None = None,
    flow_id: str | None = None,
    environment: str | None = None,
) -> list[dict[str, Any]]:
    records = db_manager.list_variables(scope=scope, flow_id=flow_id, environment=environment)
    return [r.model_dump() for r in records]


@router.get("/variables/resolved")
async def get_resolved_variables(
    flow_id: str | None = None,
    environment: str = "dev",
) -> dict[str, str]:
    return db_manager.get_all_resolved_variables(flow_id=flow_id, environment=environment)


@router.post("/variables", status_code=201)
async def create_variable(req: VariableCreateRequest) -> dict[str, Any]:
    if req.scope == "flow" and not req.flow_id:
        raise HTTPException(
            status_code=400,
            detail="flow_id is required for flow-scoped variables",
        )
    record = db_manager.create_variable(
        key=req.key,
        value=req.value,
        scope=req.scope,
        flow_id=req.flow_id,
        environment=req.environment,
        is_secret=req.is_secret,
    )
    return record.model_dump()


@router.get("/variables/{var_id}")
async def get_variable(var_id: str) -> dict[str, Any]:
    record = db_manager.get_variable(var_id)
    if not record:
        raise HTTPException(status_code=404, detail="Variable not found")
    return record.model_dump()


@router.put("/variables/{var_id}")
async def update_variable(
    var_id: str,
    req: VariableUpdateRequest,
) -> dict[str, Any]:
    record = db_manager.update_variable(
        var_id=var_id,
        value=req.value,
        environment=req.environment,
        is_secret=req.is_secret,
    )
    if not record:
        raise HTTPException(status_code=404, detail="Variable not found")
    return record.model_dump()


@router.delete("/variables/{var_id}")
async def delete_variable(var_id: str) -> dict[str, bool]:
    success = db_manager.delete_variable(var_id)
    if not success:
        raise HTTPException(status_code=404, detail="Variable not found")
    return {"deleted": True}

