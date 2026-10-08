import asyncio
from typing import Any, ClassVar

from backend.app.components.base import BaseComponent
from backend.app.components.inputs import (
    BaseInput,
    DictInput,
    FloatInput,
    SelectInput,
    StrInput,
)
from backend.app.components.outputs import Output


class IfConditionComponent(BaseComponent):
    name: ClassVar[str] = "IfConditionComponent"
    display_name: ClassVar[str] = "IF Condition"
    category: ClassVar[str] = "Logic"
    description: ClassVar[str] = "Evaluates an expression against input data and routes to True or False branch."
    icon: ClassVar[str] = "git-branch"

    inputs: ClassVar[list[BaseInput]] = [
        DictInput(name="input_data", label="Incoming Data", required=True),
        StrInput(
            name="expression",
            label="Condition Expression",
            placeholder="data.get('status') == 'active'",
            default="bool(data)",
            required=True,
        ),
    ]

    outputs: ClassVar[list[Output]] = [
        Output(name="true_branch", label="True Branch (Condition Met)", type="dict", method="get_true_branch"),
        Output(name="false_branch", label="False Branch (Condition Not Met)", type="dict", method="get_false_branch"),
        Output(name="result", label="Result (Boolean)", type="bool", method="get_result"),
        Output(name="branch", label="Active Branch ('true' or 'false')", type="str", method="get_branch"),
    ]

    def __init__(self, inputs: dict[str, Any] | None = None):
        super().__init__(inputs)
        self._last_result: bool = False
        self._last_data: Any = None
        self._last_branch: str = "false"

    async def execute(self, **kwargs: Any) -> dict[str, Any]:
        if kwargs:
            self._raw_inputs.update(kwargs)
        return await self.evaluate_condition()

    async def evaluate_condition(self) -> dict[str, Any]:
        inp = self.get_inputs()
        data = inp.get("input_data", {})
        expr = inp.get("expression", "bool(data)")

        safe_globals = {
            "__builtins__": {
                "bool": bool,
                "int": int,
                "float": float,
                "str": str,
                "len": len,
                "list": list,
                "dict": dict,
                "sum": sum,
                "max": max,
                "min": min,
                "isinstance": isinstance,
                "True": True,
                "False": False,
                "None": None,
            }
        }
        safe_locals = {"data": data}

        try:
            res = bool(eval(expr, safe_globals, safe_locals))
        except Exception:
            res = False

        self._last_result = res
        self._last_data = data
        self._last_branch = "true" if res else "false"

        return {
            "result": res,
            "branch": self._last_branch,
            "true_branch": data if res else None,
            "false_branch": None if res else data,
        }

    async def get_true_branch(self) -> Any:
        return self._last_data if self._last_result else None

    async def get_false_branch(self) -> Any:
        return None if self._last_result else self._last_data

    async def get_result(self) -> bool:
        return self._last_result

    async def get_branch(self) -> str:
        return self._last_branch


class DelayComponent(BaseComponent):
    name: ClassVar[str] = "DelayComponent"
    display_name: ClassVar[str] = "Delay / Sleep"
    category: ClassVar[str] = "Logic"
    description: ClassVar[str] = (
        "Suspends workflow execution for a specified duration before proceeding to downstream nodes."
    )
    icon: ClassVar[str] = "clock"

    inputs: ClassVar[list[BaseInput]] = [
        BaseInput(
            name="input_data",
            label="Incoming Data",
            required=False,
            default={},
            description="Incoming payload to pass through transparently to downstream nodes",
        ),
        FloatInput(
            name="delay",
            label="Duration",
            default=1.0,
            required=True,
            description="Amount of time to wait",
        ),
        SelectInput(
            name="unit",
            label="Time Unit",
            options=["seconds", "milliseconds", "minutes"],
            default="seconds",
            description="Time unit (seconds, milliseconds, minutes)",
        ),
    ]

    outputs: ClassVar[list[Output]] = [
        Output(name="data", label="Output Data", type="dict", method="get_data"),
        Output(
            name="waited_seconds",
            label="Waited Seconds",
            type="float",
            method="get_waited_seconds",
        ),
    ]

    def __init__(self, inputs: dict[str, Any] | None = None):
        super().__init__(inputs)
        self._last_data: Any = None
        self._last_waited_seconds: float = 0.0

    async def execute(self, **kwargs: Any) -> dict[str, Any]:
        if kwargs:
            self._raw_inputs.update(kwargs)
        return await self.wait()

    async def wait(self) -> dict[str, Any]:
        inp = self.get_inputs()
        data = inp.get("input_data", {})
        delay_val = inp.get("delay", 1.0)
        unit = str(inp.get("unit", "seconds")).lower()

        try:
            delay_num = float(delay_val)
        except (ValueError, TypeError):
            delay_num = 0.0

        if unit in ("milliseconds", "ms"):
            seconds = max(0.0, delay_num / 1000.0)
        elif unit in ("minutes", "min"):
            seconds = max(0.0, delay_num * 60.0)
        else:
            seconds = max(0.0, delay_num)

        if seconds > 0:
            await asyncio.sleep(seconds)

        self._last_data = data
        self._last_waited_seconds = seconds

        return {
            "data": data,
            "waited_seconds": seconds,
            "delay": delay_num,
            "unit": unit,
        }

    async def get_data(self) -> Any:
        return self._last_data

    async def get_waited_seconds(self) -> float:
        return self._last_waited_seconds


