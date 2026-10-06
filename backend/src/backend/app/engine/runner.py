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
    ):
        self.flow = flow
        self.registry = registry or get_registry()
        self.builder = DAGBuilder(flow)
        self.context = ExecutionContext(flow.id)
        self.frozen_results = frozen_results or {}

        # Pre-seed results with frozen outputs
        for nid, val in self.frozen_results.items():
            self.context.set_result(nid, val)

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

        return node_inputs

    async def execute_stream(self) -> AsyncGenerator[dict[str, Any], None]:
        self.context.start()
        yield {"event": "flow_started", "flow_id": self.flow.id}

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
                self.context.errors[node_id] = "Skipped due to upstream dependency error"
                yield {
                    "event": "node_skipped",
                    "node_id": node_id,
                    "reason": "upstream_error",
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
