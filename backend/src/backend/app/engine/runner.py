import re
from collections.abc import AsyncGenerator
from typing import Any

from backend.app.components.registry import ComponentRegistry, get_registry
from backend.app.engine.context import ExecutionContext
from backend.app.engine.dag_builder import DAGBuilder
from backend.app.engine.exceptions import CyclicGraphError
from backend.app.models.flow import FlowModel


class FlowRunner:
    def __init__(
        self,
        flow: FlowModel,
        registry: ComponentRegistry | None = None,
        frozen_results: dict[str, Any] | None = None,
        db_manager: Any | None = None,
        variables: dict[str, Any] | None = None,
        environment: str | None = None,
        require_trigger: bool = False,
    ):
        self.flow = flow
        self.registry = registry or get_registry()
        self.builder = DAGBuilder(flow)
        self.context = ExecutionContext(flow.id)
        self.frozen_results = frozen_results or {}
        self.db_manager = db_manager
        self.custom_variables = variables or {}
        self.environment = environment or getattr(flow, "environment", "dev") or "dev"
        self.require_trigger = require_trigger

        # Pre-seed results with frozen outputs
        for nid, val in self.frozen_results.items():
            self.context.set_result(nid, val)

    def has_trigger_node(self) -> bool:
        """Returns True if the flow contains at least one trigger node."""
        if not self.flow.nodes:
            return False
        for node in self.flow.nodes:
            comp_cls = self.registry.get(node.type)
            if comp_cls and getattr(comp_cls, "category", "") == "Triggers":
                return True
            if "trigger" in node.type.lower():
                return True
        return False

    def _get_variables_map(self) -> dict[str, Any]:
        var_map: dict[str, Any] = {}
        mgr = self.db_manager
        if mgr is None:
            try:
                from backend.app.db import db_manager as default_db

                mgr = default_db
            except Exception:
                mgr = None

        if mgr and hasattr(mgr, "get_all_resolved_variables"):
            try:
                var_map.update(
                    mgr.get_all_resolved_variables(self.flow.id, environment=self.environment)
                )
            except TypeError:
                try:
                    var_map.update(mgr.get_all_resolved_variables(self.flow.id))
                except Exception:
                    pass
            except Exception:
                pass

        var_map.update(self.custom_variables)
        return var_map

    def _interpolate_value(self, val: Any, var_map: dict[str, Any]) -> Any:
        if isinstance(val, str):

            def replacer(match: re.Match[str]) -> str:
                raw_key = match.group(1).strip()
                if raw_key in var_map:
                    return str(var_map[raw_key])
                if "." in raw_key:
                    stripped_key = raw_key.split(".", 1)[1]
                    if stripped_key in var_map:
                        return str(var_map[stripped_key])
                return match.group(0)

            return re.sub(r"\{\{\s*([a-zA-Z0-9_\.]+)\s*\}\}", replacer, val)
        elif isinstance(val, dict):
            return {k: self._interpolate_value(v, var_map) for k, v in val.items()}
        elif isinstance(val, list):
            return [self._interpolate_value(item, var_map) for item in val]
        return val

    def _resolve_node_inputs(self, node_id: str) -> dict[str, Any]:
        node = self.builder.get_node(node_id)
        if not node:
            return {}

        node_inputs = dict(node.data.get("inputs", {})) if isinstance(node.data, dict) else {}

        # Resolve upstream connections
        for edge in self.builder.get_incoming_edges(node_id):
            if edge.source in self.context.results:
                source_result = self.context.results[edge.source]
                extracted_val = source_result

                if (
                    isinstance(source_result, dict)
                    and edge.source_handle
                    and edge.source_handle in source_result
                ):
                    extracted_val = source_result[edge.source_handle]

                # Map into target handle if specified, or source_handle
                target_key = edge.target_handle or edge.source_handle or "input_data"
                node_inputs[target_key] = extracted_val
            elif edge.source in self.context.errors:
                node_inputs["_upstream_error"] = self.context.errors[edge.source]

        # Interpolate variables across inputs
        var_map = self._get_variables_map()
        interpolated = self._interpolate_value(node_inputs, var_map)
        if isinstance(interpolated, dict):
            node_inputs = interpolated

        # Inject context variables and flow id for component-level access
        node_inputs["_variables"] = var_map
        node_inputs["_flow_id"] = self.flow.id
        node_inputs["_environment"] = self.environment
        if self.db_manager:
            node_inputs["_db_manager"] = self.db_manager
        else:
            try:
                from backend.app.db import db_manager as default_db

                node_inputs["_db_manager"] = default_db
            except Exception:
                pass

        return node_inputs

    async def execute_stream(self) -> AsyncGenerator[dict[str, Any], None]:
        self.context.start()
        yield {"event": "flow_started", "flow_id": self.flow.id}

        if self.require_trigger and not self.has_trigger_node():
            err_msg = (
                "O workflow precisa de pelo menos um nó Trigger inicial "
                "(ex: ManualTriggerComponent, WebhookTriggerComponent ou CronTriggerComponent) "
                "para ser executado."
            )
            self.context.set_error("workflow_validation", err_msg)
            self.context.complete()
            yield {
                "event": "flow_failed",
                "error": err_msg,
                "summary": self.context.to_dict(),
            }
            return

        try:
            topological_order = self.builder.get_topological_order()
        except CyclicGraphError as exc:
            self.context.set_error("dag_builder", str(exc))
            self.context.complete()
            yield {"event": "flow_failed", "error": str(exc)}
            return

        for node_id in topological_order:
            node = self.builder.get_node(node_id)
            if not node:
                continue

            # If node is already resolved via frozen execution snapshot, skip re-executing
            if node_id in self.frozen_results:
                yield {
                    "event": "node_completed",
                    "node_id": node_id,
                    "output": self.frozen_results[node_id],
                    "frozen": True,
                }
                continue

            # Check if any predecessor failed
            incoming = self.builder.get_incoming_edges(node_id)
            has_failed_upstream = any(edge.source in self.context.errors for edge in incoming)
            if has_failed_upstream:
                inputs_raw = node.data.get("inputs", {}) if isinstance(node.data, dict) else {}
                catch_enabled = inputs_raw.get("catch_upstream_errors", True)
                if isinstance(catch_enabled, str):
                    catch_enabled = catch_enabled.lower() not in ("false", "0", "no")
                else:
                    catch_enabled = bool(catch_enabled)

                if node.type == "TryCatchComponent" and catch_enabled:
                    # Reset context status back to running since TryCatch intercepts and handles the error
                    self.context.status = "running"
                else:
                    self.context.errors[node_id] = "Skipped due to upstream dependency error"
                    self.context.set_skipped(node_id)
                    yield {
                        "event": "node_skipped",
                        "node_id": node_id,
                        "reason": "upstream_error",
                    }
                    continue

            # Check conditional branching and skipped upstreams
            if incoming:
                all_edges_inactive = True
                has_conditional_edge = False
                conditional_edge_inactive = False

                for edge in incoming:
                    if edge.source in self.context.skipped:
                        continue
                    if edge.source_handle in [
                        "true_branch",
                        "false_branch",
                        "case_1",
                        "case_2",
                        "case_3",
                        "default_branch",
                        "success_branch",
                        "error_branch",
                    ]:
                        has_conditional_edge = True
                        src_res = self.context.results.get(edge.source)
                        if isinstance(src_res, dict) and src_res.get(edge.source_handle) is None:
                            conditional_edge_inactive = True
                            continue
                    # Edge is active
                    all_edges_inactive = False
                    break

                if all_edges_inactive and (has_conditional_edge or any(edge.source in self.context.skipped for edge in incoming)):
                    self.context.set_skipped(node_id)
                    yield {
                        "event": "node_skipped",
                        "node_id": node_id,
                        "reason": "condition_not_met" if conditional_edge_inactive else "upstream_skipped",
                    }
                    continue

            comp_cls = self.registry.get(node.type)
            if not comp_cls:
                err_msg = f"Unknown component type '{node.type}'"
                self.context.set_error(node_id, err_msg)
                yield {"event": "node_failed", "node_id": node_id, "error": err_msg}
                continue

            yield {"event": "node_started", "node_id": node_id, "type": node.type}

            try:
                resolved_inputs = self._resolve_node_inputs(node_id)
                component = comp_cls(inputs=resolved_inputs)
                output = await component.execute()
                self.context.set_result(node_id, output)
                if isinstance(output, dict) and output.get("success") and "variable_name" in output:
                    var_name = output.get("variable_name")
                    if var_name:
                        self.custom_variables[var_name] = output.get("value")

                yield {
                    "event": "node_completed",
                    "node_id": node_id,
                    "output": output,
                }
            except Exception as exc:  # noqa: BLE001
                self.context.set_error(node_id, str(exc))
                yield {
                    "event": "node_failed",
                    "node_id": node_id,
                    "error": str(exc),
                }

        self.context.complete()
        yield {
            "event": "flow_completed",
            "flow_id": self.flow.id,
            "status": self.context.status,
            "summary": self.context.to_dict(),
        }

    async def execute_flow(self) -> dict[str, Any]:
        async for _ in self.execute_stream():
            pass
        return self.context.to_dict()

    def get_summary(self) -> dict[str, Any]:
        return self.context.to_dict()
