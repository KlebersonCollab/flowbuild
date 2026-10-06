from typing import Any, ClassVar

import httpx

from backend.app.components.base import BaseComponent
from backend.app.components.inputs import (
    BaseInput,
    CodeInput,
    DictInput,
    IntInput,
    SelectInput,
    StrInput,
)
from backend.app.components.outputs import Output


class HttpRequestComponent(BaseComponent):
    name: ClassVar[str] = "HttpRequestComponent"
    display_name: ClassVar[str] = "HTTP Request"
    category: ClassVar[str] = "Actions"
    description: ClassVar[str] = "Performs an asynchronous HTTP request to an external API."
    icon: ClassVar[str] = "globe"

    inputs: ClassVar[list[BaseInput]] = [
        SelectInput(
            name="method",
            label="HTTP Method",
            options=["GET", "POST", "PUT", "DELETE", "PATCH"],
            default="GET",
        ),
        StrInput(name="url", label="Endpoint URL", placeholder="https://api.example.com", required=True),
        DictInput(name="headers", label="Request Headers", default={}),
        DictInput(name="body", label="Request Body (JSON)", default=None),
        IntInput(name="timeout", label="Timeout (seconds)", default=30),
    ]

    outputs: ClassVar[list[Output]] = [
        Output(name="data", label="Response Body", type="dict", method="execute_request"),
        Output(name="status_code", label="Status Code", type="int", method="get_status"),
    ]

    def __init__(self, inputs: dict[str, Any] | None = None):
        super().__init__(inputs)
        self._last_status_code: int = 0

    async def execute_request(self) -> dict[str, Any]:
        inp = self.get_inputs()
        async with httpx.AsyncClient(timeout=inp["timeout"]) as client:
            resp = await client.request(
                method=inp["method"],
                url=inp["url"],
                headers=inp["headers"],
                json=inp["body"],
            )
            self._last_status_code = resp.status_code
            try:
                data = resp.json()
            except ValueError:
                data = {"text": resp.text}
            return {"data": data, "status_code": resp.status_code}

    async def get_status(self) -> int:
        return self._last_status_code


class PythonScriptComponent(BaseComponent):
    name: ClassVar[str] = "PythonScriptComponent"
    display_name: ClassVar[str] = "Python Script"
    category: ClassVar[str] = "Actions"
    description: ClassVar[str] = "Executes custom Python script with inputs and returns a dictionary."
    icon: ClassVar[str] = "code"

    inputs: ClassVar[list[BaseInput]] = [
        CodeInput(
            name="code",
            label="Python Code",
            default="def run(inputs):\n    return {'result': inputs}\n",
        ),
        DictInput(name="input_data", label="Input Data", default={}),
    ]

    outputs: ClassVar[list[Output]] = [
        Output(name="result", label="Result", type="any", method="run_script"),
    ]

    async def run_script(self) -> Any:
        inp = self.get_inputs()
        code = inp["code"]
        data = inp["input_data"]

        local_vars: dict[str, Any] = {}
        # Safe scope
        global_scope: dict[str, Any] = {
            "__builtins__": {
                "len": len,
                "str": str,
                "int": int,
                "float": float,
                "bool": bool,
                "list": list,
                "dict": dict,
                "range": range,
                "min": min,
                "max": max,
                "sum": sum,
            }
        }

        exec(code, global_scope, local_vars)  # noqa: S102
        if "run" not in local_vars or not callable(local_vars["run"]):
            raise ValueError("Script must define a 'run(inputs)' function.")

        return local_vars["run"](data)


class JsonTransformComponent(BaseComponent):
    name: ClassVar[str] = "JsonTransformComponent"
    display_name: ClassVar[str] = "JSON Transform"
    category: ClassVar[str] = "Transform"
    description: ClassVar[str] = "Evaluates an expression against an input JSON payload."
    icon: ClassVar[str] = "shuffle"

    inputs: ClassVar[list[BaseInput]] = [
        DictInput(name="input_data", label="Input JSON", default={}),
        StrInput(name="expression", label="Python Expression", default="payload"),
    ]

    outputs: ClassVar[list[Output]] = [
        Output(name="output_data", label="Transformed Output", type="any", method="transform"),
    ]

    async def transform(self) -> Any:
        inp = self.get_inputs()
        payload = inp["input_data"]
        expression = inp["expression"]

        safe_env = {
            "payload": payload,
            "len": len,
            "str": str,
            "int": int,
            "dict": dict,
            "list": list,
        }
        return eval(expression, {"__builtins__": {}}, safe_env)
