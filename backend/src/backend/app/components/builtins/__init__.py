from backend.app.components.builtins.actions import (
    CsvParserComponent,
    DataAggregatorComponent,
    DataFilterComponent,
    DataMapperComponent,
    DatabaseQueryComponent,
    DiscordWebhookComponent,
    EmailNotificationComponent,
    HttpRequestComponent,
    JsonTransformComponent,
    KeyValueStoreComponent,
    PaginatedHttpComponent,
    PythonScriptComponent,
    SlackWebhookComponent,
    TelegramWebhookComponent,
)
from backend.app.components.builtins.logic import (
    DelayComponent,
    IfConditionComponent,
    LoopIteratorComponent,
    SwitchNodeComponent,
    TryCatchComponent,
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
    registry.register(DataFilterComponent)
    registry.register(DataMapperComponent)
    registry.register(DataAggregatorComponent)
    registry.register(CsvParserComponent)
    registry.register(DatabaseQueryComponent)
    registry.register(KeyValueStoreComponent)
    registry.register(SlackWebhookComponent)
    registry.register(DiscordWebhookComponent)
    registry.register(TelegramWebhookComponent)
    registry.register(EmailNotificationComponent)
    registry.register(IfConditionComponent)
    registry.register(DelayComponent)
    registry.register(SwitchNodeComponent)
    registry.register(LoopIteratorComponent)
    registry.register(TryCatchComponent)
    registry.register(VariableComponent)


__all__ = [
    "CronTriggerComponent",
    "CsvParserComponent",
    "DataAggregatorComponent",
    "DataFilterComponent",
    "DataMapperComponent",
    "DatabaseQueryComponent",
    "DelayComponent",
    "DiscordWebhookComponent",
    "EmailNotificationComponent",
    "HttpRequestComponent",
    "IfConditionComponent",
    "JsonTransformComponent",
    "KeyValueStoreComponent",
    "LoopIteratorComponent",
    "ManualTriggerComponent",
    "PaginatedHttpComponent",
    "PythonScriptComponent",
    "SlackWebhookComponent",
    "SwitchNodeComponent",
    "TelegramWebhookComponent",
    "TryCatchComponent",
    "VariableComponent",
    "WebhookTriggerComponent",
    "register_all_builtins",
]