class SwitchNodeComponent(BaseComponent):
    name: ClassVar[str] = "SwitchNodeComponent"
    display_name: ClassVar[str] = "Switch / Router"
    category: ClassVar[str] = "Logic"
    description: ClassVar[str] = (
        "Routes incoming data to one of multiple branches (case_1, case_2, case_3, or default) based on value or expression evaluation."
    )
    icon: ClassVar[str] = "git-fork"

    inputs: ClassVar[list[BaseInput]] = [
        DictInput(name="input_data", label="Incoming Data", default={}),
        StrInput(
            name="expression",
            label="Switch Expression",
            placeholder="data.get('status')",
            default="data.get('status')",
            required=True,
        ),
        StrInput(
            name="case_1_value",
            label="Case 1 Match Value",
            placeholder="case_1",
            default="case_1",
        ),
        StrInput(
            name="case_2_value",
            label="Case 2 Match Value",
            placeholder="case_2",
            default="case_2",
        ),
        StrInput(
            name="case_3_value",
            label="Case 3 Match Value",
            placeholder="case_3",
            default="case_3",
        ),
    ]

    outputs: ClassVar[list[Output]] = [
        Output(name="case_1", label="Case 1 Branch", type="dict", method="get_case_1"),
        Output(name="case_2", label="Case 2 Branch", type="dict", method="get_case_2"),
        Output(name="case_3", label="Case 3 Branch", type="dict", method="get_case_3"),
        Output(name="default_branch", label="Default Branch", type="dict", method="get_default_branch"),
        Output(name="matched_case", label="Matched Case", type="str", method="get_matched_case"),
        Output(name="evaluated_value", label="Evaluated Value", type="any", method="get_evaluated_value"),
    ]

    def __init__(self, inputs: dict[str, Any] | None = None):
        super().__init__(inputs)
        self._last_data: Any = None
        self._last_matched_case: str = "default_branch"
        self._last_evaluated_val: Any = None

    async def execute(self, **kwargs: Any) -> dict[str, Any]:
        if kwargs:
            self._raw_inputs.update(kwargs)
        return await self.route()

    async def route(self) -> dict[str, Any]:
        inp = self.get_inputs()
        data = inp.get("input_data", {})
        expr = inp.get("expression", "data.get('status')")
        c1 = inp.get("case_1_value", "case_1")
        c2 = inp.get("case_2_value", "case_2")
        c3 = inp.get("case_3_value", "case_3")

        safe_globals = {
            "__builtins__": {
                "bool": bool,
                "int": int,
                "float": float,
                "str": str,
                "len": len,
                "list": list,
                "dict": dict,
                "sum": sum,
                "max": max,
                "min": min,
                "isinstance": isinstance,
                "True": True,
                "False": False,
                "None": None,
            }
        }
        safe_locals = {"data": data}

        try:
            evaluated = eval(expr, safe_globals, safe_locals)
        except Exception:
            evaluated = None

        str_eval = str(evaluated) if evaluated is not None else ""

        if str_eval == str(c1):
            matched = "case_1"
        elif str_eval == str(c2):
            matched = "case_2"
        elif str_eval == str(c3):
            matched = "case_3"
        else:
            matched = "default_branch"

        self._last_data = data
        self._last_matched_case = matched
        self._last_evaluated_val = evaluated

        return {
            "matched_case": matched,
            "evaluated_value": evaluated,
            "case_1": data if matched == "case_1" else None,
            "case_2": data if matched == "case_2" else None,
            "case_3": data if matched == "case_3" else None,
            "default_branch": data if matched == "default_branch" else None,
        }

    async def get_case_1(self) -> Any:
        return self._last_data if self._last_matched_case == "case_1" else None

    async def get_case_2(self) -> Any:
        return self._last_data if self._last_matched_case == "case_2" else None

    async def get_case_3(self) -> Any:
        return self._last_data if self._last_matched_case == "case_3" else None

    async def get_default_branch(self) -> Any:
        return self._last_data if self._last_matched_case == "default_branch" else None

    async def get_matched_case(self) -> str:
        return self._last_matched_case

    async def get_evaluated_value(self) -> Any:
        return self._last_evaluated_val
