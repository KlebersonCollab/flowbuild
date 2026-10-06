class FlowBuildError(Exception):
    """Base exception for all FlowBuild errors."""

class CyclicGraphError(FlowBuildError):
    """Raised when a cyclic dependency is detected in the flow DAG."""

class NodeExecutionError(FlowBuildError):
    """Raised when an individual node fails to execute."""
    def __init__(self, node_id: str, message: str):
        super().__init__(f"Node '{node_id}' execution failed: {message}")
        self.node_id = node_id
        self.original_message = message

class FlowValidationError(FlowBuildError):
    """Raised when flow structure or required inputs are invalid."""
