from datetime import datetime, timezone
from typing import Any, ClassVar

from croniter import croniter

from backend.app.components.base import BaseComponent
from backend.app.components.inputs import (
    BaseInput,
    DictInput,
    SelectInput,
    StrInput,
)
from backend.app.components.outputs import Output


class ManualTriggerComponent(BaseComponent):
    name: ClassVar[str] = "ManualTriggerComponent"
    display_name: ClassVar[str] = "Manual Trigger"
    category: ClassVar[str] = "Triggers"
    description: ClassVar[str] = "Triggers the workflow manually with a custom payload."
    icon: ClassVar[str] = "play-circle"

    inputs: ClassVar[list[BaseInput]] = [
        DictInput(
            name="initial_payload",
            label="Initial Payload",
            default={},
            description="Payload data injected when flow is triggered.",
        ),
    ]

    outputs: ClassVar[list[Output]] = [
        Output(name="data", label="Payload", type="dict", method="trigger"),
    ]

    async def execute(self, **kwargs: Any) -> dict[str, Any]:
        if kwargs:
            self._raw_inputs.update(kwargs)
        return await self.trigger()

    async def trigger(self) -> dict[str, Any]:
        inputs = self.get_inputs()
        return inputs.get("initial_payload", {})


class WebhookTriggerComponent(BaseComponent):
    name: ClassVar[str] = "WebhookTriggerComponent"
    display_name: ClassVar[str] = "Webhook Trigger"
    category: ClassVar[str] = "Triggers"
    description: ClassVar[str] = "Triggers the flow upon receiving an external HTTP Webhook."
    icon: ClassVar[str] = "webhook"

    inputs: ClassVar[list[BaseInput]] = [
        StrInput(name="path", label="Webhook Path", default="/webhook/default", placeholder="/webhook/meu-endpoint"),
        SelectInput(
            name="method",
            label="HTTP Method",
            options=["POST", "GET", "PUT", "DELETE", "PATCH", "ANY"],
            default="POST",
            description="Allowed HTTP method: POST, GET, PUT, DELETE, PATCH, or ANY",
        ),
        SelectInput(
            name="auth_type",
            label="Autenticação / Segurança",
            options=["none", "api_key_header", "bearer", "api_key_query"],
            default="none",
            description="Método de proteção do webhook: Sem autenticação (none), Header customizado (api_key_header), Bearer Token (bearer) ou Query Param (api_key_query)",
        ),
        StrInput(
            name="auth_header_name",
            label="Nome do Header (se API Key)",
            default="X-API-Key",
            placeholder="X-API-Key ou X-Webhook-Token",
            description="Nome do cabeçalho HTTP onde a API key deve ser enviada",
        ),
        StrInput(
            name="auth_query_param",
            label="Nome do Query Param (se Query)",
            default="api_key",
            placeholder="api_key ou token",
            description="Nome do parâmetro de URL (?api_key=...)",
        ),
        StrInput(
            name="auth_token",
            label="Token / Segredo Esperado",
            default="",
            placeholder="Ex: minha_chave_secreta_123",
            description="Valor secreto que deve ser enviado para autorizar a chamada",
        ),
        StrInput(
            name="secret_token",
            label="Secret Token (Legado)",
            default="",
            placeholder="Opcional - compatibilidade legada",
            description="Fallback legado de token",
        ),
        DictInput(name="payload", label="Incoming Payload", default={}),
    ]

    outputs: ClassVar[list[Output]] = [
        Output(name="data", label="Payload Data", type="dict", method="receive"),
        Output(name="headers", label="Request Headers", type="dict", method="get_headers"),
    ]

    def __init__(self, inputs: dict[str, Any] | None = None):
        super().__init__(inputs)
        self._headers: dict[str, Any] = self._raw_inputs.get("_headers", {})

    async def execute(self, **kwargs: Any) -> dict[str, Any]:
        if kwargs:
            self._raw_inputs.update(kwargs)
            if "_headers" in kwargs:
                self._headers = kwargs["_headers"]
        return await self.receive()

    async def receive(self) -> dict[str, Any]:
        inputs = self.get_inputs()
        return inputs.get("payload", {})

    async def get_headers(self) -> dict[str, Any]:
        return self._headers


class CronTriggerComponent(BaseComponent):
    name: ClassVar[str] = "CronTriggerComponent"
    display_name: ClassVar[str] = "Schedule / Cron"
    category: ClassVar[str] = "Triggers"
    description: ClassVar[str] = "Triggers the flow periodically on a defined Cron schedule."
    icon: ClassVar[str] = "clock"

    inputs: ClassVar[list[BaseInput]] = [
        StrInput(name="cron_expression", label="Cron Schedule", default="*/5 * * * *", placeholder="*/5 * * * *"),
        StrInput(name="timezone_str", label="Timezone", default="UTC"),
    ]

    outputs: ClassVar[list[Output]] = [
        Output(name="payload", label="Trigger Info", type="dict", method="execute_trigger"),
    ]

    async def execute(self, **kwargs: Any) -> dict[str, Any]:
        if kwargs:
            self._raw_inputs.update(kwargs)
        return await self.execute_trigger()

    async def execute_trigger(self) -> dict[str, Any]:
        inp = self.get_inputs()
        cron_expr = inp.get("cron_expression") or "*/5 * * * *"
        now = datetime.now(timezone.utc)
        itr = croniter(cron_expr, now)
        next_dt = itr.get_next(datetime)

        return {
            "cron": cron_expr,
            "timestamp": now.isoformat(),
            "next_run": next_dt.isoformat(),
            "scheduled": True,
        }
