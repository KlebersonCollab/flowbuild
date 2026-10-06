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
        SelectInput(
            name="auth_type",
            label="Authentication Type",
            options=["none", "bearer", "basic", "api_key_header", "api_key_query"],
            default="none",
        ),
        StrInput(name="auth_token", label="Auth Token / API Key", placeholder="Token or secret", default=""),
        StrInput(name="auth_username", label="Basic Auth Username", placeholder="Username", default=""),
        StrInput(name="auth_password", label="Basic Auth Password", placeholder="Password", default=""),
        StrInput(name="auth_header_name", label="API Key Header Name", default="X-API-Key"),
        StrInput(name="auth_query_param", label="API Key Query Param", default="api_key"),
        DictInput(name="headers", label="Request Headers", default={}),
        DictInput(name="params", label="Query Parameters", default={}),
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

    async def execute(self, **kwargs: Any) -> dict[str, Any]:
        if kwargs:
            self._raw_inputs.update(kwargs)
        return await self.execute_request()

    async def execute_request(self) -> dict[str, Any]:
        import base64
        inp = self.get_inputs()
        headers = dict(inp.get("headers") or {})
        params = dict(inp.get("params") or {})

        auth_type = inp.get("auth_type", "none")
        token = inp.get("auth_token", "")

        if auth_type == "bearer" and token:
            headers["Authorization"] = f"Bearer {token}"
        elif auth_type == "basic":
            user = inp.get("auth_username", "")
            pw = inp.get("auth_password", "")
            creds = base64.b64encode(f"{user}:{pw}".encode()).decode()
            headers["Authorization"] = f"Basic {creds}"
        elif auth_type == "api_key_header" and token:
            hdr_name = inp.get("auth_header_name") or "X-API-Key"
            headers[hdr_name] = token
        elif auth_type == "api_key_query" and token:
            param_name = inp.get("auth_query_param") or "api_key"
            params[param_name] = token

        timeout_sec = inp.get("timeout") or 30
        async with httpx.AsyncClient(timeout=timeout_sec) as client:
            resp = await client.request(
                method=inp["method"],
                url=inp["url"],
                headers=headers,
                params=params if params else None,
                json=inp.get("body"),
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
