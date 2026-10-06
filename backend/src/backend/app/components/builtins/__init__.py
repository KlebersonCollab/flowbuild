from backend.app.components.builtins.actions import (
    HttpRequestComponent,
    JsonTransformComponent,
    PythonScriptComponent,
)
from backend.app.components.builtins.triggers import (
    ManualTriggerComponent,
    WebhookTriggerComponent,
)
from backend.app.components.registry import get_registry


def register_all_builtins() -> None:
    registry = get_registry()
    registry.register(ManualTriggerComponent)
    registry.register(WebhookTriggerComponent)
    registry.register(HttpRequestComponent)
    registry.register(PythonScriptComponent)
    registry.register(JsonTransformComponent)

__all__ = [
    "HttpRequestComponent",
    "JsonTransformComponent",
    "ManualTriggerComponent",
    "PythonScriptComponent",
    "WebhookTriggerComponent",
    "register_all_builtins",
]
