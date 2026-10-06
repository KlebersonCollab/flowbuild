from typing import Any, ClassVar

from backend.app.components.base import BaseComponent
from backend.app.components.inputs import BaseInput, StrInput
from backend.app.components.outputs import Output


class VariableComponent(BaseComponent):
    name: ClassVar[str] = "VariableComponent"
    display_name: ClassVar[str] = "Variable"
    category: ClassVar[str] = "Variables"
    description: ClassVar[str] = "Emits the resolved value of a global or flow variable."
    icon: ClassVar[str] = "key"

    inputs: ClassVar[list[BaseInput]] = [
        StrInput(
            name="variable_name",
            label="Variable Name",
            placeholder="e.g. API_KEY",
            required=True,
        ),
        StrInput(
            name="default_value",
            label="Default Value",
            placeholder="Fallback if not found",
            default="",
        ),
    ]

    outputs: ClassVar[list[Output]] = [
        Output(name="value", label="Variable Value", type="any", method="get_value"),
    ]

    def __init__(self, inputs: dict[str, Any] | None = None):
        super().__init__(inputs)
        self._resolved_value: Any = None

    async def execute(self, **kwargs: Any) -> dict[str, Any]:
        if kwargs:
            self._raw_inputs.update(kwargs)
        val = await self.get_value()
        return {"value": val}

    async def get_value(self) -> Any:
        inp = self.get_inputs()
        var_name = inp.get("variable_name", "")
        default_val = inp.get("default_value", "")

        # 1. Check if injected via runner inputs (e.g. _variables)
        variables = self._raw_inputs.get("_variables")
        if isinstance(variables, dict) and var_name in variables:
            self._resolved_value = variables[var_name]
            return self._resolved_value

        # 2. Check DatabaseManager
        if var_name:
            try:
                from backend.app.db import db_manager
                flow_id = self._raw_inputs.get("_flow_id")
                val = db_manager.resolve_variable_value(var_name, flow_id=flow_id)
                if val is not None:
                    self._resolved_value = val
                    return self._resolved_value
            except Exception:
                pass

        self._resolved_value = default_val
        return self._resolved_value
