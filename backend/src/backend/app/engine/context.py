import time
from typing import Any


class ExecutionContext:
    def __init__(self, flow_id: str):
        self.flow_id = flow_id
        self.status: str = "pending"  # pending, running, completed, failed
        self.results: dict[str, Any] = {}
        self.errors: dict[str, str] = {}
        self.start_time: float = 0.0
        self.end_time: float = 0.0

    def start(self) -> None:
        self.status = "running"
        self.start_time = time.time()

    def set_result(self, node_id: str, output: Any) -> None:
        self.results[node_id] = output

    def set_error(self, node_id: str, error: str) -> None:
        self.errors[node_id] = error
        self.status = "failed"

    def complete(self) -> None:
        if self.status != "failed":
            self.status = "completed"
        self.end_time = time.time()

    def to_dict(self) -> dict[str, Any]:
        return {
            "flowId": self.flow_id,
            "status": self.status,
            "results": self.results,
            "errors": self.errors,
            "duration": round(self.end_time - self.start_time, 3) if self.end_time else 0.0,
        }
