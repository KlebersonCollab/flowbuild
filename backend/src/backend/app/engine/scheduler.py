import asyncio
import logging
from datetime import datetime, timezone
from typing import Any

from croniter import croniter

from backend.app.db import db_manager
from backend.app.engine.dag_builder import DAGBuilder
from backend.app.engine.runner import FlowRunner
from backend.app.models.flow import FlowModel

logger = logging.getLogger("flowbuild.scheduler")


class CronSchedulerService:
    def __init__(self, check_interval_seconds: float = 5.0):
        self.check_interval_seconds = check_interval_seconds
        self._running = False
        self._task: asyncio.Task[None] | None = None
        self._last_run_times: dict[str, float] = {}

    def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._task = asyncio.create_task(self._scheduler_loop())
        logger.info("CronSchedulerService started.")

    def stop(self) -> None:
        self._running = False
        if self._task and not self._task.done():
            self._task.cancel()
        logger.info("CronSchedulerService stopped.")

    async def _scheduler_loop(self) -> None:
        while self._running:
            try:
                await self.check_and_trigger_flows()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in scheduler tick: {e}", exc_info=True)

            try:
                await asyncio.sleep(self.check_interval_seconds)
            except asyncio.CancelledError:
                break

    async def check_and_trigger_flows(self) -> list[str]:
        triggered_flows: list[str] = []
        now_dt = datetime.now(timezone.utc)
        now_ts = now_dt.timestamp()

        active_flows = db_manager.list_flows(active_only=True)
        for flow_rec in active_flows:
            flow_dict = flow_rec.flow_data
            cron_nodes = [
                n for n in flow_dict.get("nodes", [])
                if n.get("type") == "CronTriggerComponent"
            ]
            if not cron_nodes:
                continue

            for node in cron_nodes:
                inputs = node.get("data", {}).get("inputs", {})
                cron_expr = inputs.get("cron_expression") or "*/5 * * * *"

                # Check if due
                flow_key = f"{flow_rec.id}:{node.get('id')}"
                last_run = self._last_run_times.get(flow_key, 0)

                if self._is_due(cron_expr, last_run, now_ts):
                    self._last_run_times[flow_key] = now_ts
                    triggered_flows.append(flow_rec.id)
                    asyncio.create_task(self._execute_scheduled_flow(flow_dict))

        return triggered_flows

    def _is_due(self, cron_expr: str, last_run_ts: float, now_ts: float) -> bool:
        if last_run_ts == 0:
            # First observation: register current time as base to prevent burst execution
            return False

        try:
            # Check if there is a scheduled tick between last_run_ts and now_ts
            base_dt = datetime.fromtimestamp(last_run_ts, timezone.utc)
            now_dt = datetime.fromtimestamp(now_ts, timezone.utc)
            itr = croniter(cron_expr, base_dt)
            next_due = itr.get_next(datetime)
            return next_due <= now_dt
        except Exception as e:
            logger.warning(f"Invalid cron expression '{cron_expr}': {e}")
            return False

    async def _execute_scheduled_flow(self, flow_dict: dict[str, Any]) -> None:
        flow_id = flow_dict.get("id", "scheduled-flow")
        exec_id = f"exec-cron-{int(datetime.now().timestamp())}"
        start_time = datetime.now(timezone.utc).timestamp()

        db_manager.record_execution(
            execution_id=exec_id,
            flow_id=flow_id,
            trigger_type="cron",
            status="running",
            initial_payload={"scheduled_at": datetime.now(timezone.utc).isoformat()}
        )

        try:
            flow_model = FlowModel.model_validate(flow_dict)
            dag = DAGBuilder.build(flow_model)
            runner = FlowRunner(dag)
            summary = await runner.execute_flow()

            duration_ms = (datetime.now(timezone.utc).timestamp() - start_time) * 1000
            db_manager.update_execution_status(
                execution_id=exec_id,
                status=summary.status,
                duration_ms=duration_ms,
                node_states={
                    nid: {
                        "status": "completed" if nid in summary.successful_nodes else "failed",
                        "output": summary.results.get(nid),
                        "error": summary.errors.get(nid),
                    }
                    for nid in dag.nodes
                }
            )
        except Exception as e:
            duration_ms = (datetime.now(timezone.utc).timestamp() - start_time) * 1000
            db_manager.update_execution_status(
                execution_id=exec_id,
                status="failed",
                duration_ms=duration_ms,
                error_message=str(e),
            )


scheduler_service = CronSchedulerService()
