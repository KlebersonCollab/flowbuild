from backend.app.components.builtins.actions import (
    HttpRequestComponent,
    JsonTransformComponent,
    PaginatedHttpComponent,
    PythonScriptComponent,
)
from backend.app.components.builtins.logic import (
    DelayComponent,
    IfConditionComponent,
)
from backend.app.components.builtins.triggers import (
    CronTriggerComponent,
    ManualTriggerComponent,
    WebhookTriggerComponent,
)
from backend.app.components.builtins.variables import (
    VariableComponent,
)
from backend.app.components.registry import get_registry


def register_all_builtins() -> None:
    registry = get_registry()
    registry.register(ManualTriggerComponent)
    registry.register(WebhookTriggerComponent)
    registry.register(CronTriggerComponent)
    registry.register(HttpRequestComponent)
    registry.register(PaginatedHttpComponent)
    registry.register(PythonScriptComponent)
    registry.register(JsonTransformComponent)
    registry.register(IfConditionComponent)
    registry.register(DelayComponent)
    registry.register(VariableComponent)


__all__ = [
    "CronTriggerComponent",
    "DelayComponent",
    "HttpRequestComponent",
    "IfConditionComponent",
    "JsonTransformComponent",
    "ManualTriggerComponent",
    "PaginatedHttpComponent",
    "PythonScriptComponent",
    "VariableComponent",
    "WebhookTriggerComponent",
    "register_all_builtins",
]
