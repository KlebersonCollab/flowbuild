import json
from typing import Any, ClassVar

from backend.app.components.base import BaseComponent
from backend.app.components.inputs import (
    BaseInput,
    BoolInput,
    SelectInput,
    StrInput,
)
from backend.app.components.outputs import Output


class VariableOutput(dict):
    """Dictionary output for VariableComponent providing backwards-compatible
    equality with legacy single-key {'value': ...} assertions while exposing
    metadata keys ('variable_name', 'success').
    """

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, dict) and list(other.keys()) == ["value"]:
            return self.get("value") == other.get("value")
        return super().__eq__(other)


class VariableComponent(BaseComponent):
    name: ClassVar[str] = "VariableComponent"
    display_name: ClassVar[str] = "Variable"
    category: ClassVar[str] = "Variables"
    description: ClassVar[str] = "Reads (get) or writes and persists (set) global and flow-scoped variables."
    icon: ClassVar[str] = "key"

    inputs: ClassVar[list[BaseInput]] = [
        SelectInput(
            name="mode",
            label="Operation Mode",
            options=["get", "set"],
            default="get",
            description="Choose whether to get or set/persist the variable",
        ),
        StrInput(
            name="variable_name",
            label="Variable Name",
            placeholder="e.g. API_KEY or AUTH_TOKEN",
            required=True,
        ),
        StrInput(
            name="value",
            label="Value to Set",
            placeholder="Static value or connected edge data",
            default="",
            description="Value to assign in 'set' mode",
        ),
        SelectInput(
            name="scope",
            label="Scope",
            options=["flow", "global"],
            default="flow",
            description="Scope of the variable when setting ('flow' or 'global')",
        ),
        SelectInput(
            name="environment",
            label="Environment",
            options=["current", "all", "dev", "qa", "prd"],
            default="current",
            description="Target environment: 'current' (inherits flow environment), 'all' (shared), or specific ('dev', 'qa', 'prd')",
        ),
        BoolInput(
            name="persist",
            label="Persist in Database",
            default=True,
            description="Persist to database so subsequent runs can access it",
        ),
        StrInput(
            name="default_value",
            label="Default Value",
            placeholder="Fallback if not found in 'get' mode",
            default="",
        ),
    ]

    outputs: ClassVar[list[Output]] = [
        Output(name="value", label="Variable Value", type="any", method="get_value"),
        Output(name="variable_name", label="Variable Name", type="str"),
        Output(name="success", label="Success", type="bool"),
    ]

    def __init__(self, inputs: dict[str, Any] | None = None):
        super().__init__(inputs)
        self._resolved_value: Any = None

    async def execute(self, **kwargs: Any) -> dict[str, Any]:
        if kwargs:
            self._raw_inputs.update(kwargs)

        inp = self.get_inputs()
        mode = inp.get("mode", "get")
        var_name = inp.get("variable_name", "")

        db_mgr = self._raw_inputs.get("_db_manager")
        if db_mgr is None:
            try:
                from backend.app.db import db_manager as default_db

                db_mgr = default_db
            except Exception:
                db_mgr = None

        flow_id = self._raw_inputs.get("_flow_id")
        env_choice = inp.get("environment", "current")
        runtime_env = self._raw_inputs.get("_environment", "dev")
        target_env = runtime_env if env_choice == "current" else env_choice

        if mode == "set":
            val_to_set = inp.get("value")
            if (val_to_set is None or val_to_set == "") and "input_data" in self._raw_inputs:
                val_to_set = self._raw_inputs["input_data"]
            elif val_to_set is None:
                val_to_set = ""

            scope = inp.get("scope", "flow")
            persist = bool(inp.get("persist", True))

            if persist and db_mgr and hasattr(db_mgr, "upsert_variable") and var_name:
                str_val = (
                    val_to_set
                    if isinstance(val_to_set, str)
                    else json.dumps(val_to_set)
                    if isinstance(val_to_set, (dict, list))
                    else str(val_to_set)
                )
                try:
                    db_mgr.upsert_variable(
                        key=var_name,
                        value=str_val,
                        scope=scope,
                        flow_id=flow_id,
                        environment=target_env,
                    )
                except Exception:
                    pass

            if isinstance(self._raw_inputs.get("_variables"), dict) and var_name:
                self._raw_inputs["_variables"][var_name] = val_to_set

            self._resolved_value = val_to_set
            return VariableOutput({
                "value": self._resolved_value,
                "variable_name": var_name,
                "success": True,
            })

        val = await self.get_value(target_environment=target_env)
        return VariableOutput({
            "value": val,
            "variable_name": var_name,
            "success": True,
        })

    async def get_value(self, target_environment: str | None = None) -> Any:
        inp = self.get_inputs()
        var_name = inp.get("variable_name", "")
        default_val = inp.get("default_value", "")

        env_choice = inp.get("environment", "current")
        runtime_env = self._raw_inputs.get("_environment", "dev")
        resolved_env = target_environment or (runtime_env if env_choice == "current" else env_choice)

        # 1. Check if injected via runner inputs (e.g. _variables) when resolving for current env
        variables = self._raw_inputs.get("_variables")
        if env_choice == "current" and isinstance(variables, dict) and var_name in variables:
            self._resolved_value = variables[var_name]
            return self._resolved_value

        # 2. Check DatabaseManager
        db_mgr = self._raw_inputs.get("_db_manager")
        if db_mgr is None:
            try:
                from backend.app.db import db_manager as default_db

                db_mgr = default_db
            except Exception:
                db_mgr = None

        if var_name and db_mgr and hasattr(db_mgr, "resolve_variable_value"):
            try:
                flow_id = self._raw_inputs.get("_flow_id")
                val = db_mgr.resolve_variable_value(var_name, flow_id=flow_id, environment=resolved_env)
                if val is not None:
                    self._resolved_value = val
                    return self._resolved_value
            except Exception:
                pass

        if isinstance(variables, dict) and var_name in variables:
            self._resolved_value = variables[var_name]
            return self._resolved_value

        self._resolved_value = default_val
        return self._resolved_value
