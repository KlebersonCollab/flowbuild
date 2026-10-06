from typing import Any, ClassVar

from backend.app.components.base import BaseComponent
from backend.app.components.inputs import BaseInput, DictInput, StrInput
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
        StrInput(name="path", label="Webhook Path", default="/webhook/default"),
        StrInput(name="method", label="HTTP Method", default="POST"),
        DictInput(name="payload", label="Incoming Payload", default={}),
    ]

    outputs: ClassVar[list[Output]] = [
        Output(name="data", label="Payload Data", type="dict", method="receive"),
    ]

    async def receive(self) -> dict[str, Any]:
        inputs = self.get_inputs()
        return inputs.get("payload", {})
