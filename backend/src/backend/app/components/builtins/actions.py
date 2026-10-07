import asyncio
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
        raw_headers = inp.get("headers") or {}
        headers: dict[str, str] = {}
        if isinstance(raw_headers, dict):
            for k, v in raw_headers.items():
                if v is not None and not isinstance(v, (dict, list)):
                    headers[str(k)] = str(v)
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

        def _execute_sync(c: str, d: Any) -> Any:
            exec_scope: dict[str, Any] = {
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
                    "__import__": __import__,
                }
            }
            exec(c, exec_scope)  # noqa: S102
            if "run" not in exec_scope or not callable(exec_scope["run"]):
                raise ValueError("Script must define a 'run(inputs)' function.")

            return exec_scope["run"](d)

        return await asyncio.to_thread(_execute_sync, code, data)


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
            "data": payload,
            "len": len,
            "str": str,
            "int": int,
            "float": float,
            "bool": bool,
            "dict": dict,
            "list": list,
            "set": set,
            "tuple": tuple,
            "sum": sum,
            "max": max,
            "min": min,
            "any": any,
            "all": all,
            "sorted": sorted,
            "range": range,
            "round": round,
            "enumerate": enumerate,
            "zip": zip,
            "isinstance": isinstance,
            "True": True,
            "False": False,
            "None": None,
        }
        return eval(expression, {"__builtins__": {}}, safe_env)


