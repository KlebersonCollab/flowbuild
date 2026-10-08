import asyncio
import csv
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import io
import smtplib
from typing import Any, ClassVar

import httpx
from sqlalchemy import create_engine, text

from backend.app.components.base import BaseComponent
from backend.app.components.inputs import (
    BaseInput,
    BoolInput,
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
                    "isinstance": isinstance,
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


class DataFilterComponent(BaseComponent):
    name: ClassVar[str] = "DataFilterComponent"
    display_name: ClassVar[str] = "Data Filter"
    category: ClassVar[str] = "Transform"
    description: ClassVar[str] = (
        "Filters arrays of objects or data payloads declaratively based on field comparisons or expressions."
    )
    icon: ClassVar[str] = "filter"

    inputs: ClassVar[list[BaseInput]] = [
        BaseInput(
            name="input_data",
            label="Incoming Collection",
            default=[],
            description="Array of items or dict containing a collection",
        ),
        StrInput(
            name="items_path",
            label="Items Key / Path",
            default="",
            placeholder="e.g. items or results",
            description="Nested path to extract list if input_data is a dict (dot-separated)",
        ),
        StrInput(
            name="field",
            label="Field Name",
            default="status",
            placeholder="e.g. status or price",
            description="Property to evaluate on each item",
        ),
        SelectInput(
            name="operator",
            label="Comparison Operator",
            options=[
                "equals",
                "not_equals",
                "greater_than",
                "less_than",
                "greater_or_equal",
                "less_or_equal",
                "contains",
                "not_contains",
                "is_empty",
                "is_not_empty",
                "expression",
            ],
            default="equals",
        ),
        StrInput(
            name="value",
            label="Comparison Value",
            default="active",
            placeholder="Target comparison value",
        ),
        StrInput(
            name="custom_expression",
            label="Custom Expression",
            default="item.get('status') == 'active'",
            placeholder="e.g. item.get('price', 0) > 50",
            description="Python expression evaluated when operator is 'expression'",
        ),
    ]

    outputs: ClassVar[list[Output]] = [
        Output(name="filtered_items", label="Filtered Items", type="list", method="get_filtered_items"),
        Output(name="discarded_items", label="Discarded Items", type="list", method="get_discarded_items"),
        Output(name="count", label="Count", type="int", method="get_count"),
        Output(name="total_count", label="Total Count", type="int", method="get_total_count"),
    ]

    def __init__(self, inputs: dict[str, Any] | None = None):
        super().__init__(inputs)
        self._filtered_items: list[Any] = []
        self._discarded_items: list[Any] = []
        self._count: int = 0
        self._total_count: int = 0

    async def execute(self, **kwargs: Any) -> dict[str, Any]:
        if kwargs:
            self._raw_inputs.update(kwargs)
        return await self.filter_data()

    async def filter_data(self) -> dict[str, Any]:
        inp = self.get_inputs()
        raw_data = inp.get("input_data", [])
        items_path = str(inp.get("items_path", "")).strip()
        field = str(inp.get("field", "status")).strip()
        operator = str(inp.get("operator", "equals")).strip()
        target_value = inp.get("value", "active")
        custom_expr = str(inp.get("custom_expression", "item.get('status') == 'active'")).strip()

        items: list[Any] = []
        if isinstance(raw_data, list):
            items = raw_data
        elif isinstance(raw_data, dict):
            if items_path:
                curr: Any = raw_data
                for part in items_path.split("."):
                    if isinstance(curr, dict):
                        curr = curr.get(part, [])
                    else:
                        curr = []
                        break
                if isinstance(curr, list):
                    items = curr
                else:
                    items = [curr] if curr is not None else []
            else:
                if "items" in raw_data and isinstance(raw_data["items"], list):
                    items = raw_data["items"]
                elif "results" in raw_data and isinstance(raw_data["results"], list):
                    items = raw_data["results"]
                else:
                    items = [raw_data]
        elif raw_data is not None:
            items = [raw_data]

        def _get_field(item: Any, fld: str) -> Any:
            if isinstance(item, dict):
                if "." in fld:
                    curr = item
                    for part in fld.split("."):
                        if isinstance(curr, dict):
                            curr = curr.get(part)
                        else:
                            return None
                    return curr
                return item.get(fld)
            return getattr(item, fld, None)

        def _coerce(val: Any, target_raw: Any) -> tuple[Any, Any]:
            target_str = str(target_raw).strip()
            try:
                if isinstance(val, (int, float)):
                    return float(val), float(target_str)
            except Exception:
                pass
            if isinstance(val, bool):
                return val, target_str.lower() in ("true", "1", "yes")
            return str(val) if val is not None else "", target_str

        def _evaluate_item(item: Any) -> bool:
            if operator == "expression":
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
                safe_locals = {"item": item}
                try:
                    return bool(eval(custom_expr, safe_globals, safe_locals))
                except Exception:
                    return False

            val = _get_field(item, field)

            if operator == "is_empty":
                return val is None or val == "" or val == [] or val == {}
            if operator == "is_not_empty":
                return not (val is None or val == "" or val == [] or val == {})

            if operator == "contains":
                if isinstance(val, (list, tuple, set)):
                    return str(target_value) in [str(x) for x in val]
                return str(target_value).lower() in str(val).lower() if val is not None else False
            if operator == "not_contains":
                if isinstance(val, (list, tuple, set)):
                    return str(target_value) not in [str(x) for x in val]
                return str(target_value).lower() not in str(val).lower() if val is not None else True

            v1, v2 = _coerce(val, target_value)
            if operator == "equals":
                return v1 == v2
            if operator == "not_equals":
                return v1 != v2
            if operator == "greater_than":
                try:
                    return float(v1) > float(v2)
                except Exception:
                    return str(v1) > str(v2)
            if operator == "less_than":
                try:
                    return float(v1) < float(v2)
                except Exception:
                    return str(v1) < str(v2)
            if operator == "greater_or_equal":
                try:
                    return float(v1) >= float(v2)
                except Exception:
                    return str(v1) >= str(v2)
            if operator == "less_or_equal":
                try:
                    return float(v1) <= float(v2)
                except Exception:
                    return str(v1) <= str(v2)

            return False

        filtered: list[Any] = []
        discarded: list[Any] = []

        for itm in items:
            if _evaluate_item(itm):
                filtered.append(itm)
            else:
                discarded.append(itm)

        self._filtered_items = filtered
        self._discarded_items = discarded
        self._count = len(filtered)
        self._total_count = len(items)

        return {
            "filtered_items": filtered,
            "discarded_items": discarded,
            "count": self._count,
            "total_count": self._total_count,
        }

    async def get_filtered_items(self) -> list[Any]:
        return self._filtered_items

    async def get_discarded_items(self) -> list[Any]:
        return self._discarded_items

    async def get_count(self) -> int:
        return self._count

    async def get_total_count(self) -> int:
        return self._total_count


class SlackWebhookComponent(BaseComponent):
    name: ClassVar[str] = "SlackWebhookComponent"
    display_name: ClassVar[str] = "Slack Notification"
    category: ClassVar[str] = "Actions"
    description: ClassVar[str] = "Sends formatted alert messages and notifications to Slack channels via Incoming Webhooks."
    icon: ClassVar[str] = "message-square"

    inputs: ClassVar[list[BaseInput]] = [
        StrInput(
            name="webhook_url",
            label="Webhook URL",
            placeholder="https://hooks.slack.com/services/...",
            required=True,
        ),
        StrInput(
            name="text",
            label="Message Text",
            placeholder="Alert text (supports mrkdwn & {{VARIABLES}})",
            required=True,
        ),
        StrInput(
            name="channel",
            label="Channel Override",
            placeholder="#general or @user (optional)",
            default="",
        ),
        StrInput(
            name="username",
            label="Bot Username",
            placeholder="Bot display name",
            default="FlowBuild Bot",
        ),
        StrInput(
            name="icon_emoji",
            label="Icon Emoji",
            placeholder=":robot_face:",
            default=":robot_face:",
        ),
        DictInput(
            name="blocks",
            label="Block Kit Blocks (JSON array/dict)",
            default=None,
        ),
        DictInput(
            name="attachments",
            label="Attachments (JSON array/dict)",
            default=None,
        ),
        IntInput(
            name="timeout",
            label="Timeout (seconds)",
            default=15,
        ),
    ]

    outputs: ClassVar[list[Output]] = [
        Output(name="success", label="Success", type="bool", method="get_success"),
        Output(name="status_code", label="Status Code", type="int", method="get_status_code"),
        Output(name="response", label="Response", type="str", method="get_response"),
    ]

    def __init__(self, inputs: dict[str, Any] | None = None):
        super().__init__(inputs)
        self._success: bool = False
        self._status_code: int = 0
        self._response: str = ""

    async def execute(self, **kwargs: Any) -> dict[str, Any]:
        if kwargs:
            self._raw_inputs.update(kwargs)
        return await self.send_notification()

    async def send_notification(self) -> dict[str, Any]:
        inp = self.get_inputs()
        webhook_url = str(inp.get("webhook_url") or "").strip()
        text = str(inp.get("text") or "").strip()
        channel = str(inp.get("channel") or "").strip()
        username = str(inp.get("username") or "FlowBuild Bot").strip()
        icon_emoji = str(inp.get("icon_emoji") or ":robot_face:").strip()
        blocks = inp.get("blocks")
        attachments = inp.get("attachments")
        timeout = int(inp.get("timeout") or 15)

        if not webhook_url:
            self._success = False
            self._status_code = 0
            self._response = "webhook_url is required"
            return {"success": self._success, "status_code": self._status_code, "response": self._response}

        if not text:
            self._success = False
            self._status_code = 0
            self._response = "text is required"
            return {"success": self._success, "status_code": self._status_code, "response": self._response}

        payload: dict[str, Any] = {"text": text}
        if channel:
            payload["channel"] = channel
        if username:
            payload["username"] = username
        if icon_emoji:
            payload["icon_emoji"] = icon_emoji
        if blocks:
            payload["blocks"] = blocks
        if attachments:
            payload["attachments"] = attachments

        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                resp = await client.post(webhook_url, json=payload)
                self._status_code = resp.status_code
                self._response = resp.text
                self._success = resp.status_code == 200 and ("ok" in resp.text.lower())
        except Exception as e:
            self._success = False
            self._status_code = 0
            self._response = str(e)

        return {
            "success": self._success,
            "status_code": self._status_code,
            "response": self._response,
        }

    async def get_success(self) -> bool:
        return self._success

    async def get_status_code(self) -> int:
        return self._status_code

    async def get_response(self) -> str:
        return self._response


class DiscordWebhookComponent(BaseComponent):
    name: ClassVar[str] = "DiscordWebhookComponent"
    display_name: ClassVar[str] = "Discord Notification"
    category: ClassVar[str] = "Actions"
    description: ClassVar[str] = "Sends formatted messages, embeds, and alerts to Discord channels via Webhooks."
    icon: ClassVar[str] = "message-circle"

    inputs: ClassVar[list[BaseInput]] = [
        StrInput(
            name="webhook_url",
            label="Webhook URL",
            placeholder="https://discord.com/api/webhooks/...",
            required=True,
        ),
        StrInput(
            name="content",
            label="Message Content",
            placeholder="Message text (supports markdown & {{VARIABLES}})",
            default="",
        ),
        StrInput(
            name="username",
            label="Bot Username",
            placeholder="FlowBuild Bot",
            default="FlowBuild Bot",
        ),
        StrInput(
            name="avatar_url",
            label="Avatar Image URL",
            placeholder="https://example.com/avatar.png",
            default="",
        ),
        StrInput(
            name="embed_title",
            label="Embed Card Title",
            placeholder="Card title (optional)",
            default="",
        ),
        StrInput(
            name="embed_description",
            label="Embed Card Description",
            placeholder="Detailed embed description",
            default="",
        ),
        StrInput(
            name="embed_color",
            label="Embed Accent Color",
            placeholder="#5865F2 or 5814783",
            default="5814783",
        ),
        DictInput(
            name="embeds",
            label="Custom Embeds (JSON array)",
            default=None,
        ),
        IntInput(
            name="timeout",
            label="Timeout (seconds)",
            default=15,
        ),
    ]

    outputs: ClassVar[list[Output]] = [
        Output(name="success", label="Success", type="bool", method="get_success"),
        Output(name="status_code", label="Status Code", type="int", method="get_status_code"),
        Output(name="response", label="Response", type="str", method="get_response"),
    ]

    def __init__(self, inputs: dict[str, Any] | None = None):
        super().__init__(inputs)
        self._success: bool = False
        self._status_code: int = 0
        self._response: str = ""

    async def execute(self, **kwargs: Any) -> dict[str, Any]:
        if kwargs:
            self._raw_inputs.update(kwargs)
        return await self.send_notification()

    async def send_notification(self) -> dict[str, Any]:
        inp = self.get_inputs()
        webhook_url = str(inp.get("webhook_url") or "").strip()
        content = str(inp.get("content") or "").strip()
        username = str(inp.get("username") or "FlowBuild Bot").strip()
        avatar_url = str(inp.get("avatar_url") or "").strip()
        embed_title = str(inp.get("embed_title") or "").strip()
        embed_description = str(inp.get("embed_description") or "").strip()
        embed_color_raw = str(inp.get("embed_color") or "5814783").strip()
        custom_embeds = inp.get("embeds")
        timeout = int(inp.get("timeout") or 15)

        if not webhook_url:
            self._success = False
            self._status_code = 0
            self._response = "webhook_url is required"
            return {"success": self._success, "status_code": self._status_code, "response": self._response}

        has_embed = bool(embed_title or embed_description or custom_embeds)
        if not content and not has_embed:
            self._success = False
            self._status_code = 0
            self._response = "content or embed is required"
            return {"success": self._success, "status_code": self._status_code, "response": self._response}

        payload: dict[str, Any] = {}
        if content:
            payload["content"] = content
        if username:
            payload["username"] = username
        if avatar_url:
            payload["avatar_url"] = avatar_url

        if custom_embeds:
            if isinstance(custom_embeds, list):
                payload["embeds"] = custom_embeds
            elif isinstance(custom_embeds, dict):
                payload["embeds"] = [custom_embeds]
        elif embed_title or embed_description:
            color_int = 5814783
            try:
                if embed_color_raw.startswith("#"):
                    color_int = int(embed_color_raw.lstrip("#"), 16)
                elif embed_color_raw.startswith("0x"):
                    color_int = int(embed_color_raw, 16)
                else:
                    color_int = int(embed_color_raw)
            except Exception:
                color_int = 5814783

            embed_obj: dict[str, Any] = {"color": color_int}
            if embed_title:
                embed_obj["title"] = embed_title
            if embed_description:
                embed_obj["description"] = embed_description
            payload["embeds"] = [embed_obj]

        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                resp = await client.post(webhook_url, json=payload)
                self._status_code = resp.status_code
                self._response = resp.text if resp.text else "ok"
                self._success = resp.status_code in (200, 204)
        except Exception as e:
            self._success = False
            self._status_code = 0
            self._response = str(e)

        return {
            "success": self._success,
            "status_code": self._status_code,
            "response": self._response,
        }

    async def get_success(self) -> bool:
        return self._success

    async def get_status_code(self) -> int:
        return self._status_code

    async def get_response(self) -> str:
        return self._response


class TelegramWebhookComponent(BaseComponent):
    name: ClassVar[str] = "TelegramWebhookComponent"
    display_name: ClassVar[str] = "Telegram Notification"
    category: ClassVar[str] = "Actions"
    description: ClassVar[str] = (
        "Sends messages, alerts, or formatted notifications to Telegram chats or channels via Telegram Bot API."
    )
    icon: ClassVar[str] = "send"

    inputs: ClassVar[list[BaseInput]] = [
        StrInput(
            name="bot_token",
            label="Bot Token",
            placeholder="123456789:ABCdefGhIJKlmNoPQRsTUVwxyZ...",
            required=True,
        ),
        StrInput(
            name="chat_id",
            label="Chat ID",
            placeholder="@channel_username or -1001234567890",
            required=True,
        ),
        StrInput(
            name="message",
            label="Message Text",
            placeholder="Message text (supports HTML/Markdown & {{VARIABLES}})",
            required=True,
            default="",
        ),
        SelectInput(
            name="parse_mode",
            label="Parse Mode",
            options=["HTML", "MarkdownV2", "Markdown", "None"],
            default="HTML",
        ),
        BoolInput(
            name="disable_web_page_preview",
            label="Disable Link Previews",
            default=False,
        ),
        BoolInput(
            name="disable_notification",
            label="Silent Notification",
            default=False,
        ),
        IntInput(
            name="timeout",
            label="Timeout (seconds)",
            default=15,
        ),
    ]

    outputs: ClassVar[list[Output]] = [
        Output(name="success", label="Success", type="bool", method="get_success"),
        Output(name="status_code", label="Status Code", type="int", method="get_status_code"),
        Output(name="response", label="Response", type="str", method="get_response"),
        Output(name="message_id", label="Message ID", type="int", method="get_message_id"),
    ]

    def __init__(self, inputs: dict[str, Any] | None = None):
        super().__init__(inputs)
        self._success: bool = False
        self._status_code: int = 0
        self._response: str = ""
        self._message_id: int = 0

    async def execute(self, **kwargs: Any) -> dict[str, Any]:
        if kwargs:
            self._raw_inputs.update(kwargs)
        return await self.send_notification()

    async def send_notification(self) -> dict[str, Any]:
        inp = self.get_inputs()
        bot_token = str(inp.get("bot_token") or "").strip()
        chat_id = str(inp.get("chat_id") or "").strip()
        message = str(inp.get("message") or "").strip()
        parse_mode = str(inp.get("parse_mode") or "HTML").strip()
        disable_web_page_preview = bool(inp.get("disable_web_page_preview", False))
        disable_notification = bool(inp.get("disable_notification", False))
        timeout = int(inp.get("timeout") or 15)

        if not bot_token:
            self._success = False
            self._status_code = 0
            self._response = "bot_token is required"
            self._message_id = 0
            return {
                "success": self._success,
                "status_code": self._status_code,
                "response": self._response,
                "message_id": self._message_id,
            }

        if not chat_id:
            self._success = False
            self._status_code = 0
            self._response = "chat_id is required"
            self._message_id = 0
            return {
                "success": self._success,
                "status_code": self._status_code,
                "response": self._response,
                "message_id": self._message_id,
            }

        if not message:
            self._success = False
            self._status_code = 0
            self._response = "message is required"
            self._message_id = 0
            return {
                "success": self._success,
                "status_code": self._status_code,
                "response": self._response,
                "message_id": self._message_id,
            }

        endpoint = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload: dict[str, Any] = {
            "chat_id": chat_id,
            "text": message,
        }

        if parse_mode and parse_mode != "None":
            payload["parse_mode"] = parse_mode
        if disable_web_page_preview:
            payload["disable_web_page_preview"] = True
        if disable_notification:
            payload["disable_notification"] = True

        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                resp = await client.post(endpoint, json=payload)
                self._status_code = resp.status_code
                self._response = resp.text

                msg_id = 0
                is_ok = False
                try:
                    data = resp.json()
                    is_ok = bool(data.get("ok", False))
                    if isinstance(data.get("result"), dict):
                        msg_id = int(data["result"].get("message_id", 0))
                except Exception:
                    is_ok = resp.status_code == 200

                self._success = is_ok and (resp.status_code == 200)
                self._message_id = msg_id
        except Exception as e:
            self._success = False
            self._status_code = 0
            self._response = str(e)
            self._message_id = 0

        return {
            "success": self._success,
            "status_code": self._status_code,
            "response": self._response,
            "message_id": self._message_id,
        }

    async def get_success(self) -> bool:
        return self._success

    async def get_status_code(self) -> int:
        return self._status_code

    async def get_response(self) -> str:
        return self._response

    async def get_message_id(self) -> int:
        return self._message_id


class EmailNotificationComponent(BaseComponent):
    name: ClassVar[str] = "EmailNotificationComponent"
    display_name: ClassVar[str] = "Email Notification"
    category: ClassVar[str] = "Actions"
    description: ClassVar[str] = (
        "Sends transactional emails and alerts via standard SMTP with HTML and plain text support."
    )
    icon: ClassVar[str] = "mail"

    inputs: ClassVar[list[BaseInput]] = [
        StrInput(
            name="smtp_host",
            label="SMTP Host",
            placeholder="smtp.gmail.com or smtp.sendgrid.net",
            required=True,
        ),
        IntInput(
            name="smtp_port",
            label="SMTP Port",
            default=587,
        ),
        StrInput(
            name="smtp_user",
            label="SMTP Username",
            placeholder="apikey or user@example.com",
            default="",
        ),
        StrInput(
            name="smtp_password",
            label="SMTP Password / Key",
            placeholder="password or api_key",
            default="",
        ),
        BoolInput(
            name="use_tls",
            label="Use STARTTLS (Port 587)",
            default=True,
        ),
        BoolInput(
            name="use_ssl",
            label="Use SSL/TLS (Port 465)",
            default=False,
        ),
        StrInput(
            name="from_email",
            label="From Email",
            placeholder="alerts@example.com or System <alerts@example.com>",
            required=True,
        ),
        StrInput(
            name="to_email",
            label="To Email(s)",
            placeholder="recipient@example.com, team@example.com",
            required=True,
        ),
        StrInput(
            name="subject",
            label="Subject",
            placeholder="Notification Subject (supports {{VARIABLES}})",
            required=True,
        ),
        StrInput(
            name="body_html",
            label="HTML Body",
            placeholder="<p>Formatted HTML email message</p>",
            default="",
        ),
        StrInput(
            name="body_text",
            label="Plain Text Body",
            placeholder="Fallback plain text email message",
            default="",
        ),
        IntInput(
            name="timeout",
            label="Timeout (seconds)",
            default=20,
        ),
    ]

    outputs: ClassVar[list[Output]] = [
        Output(name="success", label="Success", type="bool", method="get_success"),
        Output(name="status_code", label="Status Code", type="int", method="get_status_code"),
        Output(name="response", label="Response", type="str", method="get_response"),
        Output(name="recipients_count", label="Recipients Count", type="int", method="get_recipients_count"),
    ]

    def __init__(self, inputs: dict[str, Any] | None = None):
        super().__init__(inputs)
        self._success: bool = False
        self._status_code: int = 0
        self._response: str = ""
        self._recipients_count: int = 0

    async def execute(self, **kwargs: Any) -> dict[str, Any]:
        if kwargs:
            self._raw_inputs.update(kwargs)
        return await self.send_email()

    async def send_email(self) -> dict[str, Any]:
        inp = self.get_inputs()
        smtp_host = str(inp.get("smtp_host") or "").strip()
        smtp_port = int(inp.get("smtp_port") or 587)
        smtp_user = str(inp.get("smtp_user") or "").strip()
        smtp_password = str(inp.get("smtp_password") or "").strip()
        use_tls = bool(inp.get("use_tls", True))
        use_ssl = bool(inp.get("use_ssl", False))
        from_email = str(inp.get("from_email") or "").strip()
        to_email = str(inp.get("to_email") or "").strip()
        subject = str(inp.get("subject") or "").strip()
        body_html = str(inp.get("body_html") or "").strip()
        body_text = str(inp.get("body_text") or "").strip()
        timeout = int(inp.get("timeout") or 20)

        if not smtp_host:
            self._success = False
            self._status_code = 0
            self._response = "smtp_host is required"
            self._recipients_count = 0
            return self._build_result()

        if not from_email:
            self._success = False
            self._status_code = 0
            self._response = "from_email is required"
            self._recipients_count = 0
            return self._build_result()

        if not to_email:
            self._success = False
            self._status_code = 0
            self._response = "to_email is required"
            self._recipients_count = 0
            return self._build_result()

        if not subject:
            self._success = False
            self._status_code = 0
            self._response = "subject is required"
            self._recipients_count = 0
            return self._build_result()

        if not body_html and not body_text:
            self._success = False
            self._status_code = 0
            self._response = "At least one of body_html or body_text is required"
            self._recipients_count = 0
            return self._build_result()

        recipients = [addr.strip() for addr in to_email.split(",") if addr.strip()]
        if not recipients:
            self._success = False
            self._status_code = 0
            self._response = "No valid recipient email addresses found in to_email"
            self._recipients_count = 0
            return self._build_result()

        def _send_sync() -> tuple[bool, int, str]:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = from_email
            msg["To"] = ", ".join(recipients)

            if body_text:
                try:
                    body_text.encode("ascii")
                    msg.attach(MIMEText(body_text, "plain"))
                except UnicodeEncodeError:
                    msg.attach(MIMEText(body_text, "plain", "utf-8"))
            if body_html:
                try:
                    body_html.encode("ascii")
                    msg.attach(MIMEText(body_html, "html"))
                except UnicodeEncodeError:
                    msg.attach(MIMEText(body_html, "html", "utf-8"))

            server = None
            try:
                if use_ssl:
                    server = smtplib.SMTP_SSL(smtp_host, smtp_port, timeout=timeout)
                else:
                    server = smtplib.SMTP(smtp_host, smtp_port, timeout=timeout)
                    if use_tls:
                        server.starttls()

                if smtp_user and smtp_password:
                    server.login(smtp_user, smtp_password)

                server.sendmail(from_email, recipients, msg.as_string())
                return True, 250, f"Email sent successfully to {len(recipients)} recipient(s)"
            finally:
                if server is not None:
                    try:
                        server.quit()
                    except Exception:
                        pass

        try:
            ok, code, message = await asyncio.to_thread(_send_sync)
            self._success = ok
            self._status_code = code
            self._response = message
            self._recipients_count = len(recipients) if ok else 0
        except Exception as e:
            self._success = False
            self._status_code = 0
            self._response = str(e)
            self._recipients_count = 0

        return self._build_result()

    def _build_result(self) -> dict[str, Any]:
        return {
            "success": self._success,
            "status_code": self._status_code,
            "response": self._response,
            "recipients_count": self._recipients_count,
        }

    async def get_success(self) -> bool:
        return self._success

    async def get_status_code(self) -> int:
        return self._status_code

    async def get_response(self) -> str:
        return self._response

    async def get_recipients_count(self) -> int:
        return self._recipients_count


def _resolve_nested_path(data: Any, path: str) -> Any:
    if not path or data is None:
        return None
    curr = data
    for part in path.split("."):
        if isinstance(curr, dict):
            curr = curr.get(part)
        elif isinstance(curr, (list, tuple)) and part.isdigit():
            idx = int(part)
            if 0 <= idx < len(curr):
                curr = curr[idx]
            else:
                return None
        else:
            return None
        if curr is None:
            return None
    return curr


class DataMapperComponent(BaseComponent):
    name: ClassVar[str] = "DataMapperComponent"
    display_name: ClassVar[str] = "Data Mapper"
    category: ClassVar[str] = "Transform"
    description: ClassVar[str] = (
        "Transforms, renames, and restructures objects or collections using declarative field mappings."
    )
    icon: ClassVar[str] = "arrow-right-left"

    inputs: ClassVar[list[BaseInput]] = [
        DictInput(
            name="input_data",
            label="Input Data",
            placeholder="Object or list of objects to map",
            default={},
        ),
        DictInput(
            name="mapping",
            label="Field Mapping Schema",
            placeholder='{"target_key": "source.path.key"}',
            default={},
        ),
        StrInput(
            name="items_path",
            label="Items Array Path",
            placeholder="Optional path to items list (e.g. 'results' or 'data.users')",
            default="",
        ),
        BoolInput(
            name="pass_unmapped",
            label="Pass Unmapped Fields",
            default=False,
        ),
        SelectInput(
            name="mode",
            label="Processing Mode",
            options=["auto", "single", "array"],
            default="auto",
        ),
    ]

    outputs: ClassVar[list[Output]] = [
        Output(name="output_data", label="Mapped Output", type="any", method="get_output_data"),
        Output(name="mapped_count", label="Mapped Count", type="int", method="get_mapped_count"),
    ]

    def __init__(self, inputs: dict[str, Any] | None = None):
        super().__init__(inputs)
        self._output_data: Any = {}
        self._mapped_count: int = 0

    async def execute(self, **kwargs: Any) -> dict[str, Any]:
        if kwargs:
            self._raw_inputs.update(kwargs)
        return await self.map_data()

    async def map_data(self) -> dict[str, Any]:
        inp = self.get_inputs()
        raw_data = inp.get("input_data")
        mapping = inp.get("mapping") or {}
        items_path = str(inp.get("items_path") or "").strip()
        pass_unmapped = bool(inp.get("pass_unmapped", False))
        mode = str(inp.get("mode") or "auto").strip()

        if not isinstance(mapping, dict):
            mapping = {}

        source_data = raw_data
        if items_path:
            source_data = _resolve_nested_path(raw_data, items_path)

        def _map_single_record(record: Any) -> dict[str, Any]:
            if not isinstance(record, dict):
                return {}
            out: dict[str, Any] = {}
            if pass_unmapped:
                out.update(record)
            for dest_key, src_path in mapping.items():
                if isinstance(src_path, str):
                    out[dest_key] = _resolve_nested_path(record, src_path)
                else:
                    out[dest_key] = src_path
            return out

        is_collection = False
        if mode == "array":
            is_collection = True
        elif mode == "single":
            is_collection = False
        else:  # auto
            is_collection = isinstance(source_data, list)

        if is_collection and isinstance(source_data, list):
            mapped_list = [_map_single_record(item) for item in source_data]
            self._output_data = mapped_list
            self._mapped_count = len(mapped_list)
        elif isinstance(source_data, dict):
            mapped_dict = _map_single_record(source_data)
            self._output_data = mapped_dict
            self._mapped_count = 1 if source_data else 0
        else:
            self._output_data = {} if not is_collection else []
            self._mapped_count = 0

        return {
            "output_data": self._output_data,
            "mapped_count": self._mapped_count,
        }

    async def get_output_data(self) -> Any:
        return self._output_data

    async def get_mapped_count(self) -> int:
        return self._mapped_count


class DataAggregatorComponent(BaseComponent):
    name: ClassVar[str] = "DataAggregatorComponent"
    display_name: ClassVar[str] = "Data Aggregator"
    category: ClassVar[str] = "Transform"
    description: ClassVar[str] = (
        "Calculates mathematical and statistical aggregations (sum, avg, min, max, count, concat, group_by) on collections."
    )
    icon: ClassVar[str] = "calculator"

    inputs: ClassVar[list[BaseInput]] = [
        DictInput(
            name="items",
            label="Items Collection",
            placeholder="List of records or object containing items",
            default=[],
        ),
        StrInput(
            name="items_path",
            label="Items Array Path",
            placeholder="Optional path to items list (e.g. 'orders' or 'data.items')",
            default="",
        ),
        StrInput(
            name="field",
            label="Target Field Path",
            placeholder="Field to aggregate (e.g. 'price' or 'user.age')",
            default="",
        ),
        SelectInput(
            name="operation",
            label="Aggregation Operation",
            options=["all", "sum", "avg", "min", "max", "count", "concat"],
            default="all",
        ),
        StrInput(
            name="group_by",
            label="Group By Field",
            placeholder="Optional field to group by (e.g. 'category')",
            default="",
        ),
        StrInput(
            name="delimiter",
            label="Concat Delimiter",
            default=", ",
        ),
    ]

    outputs: ClassVar[list[Output]] = [
        Output(name="result", label="Result", type="any", method="get_result"),
        Output(name="summary", label="Summary", type="dict", method="get_summary"),
        Output(name="count", label="Count", type="int", method="get_count"),
    ]

    def __init__(self, inputs: dict[str, Any] | None = None):
        super().__init__(inputs)
        self._result: Any = 0
        self._summary: dict[str, Any] = {"count": 0, "sum": 0.0, "avg": 0.0, "min": 0.0, "max": 0.0}
        self._count: int = 0

    async def execute(self, **kwargs: Any) -> dict[str, Any]:
        if kwargs:
            self._raw_inputs.update(kwargs)
        return await self.aggregate_data()

    async def aggregate_data(self) -> dict[str, Any]:
        inp = self.get_inputs()
        raw_items = inp.get("items")
        items_path = str(inp.get("items_path") or "").strip()
        field = str(inp.get("field") or "").strip()
        op = str(inp.get("operation") or "all").lower().strip()
        group_by = str(inp.get("group_by") or "").strip()
        delimiter = str(inp.get("delimiter") or ", ")

        collection = raw_items
        if items_path:
            collection = _resolve_nested_path(raw_items, items_path)

        if not isinstance(collection, (list, tuple)):
            if isinstance(collection, dict):
                collection = [collection]
            else:
                collection = []

        def _extract_val(item: Any, target_field: str) -> Any:
            if not target_field:
                return item
            if isinstance(item, dict):
                return _resolve_nested_path(item, target_field)
            return None

        # Group By handling
        if group_by:
            groups: dict[str, list[Any]] = {}
            for item in collection:
                g_key = str(_extract_val(item, group_by) or "Unknown")
                groups.setdefault(g_key, []).append(item)

            grouped_results: dict[str, Any] = {}
            for g_key, g_items in groups.items():
                g_summary = self._compute_metrics(g_items, field, delimiter)
                if op == "sum":
                    grouped_results[g_key] = {"sum": g_summary["sum"], "count": g_summary["count"], "avg": g_summary["avg"]}
                elif op == "avg":
                    grouped_results[g_key] = {"avg": g_summary["avg"], "count": g_summary["count"]}
                elif op == "count":
                    grouped_results[g_key] = g_summary["count"]
                else:
                    grouped_results[g_key] = g_summary

            self._result = grouped_results
            self._summary = self._compute_metrics(collection, field, delimiter)
            self._count = len(collection)
            return {
                "result": self._result,
                "summary": self._summary,
                "count": self._count,
            }

        summary = self._compute_metrics(collection, field, delimiter)
        self._summary = summary

        if op == "sum":
            self._result = summary["sum"]
            self._count = summary["count"]
        elif op == "avg":
            self._result = summary["avg"]
            self._count = summary["count"]
        elif op == "min":
            self._result = summary["min"]
            self._count = summary["count"]
        elif op == "max":
            self._result = summary["max"]
            self._count = summary["count"]
        elif op == "count":
            self._result = summary["count"]
            self._count = summary["count"]
        elif op == "concat":
            self._result = summary.get("concat", "")
            self._count = summary["count"]
        else:  # "all"
            self._result = summary
            self._count = summary["count"]

        return {
            "result": self._result,
            "summary": self._summary,
            "count": self._count,
        }

    def _compute_metrics(self, items: list[Any], field: str, delimiter: str) -> dict[str, Any]:
        numeric_vals: list[float] = []
        string_vals: list[str] = []

        for item in items:
            val = item if not field else (
                _resolve_nested_path(item, field) if isinstance(item, dict) else None
            )
            if val is not None:
                string_vals.append(str(val))
                try:
                    if isinstance(val, (int, float)):
                        numeric_vals.append(float(val))
                    elif isinstance(val, str) and val.strip():
                        numeric_vals.append(float(val.strip()))
                except (ValueError, TypeError):
                    pass

        if numeric_vals:
            count_val = len(numeric_vals)
        elif string_vals:
            count_val = len(string_vals)
        else:
            count_val = len(items)

        total_sum = sum(numeric_vals) if numeric_vals else 0.0
        avg_val = (total_sum / count_val) if numeric_vals and count_val > 0 else 0.0
        min_val = min(numeric_vals) if numeric_vals else 0.0
        max_val = max(numeric_vals) if numeric_vals else 0.0
        concat_val = delimiter.join(string_vals)

        return {
            "count": count_val,
            "sum": total_sum,
            "avg": avg_val,
            "min": min_val,
            "max": max_val,
            "concat": concat_val,
        }

    async def get_result(self) -> Any:
        return self._result

    async def get_summary(self) -> dict[str, Any]:
        return self._summary

    async def get_count(self) -> int:
        return self._count


class CsvParserComponent(BaseComponent):
    name: ClassVar[str] = "CsvParserComponent"
    display_name: ClassVar[str] = "CSV Parser"
    category: ClassVar[str] = "Transform"
    description: ClassVar[str] = (
        "Parses CSV text into JSON collections, or converts JSON collections into formatted CSV strings."
    )
    icon: ClassVar[str] = "file-spreadsheet"

    inputs: ClassVar[list[BaseInput]] = [
        SelectInput(
            name="mode",
            label="Operation Mode",
            options=["parse", "generate"],
            default="parse",
        ),
        StrInput(
            name="csv_data",
            label="CSV Data",
            placeholder="CSV text content",
            default="",
        ),
        DictInput(
            name="json_data",
            label="JSON Data",
            placeholder="Array of objects to convert to CSV",
            default=[],
        ),
        StrInput(
            name="delimiter",
            label="Delimiter",
            default=",",
        ),
        BoolInput(
            name="has_headers",
            label="Has Header Row",
            default=True,
        ),
        BoolInput(
            name="skip_empty_lines",
            label="Skip Empty Lines",
            default=True,
        ),
        StrInput(
            name="custom_headers",
            label="Custom Headers (Generate Mode)",
            placeholder="Comma-separated header names",
            default="",
        ),
    ]

    outputs: ClassVar[list[Output]] = [
        Output(name="data", label="Output Data", type="any", method="get_data"),
        Output(name="row_count", label="Row Count", type="int", method="get_row_count"),
        Output(name="headers", label="Headers", type="list", method="get_headers"),
    ]

    def __init__(self, inputs: dict[str, Any] | None = None):
        super().__init__(inputs)
        self._data: Any = []
        self._row_count: int = 0
        self._headers: list[str] = []

    async def execute(self, **kwargs: Any) -> dict[str, Any]:
        if kwargs:
            self._raw_inputs.update(kwargs)
        return await self.process_csv()

    async def process_csv(self) -> dict[str, Any]:
        inp = self.get_inputs()
        mode = str(inp.get("mode") or "parse").lower().strip()
        delimiter = str(inp.get("delimiter") or ",")
        if not delimiter:
            delimiter = ","
        has_headers = bool(inp.get("has_headers", True))
        skip_empty_lines = bool(inp.get("skip_empty_lines", True))
        custom_headers_raw = str(inp.get("custom_headers") or "").strip()

        if mode == "generate":
            json_data = inp.get("json_data")
            if not isinstance(json_data, list):
                if isinstance(json_data, dict):
                    json_data = [json_data]
                else:
                    json_data = []

            if not json_data:
                self._data = ""
                self._row_count = 0
                self._headers = []
                return self._build_result()

            fieldnames: list[str] = []
            if custom_headers_raw:
                fieldnames = [h.strip() for h in custom_headers_raw.split(",") if h.strip()]
            else:
                seen = set()
                for row in json_data:
                    if isinstance(row, dict):
                        for k in row.keys():
                            if k not in seen:
                                seen.add(k)
                                fieldnames.append(k)

            output_io = io.StringIO()
            writer = csv.DictWriter(output_io, fieldnames=fieldnames, delimiter=delimiter, extrasaction="ignore", lineterminator="\r\n")
            writer.writeheader()
            for row in json_data:
                if isinstance(row, dict):
                    writer.writerow(row)

            self._data = output_io.getvalue()
            self._row_count = len(json_data)
            self._headers = fieldnames
            return self._build_result()

        # Parse mode
        raw_csv = inp.get("csv_data")
        if isinstance(raw_csv, dict):
            for candidate in ["csv_text", "csv", "data", "text", "content"]:
                if candidate in raw_csv and isinstance(raw_csv[candidate], str):
                    raw_csv = raw_csv[candidate]
                    break
            else:
                raw_csv = ""

        csv_text = str(raw_csv or "").strip()
        if not csv_text:
            self._data = []
            self._row_count = 0
            self._headers = []
            return self._build_result()

        input_io = io.StringIO(csv_text)
        if has_headers:
            reader = csv.DictReader(input_io, delimiter=delimiter)
            rows: list[dict[str, Any]] = []
            for r in reader:
                if skip_empty_lines and not any(r.values()):
                    continue
                rows.append(dict(r))
            self._data = rows
            self._row_count = len(rows)
            self._headers = list(reader.fieldnames or [])
        else:
            reader_list = csv.reader(input_io, delimiter=delimiter)
            rows_list: list[list[str]] = []
            for r in reader_list:
                if skip_empty_lines and not any(r):
                    continue
                rows_list.append(r)
            self._data = rows_list
            self._row_count = len(rows_list)
            self._headers = [f"col_{i}" for i in range(len(rows_list[0]))] if rows_list else []

        return self._build_result()

    def _build_result(self) -> dict[str, Any]:
        return {
            "data": self._data,
            "row_count": self._row_count,
            "headers": self._headers,
        }

    async def get_data(self) -> Any:
        return self._data

    async def get_row_count(self) -> int:
        return self._row_count

    async def get_headers(self) -> list[str]:
        return self._headers


class DatabaseQueryComponent(BaseComponent):
    name: ClassVar[str] = "DatabaseQueryComponent"
    display_name: ClassVar[str] = "Database Query"
    category: ClassVar[str] = "Storage"
    description: ClassVar[str] = (
        "Executes parameterized SQL queries against SQLite, PostgreSQL, or external databases using SQLAlchemy."
    )
    icon: ClassVar[str] = "database"

    inputs: ClassVar[list[BaseInput]] = [
        StrInput(
            name="connection_string",
            label="Database Connection URL",
            placeholder="e.g. sqlite:///data.db or postgresql://... (leave empty for FlowBuild DB)",
            default="",
        ),
        CodeInput(
            name="query",
            label="SQL Query",
            language="sql",
            placeholder="SELECT * FROM table WHERE id = :id",
            default="SELECT 1 as result",
            required=True,
        ),
        DictInput(
            name="params",
            label="Query Parameters",
            placeholder="JSON object with :named parameter bindings",
            default={},
        ),
        SelectInput(
            name="fetch_mode",
            label="Fetch Mode",
            options=["all", "one", "none"],
            default="all",
        ),
        BoolInput(
            name="auto_commit",
            label="Auto Commit",
            default=True,
        ),
    ]

    outputs: ClassVar[list[Output]] = [
        Output(name="data", label="Output Data", type="any", method="get_data"),
        Output(name="row_count", label="Row Count", type="int", method="get_row_count"),
        Output(name="columns", label="Columns", type="list", method="get_columns"),
    ]

    def __init__(self, inputs: dict[str, Any] | None = None):
        super().__init__(inputs)
        self._data: Any = []
        self._row_count: int = 0
        self._columns: list[str] = []

    async def execute(self, **kwargs: Any) -> dict[str, Any]:
        if kwargs:
            self._raw_inputs.update(kwargs)
        return await self.execute_query()

    async def execute_query(self) -> dict[str, Any]:
        inp = self.get_inputs()
        conn_str = str(inp.get("connection_string") or "").strip()
        query = str(inp.get("query") or "").strip()
        raw_params = inp.get("params") or {}
        fetch_mode = str(inp.get("fetch_mode") or "all").lower().strip()
        auto_commit = bool(inp.get("auto_commit", True))

        if isinstance(raw_params, dict):
            if "query_params" in raw_params and isinstance(raw_params["query_params"], dict):
                params = raw_params["query_params"]
            elif "params" in raw_params and isinstance(raw_params["params"], dict):
                params = raw_params["params"]
            else:
                params = raw_params
        else:
            params = {}

        if not query:
            self._data = []
            self._row_count = 0
            self._columns = []
            return self._build_result()

        def _sync_worker() -> tuple[Any, int, list[str]]:
            from backend.app.db import db_manager

            engine_to_use = None
            dispose_needed = False
            if conn_str:
                engine_kwargs: dict[str, Any] = {}
                if conn_str.startswith("sqlite"):
                    engine_kwargs["connect_args"] = {"check_same_thread": False}
                engine_to_use = create_engine(conn_str, **engine_kwargs)
                dispose_needed = True
            else:
                engine_to_use = db_manager.engine

            try:
                with engine_to_use.connect() as conn:
                    stmt = text(query)
                    result = conn.execute(stmt, params)
                    if result.returns_rows and fetch_mode in ("all", "one"):
                        cols = list(result.keys())
                        if fetch_mode == "all":
                            rows = [dict(r._mapping) for r in result.all()]
                            cnt = len(rows)
                            out_data = rows
                        else:
                            r = result.first()
                            out_data = dict(r._mapping) if r is not None else None
                            cnt = 1 if r is not None else 0
                        if auto_commit:
                            conn.commit()
                        return out_data, cnt, cols
                    else:
                        cnt = result.rowcount if result.rowcount is not None and result.rowcount >= 0 else 0
                        if auto_commit:
                            conn.commit()
                        return [], cnt, []
            finally:
                if dispose_needed and engine_to_use is not None:
                    engine_to_use.dispose()

        data, count, cols = await asyncio.to_thread(_sync_worker)
        self._data = data
        self._row_count = count
        self._columns = cols
        return self._build_result()

    def _build_result(self) -> dict[str, Any]:
        return {
            "data": self._data,
            "row_count": self._row_count,
            "columns": self._columns,
        }

    async def get_data(self) -> Any:
        return self._data

    async def get_row_count(self) -> int:
        return self._row_count

    async def get_columns(self) -> list[str]:
        return self._columns


class KeyValueStoreComponent(BaseComponent):
    name: ClassVar[str] = "KeyValueStoreComponent"
    display_name: ClassVar[str] = "Key-Value Store"
    category: ClassVar[str] = "Storage"
    description: ClassVar[str] = (
        "Persists and manages cross-execution state, flags, and atomic counters across workflow runs."
    )
    icon: ClassVar[str] = "hard-drive"

    inputs: ClassVar[list[BaseInput]] = [
        SelectInput(
            name="operation",
            label="Operation",
            options=["get", "set", "delete", "increment", "list"],
            default="get",
        ),
        StrInput(
            name="key",
            label="Key",
            placeholder="e.g. rate_limit_counter or user_session",
            default="my_key",
            required=True,
        ),
        DictInput(
            name="value",
            label="Value",
            placeholder="Value to store (string, number, or JSON object)",
            default="",
        ),
        StrInput(
            name="namespace",
            label="Namespace",
            placeholder="Logical group (e.g. default, cache, auth)",
            default="default",
        ),
        StrInput(
            name="default_value",
            label="Default Fallback Value",
            placeholder="Value returned when key does not exist",
            default="",
        ),
        IntInput(
            name="amount",
            label="Increment Amount",
            default=1,
        ),
    ]

    outputs: ClassVar[list[Output]] = [
        Output(name="result", label="Result", type="any", method="get_result"),
        Output(name="found", label="Found", type="bool", method="get_found"),
        Output(name="key", label="Key", type="str", method="get_key"),
        Output(name="previous_value", label="Previous Value", type="any", method="get_previous_value"),
    ]

    def __init__(self, inputs: dict[str, Any] | None = None):
        super().__init__(inputs)
        self._result: Any = None
        self._found: bool = False
        self._key: str = ""
        self._previous_value: Any = None

    async def execute(self, **kwargs: Any) -> dict[str, Any]:
        if kwargs:
            self._raw_inputs.update(kwargs)
        return await self.execute_kv()

    async def execute_kv(self) -> dict[str, Any]:
        from backend.app.db import db_manager

        inp = self.get_inputs()
        operation = str(inp.get("operation") or "get").lower().strip()
        key = str(inp.get("key") or "my_key").strip()
        val = inp.get("value")
        namespace = str(inp.get("namespace") or "default").strip()
        if not namespace:
            namespace = "default"
        default_val = inp.get("default_value", "")
        amount = inp.get("amount", 1)
        try:
            amount_num = int(amount)
        except Exception:
            try:
                amount_num = float(amount)
            except Exception:
                amount_num = 1

        self._key = key

        def _sync_worker() -> tuple[Any, bool, Any]:
            if operation == "set":
                res, prev = db_manager.kv_set(key, val, namespace=namespace)
                found = prev is not None
                return res, found, prev
            elif operation == "delete":
                deleted = db_manager.kv_delete(key, namespace=namespace)
                return deleted, deleted, None
            elif operation == "increment":
                res, prev = db_manager.kv_increment(key, amount=amount_num, namespace=namespace)
                return res, True, prev
            elif operation == "list":
                keys = db_manager.kv_list(prefix=key if key != "my_key" else "", namespace=namespace)
                return keys, len(keys) > 0, None
            else: # "get"
                res, found = db_manager.kv_get(key, namespace=namespace, default=default_val)
                return res, found, None

        res, found, prev = await asyncio.to_thread(_sync_worker)
        self._result = res
        self._found = found
        self._previous_value = prev
        return self._build_result()

    def _build_result(self) -> dict[str, Any]:
        return {
            "result": self._result,
            "found": self._found,
            "key": self._key,
            "previous_value": self._previous_value,
        }

    async def get_result(self) -> Any:
        return self._result

    async def get_found(self) -> bool:
        return self._found

    async def get_key(self) -> str:
        return self._key

    async def get_previous_value(self) -> Any:
        return self._previous_value