class PaginatedHttpComponent(BaseComponent):
    name: ClassVar[str] = "PaginatedHttpComponent"
    display_name: ClassVar[str] = "Paginated HTTP Client"
    category: ClassVar[str] = "Actions"
    description: ClassVar[str] = (
        "Iteratively fetches paginated API pages with customizable break condition "
        "and aggregates all items."
    )
    icon: ClassVar[str] = "repeat"

    inputs: ClassVar[list[BaseInput]] = [
        StrInput(name="url", label="Base URL", required=True, placeholder="https://api.example.com/items"),
        SelectInput(name="method", label="HTTP Method", options=["GET", "POST"], default="GET"),
        SelectInput(
            name="pagination_mode",
            label="Pagination Mode",
            options=["page_number", "offset_limit", "cursor"],
            default="page_number",
        ),
        StrInput(name="page_param", label="Page / Offset Param Name", default="page"),
        StrInput(name="limit_param", label="Limit / Page Size Param Name", default="limit"),
        IntInput(name="page_size", label="Page Size", default=20),
        IntInput(name="start_page", label="Starting Page / Offset", default=1),
        StrInput(
            name="items_path",
            label="Items JSON Path",
            default="items",
            description="Path to array of items (e.g. 'items', 'data', or empty for root array)",
        ),
        StrInput(
            name="cursor_path",
            label="Next Cursor JSON Path",
            default="next_cursor",
            description="Path to next cursor or next URL in response",
        ),
        StrInput(
            name="break_condition",
            label="Break Condition Expression",
            default="",
            description="Python expression evaluated per page (e.g. 'len(items) == 0' or 'total_items >= 100')",
        ),
        IntInput(name="max_pages", label="Max Pages Safety Cap", default=25),
        DictInput(name="headers", label="Request Headers", default={}),
        DictInput(name="params", label="Extra Query Parameters", default={}),
        IntInput(name="timeout", label="Timeout (seconds)", default=15),
    ]

    outputs: ClassVar[list[Output]] = [
        Output(name="all_items", label="All Collected Items", type="list", method="get_all_items"),
        Output(name="total_items", label="Total Items Count", type="int", method="get_total_items"),
        Output(name="pages_fetched", label="Pages Fetched Count", type="int", method="get_pages_fetched"),
        Output(name="last_page", label="Last Page Payload", type="any", method="get_last_page"),
        Output(name="summary", label="Execution Summary", type="dict", method="get_summary"),
    ]

    def __init__(self, inputs: dict[str, Any] | None = None):
        super().__init__(inputs)
        self._all_items: list[Any] = []
        self._total_items: int = 0
        self._pages_fetched: int = 0
        self._last_page: Any = None
        self._summary: dict[str, Any] = {}

    async def execute(self, **kwargs: Any) -> dict[str, Any]:
        if kwargs:
            self._raw_inputs.update(kwargs)
        return await self.fetch_all_pages()

    async def get_all_items(self) -> list[Any]:
        return self._all_items

    async def get_total_items(self) -> int:
        return self._total_items

    async def get_pages_fetched(self) -> int:
        return self._pages_fetched

    async def get_last_page(self) -> Any:
        return self._last_page

    async def get_summary(self) -> dict[str, Any]:
        return self._summary

    async def fetch_all_pages(self) -> dict[str, Any]:
        inp = self.get_inputs()
        base_url = str(inp.get("url", "")).strip()
        method = str(inp.get("method", "GET")).upper()
        pagination_mode = str(inp.get("pagination_mode", "page_number"))
        page_param = str(inp.get("page_param", "page"))
        limit_param = str(inp.get("limit_param", "limit"))
        page_size = int(inp.get("page_size", 20))
        start_page = int(inp.get("start_page", 1))
        items_path = str(inp.get("items_path", "items")).strip()
        cursor_path = str(inp.get("cursor_path", "next_cursor")).strip()
        break_condition = str(inp.get("break_condition", "")).strip()
        max_pages = min(max(int(inp.get("max_pages", 25)), 1), 100)
        raw_headers = inp.get("headers") or {}
        headers: dict[str, str] = {"User-Agent": "FlowBuild/1.0"}
        if isinstance(raw_headers, dict):
            for k, v in raw_headers.items():
                if v is not None and not isinstance(v, (dict, list)):
                    headers[str(k)] = str(v)
        extra_params = inp.get("params") or {}
        if not isinstance(extra_params, dict):
            extra_params = {}
        timeout = float(inp.get("timeout", 15))

        def _extract_by_path(data: Any, path: str) -> Any:
            if not path:
                return data
            parts = path.split(".")
            curr = data
            for p in parts:
                if isinstance(curr, dict):
                    curr = curr.get(p)
                else:
                    return None
            return curr

        all_items: list[Any] = []
        pages_fetched = 0
        current_page_num = start_page
        current_offset = start_page
        current_cursor = None
        last_page = None
        stop_reason = "max_pages_reached"

        async with httpx.AsyncClient(timeout=timeout) as client:
            while pages_fetched < max_pages:
                req_params: dict[str, Any] = dict(extra_params)
                if pagination_mode == "page_number":
                    req_params[page_param] = current_page_num
                    if limit_param:
                        req_params[limit_param] = page_size
                elif pagination_mode == "offset_limit":
                    req_params[page_param] = current_offset
                    if limit_param:
                        req_params[limit_param] = page_size
                elif pagination_mode == "cursor":
                    if current_cursor is not None:
                        req_params[page_param] = current_cursor

                req_kwargs: dict[str, Any] = {"headers": headers}
                if method == "GET":
                    req_kwargs["params"] = req_params
                else:
                    req_kwargs["json"] = req_params

                resp = await client.request(method, base_url, **req_kwargs)
                resp.raise_for_status()

                try:
                    page_data = resp.json()
                except Exception:
                    page_data = resp.text

                last_page = page_data
                pages_fetched += 1

                page_items = _extract_by_path(page_data, items_path)
                if page_items is None or not isinstance(page_items, list):
                    if isinstance(page_data, list):
                        page_items = page_data
                    else:
                        page_items = [page_data] if page_data else []

                all_items.extend(page_items)
                total_items = len(all_items)

                # Check user-defined break condition first
                if break_condition:
                    safe_env = {
                        "data": page_data,
                        "payload": page_data,
                        "items": page_items,
                        "all_items": all_items,
                        "page": current_page_num,
                        "offset": current_offset,
                        "pages_fetched": pages_fetched,
                        "total_items": total_items,
                        "len": len,
                        "str": str,
                        "int": int,
                        "float": float,
                        "bool": bool,
                        "dict": dict,
                        "list": list,
                        "set": set,
                        "tuple": tuple,
                        "sum": sum,
                        "max": max,
                        "min": min,
                        "any": any,
                        "all": all,
                        "sorted": sorted,
                        "range": range,
                        "round": round,
                        "isinstance": isinstance,
                        "True": True,
                        "False": False,
                        "None": None,
                    }
                    try:
                        should_break = bool(eval(break_condition, {"__builtins__": {}}, safe_env))
                    except Exception:
                        should_break = False
                    if should_break:
                        stop_reason = "break_condition_met"
                        break

                # Automatic termination logic
                if len(page_items) == 0:
                    stop_reason = "empty_items"
                    break

                if pagination_mode == "cursor":
                    next_cursor = _extract_by_path(page_data, cursor_path)
                    if not next_cursor:
                        stop_reason = "no_next_cursor"
                        break
                    current_cursor = next_cursor

                elif pagination_mode == "offset_limit":
                    if len(page_items) < page_size:
                        stop_reason = "last_partial_page"
                        break
                    current_offset += len(page_items)

                elif pagination_mode == "page_number":
                    current_page_num += 1

        self._all_items = all_items
        self._total_items = len(all_items)
        self._pages_fetched = pages_fetched
        self._last_page = last_page
        self._summary = {
            "total_items": self._total_items,
            "pages_fetched": pages_fetched,
            "stop_reason": stop_reason,
            "mode": pagination_mode,
        }

        return {
            "all_items": self._all_items,
            "total_items": self._total_items,
            "pages_fetched": self._pages_fetched,
            "last_page": self._last_page,
            "summary": self._summary,
        }

