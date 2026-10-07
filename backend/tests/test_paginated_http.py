import pytest
import httpx

from backend.app.components.builtins.actions import PaginatedHttpComponent
from backend.app.components.builtins.triggers import ManualTriggerComponent
from backend.app.components.builtins.actions import JsonTransformComponent
from backend.app.engine.runner import FlowRunner
from backend.app.models.flow import FlowModel, NodeModel, EdgeModel, NodePosition


class MockResponse:
    def __init__(self, status_code: int = 200, json_data: dict | list | None = None):
        self.status_code = status_code
        self._json_data = json_data or {}

    def raise_for_status(self):
        if self.status_code >= 400:
            raise httpx.HTTPStatusError("HTTP Error", request=None, response=None)

    def json(self):
        return self._json_data

    @property
    def text(self):
        import json
        return json.dumps(self._json_data)


@pytest.mark.asyncio
async def test_paginated_http_page_number(monkeypatch):
    """Tests page_number pagination stopping on empty items."""
    calls = []

    class MockAsyncClient:
        def __init__(self, *args, **kwargs):
            pass
        async def __aenter__(self):
            return self
        async def __aexit__(self, exc_type, exc_val, exc_tb):
            pass
        async def request(self, method, url, **kwargs):
            params = kwargs.get("params", {})
            page = params.get("page", 1)
            calls.append(page)
            if page == 1:
                return MockResponse(200, {"items": [{"id": 1}, {"id": 2}]})
            elif page == 2:
                return MockResponse(200, {"items": [{"id": 3}]})
            else:
                return MockResponse(200, {"items": []})

    monkeypatch.setattr(httpx, "AsyncClient", MockAsyncClient)

    comp = PaginatedHttpComponent(
        inputs={
            "url": "https://api.mock.test/users",
            "pagination_mode": "page_number",
            "page_param": "page",
            "page_size": 2,
            "start_page": 1,
            "items_path": "items",
            "max_pages": 10,
        }
    )

    out = await comp.execute()

    assert out["total_items"] == 3
    assert out["pages_fetched"] == 3
    assert len(out["all_items"]) == 3
    assert out["all_items"] == [{"id": 1}, {"id": 2}, {"id": 3}]
    assert out["summary"]["stop_reason"] == "empty_items"
    assert calls == [1, 2, 3]


@pytest.mark.asyncio
async def test_paginated_http_break_condition(monkeypatch):
    """Tests early break when custom Python break_condition evaluates to True."""
    class MockAsyncClient:
        def __init__(self, *args, **kwargs):
            pass
        async def __aenter__(self):
            return self
        async def __aexit__(self, exc_type, exc_val, exc_tb):
            pass
        async def request(self, method, url, **kwargs):
            return MockResponse(200, {"results": [{"val": 1}, {"val": 2}]})

    monkeypatch.setattr(httpx, "AsyncClient", MockAsyncClient)

    comp = PaginatedHttpComponent(
        inputs={
            "url": "https://api.mock.test/items",
            "pagination_mode": "page_number",
            "start_page": 1,
            "items_path": "results",
            "break_condition": "total_items >= 4",
            "max_pages": 10,
        }
    )

    out = await comp.execute()

    assert out["total_items"] == 4
    assert out["pages_fetched"] == 2
    assert out["summary"]["stop_reason"] == "break_condition_met"


@pytest.mark.asyncio
async def test_paginated_http_offset_limit(monkeypatch):
    """Tests offset_limit pagination mode."""
    calls = []

    class MockAsyncClient:
        def __init__(self, *args, **kwargs):
            pass
        async def __aenter__(self):
            return self
        async def __aexit__(self, exc_type, exc_val, exc_tb):
            pass
        async def request(self, method, url, **kwargs):
            params = kwargs.get("params", {})
            offset = params.get("offset", 0)
            calls.append(offset)
            if offset == 0:
                return MockResponse(200, {"data": ["a", "b", "c"]})
            elif offset == 3:
                return MockResponse(200, {"data": ["d"]})
            else:
                return MockResponse(200, {"data": []})

    monkeypatch.setattr(httpx, "AsyncClient", MockAsyncClient)

    comp = PaginatedHttpComponent(
        inputs={
            "url": "https://api.mock.test/records",
            "pagination_mode": "offset_limit",
            "page_param": "offset",
            "limit_param": "limit",
            "page_size": 3,
            "start_page": 0,
            "items_path": "data",
            "max_pages": 5,
        }
    )

    out = await comp.execute()

    assert out["total_items"] == 4
    assert out["pages_fetched"] == 2
    assert out["all_items"] == ["a", "b", "c", "d"]
    assert calls == [0, 3]


@pytest.mark.asyncio
async def test_paginated_http_cursor_mode(monkeypatch):
    """Tests cursor-based pagination stopping when next cursor is null/absent."""
    class MockAsyncClient:
        def __init__(self, *args, **kwargs):
            pass
        async def __aenter__(self):
            return self
        async def __aexit__(self, exc_type, exc_val, exc_tb):
            pass
        async def request(self, method, url, **kwargs):
            params = kwargs.get("params", {})
            cursor = params.get("cursor")
            if cursor == "cur_2":
                return MockResponse(200, {"items": [{"id": 3}], "next_cursor": None})
            else:
                return MockResponse(200, {"items": [{"id": 1}, {"id": 2}], "next_cursor": "cur_2"})

    monkeypatch.setattr(httpx, "AsyncClient", MockAsyncClient)

    comp = PaginatedHttpComponent(
        inputs={
            "url": "https://api.mock.test/feed",
            "pagination_mode": "cursor",
            "page_param": "cursor",
            "cursor_path": "next_cursor",
            "items_path": "items",
            "max_pages": 10,
        }
    )

    out = await comp.execute()

    assert out["total_items"] == 3
    assert out["pages_fetched"] == 2
    assert out["all_items"] == [{"id": 1}, {"id": 2}, {"id": 3}]
    assert out["summary"]["stop_reason"] == "no_next_cursor"


@pytest.mark.asyncio
async def test_paginated_http_max_pages_safety(monkeypatch):
    """Tests that execution stops when max_pages ceiling is reached."""
    class MockAsyncClient:
        def __init__(self, *args, **kwargs):
            pass
        async def __aenter__(self):
            return self
        async def __aexit__(self, exc_type, exc_val, exc_tb):
            pass
        async def request(self, method, url, **kwargs):
            return MockResponse(200, {"items": [{"msg": "ok"}]})

    monkeypatch.setattr(httpx, "AsyncClient", MockAsyncClient)

    comp = PaginatedHttpComponent(
        inputs={
            "url": "https://api.mock.test/infinite",
            "pagination_mode": "page_number",
            "max_pages": 3,
            "items_path": "items",
        }
    )

    out = await comp.execute()

    assert out["pages_fetched"] == 3
    assert out["total_items"] == 3
    assert out["summary"]["stop_reason"] == "max_pages_reached"


@pytest.mark.asyncio
async def test_flow_runner_with_paginated_http(monkeypatch):
    """Tests end-to-end FlowRunner execution of a flow containing PaginatedHttpComponent."""
    class MockAsyncClient:
        def __init__(self, *args, **kwargs):
            pass
        async def __aenter__(self):
            return self
        async def __aexit__(self, exc_type, exc_val, exc_tb):
            pass
        async def request(self, method, url, **kwargs):
            params = kwargs.get("params", {})
            page = params.get("page", 1)
            if page == 1:
                return MockResponse(200, {"items": [{"title": "Book 1"}, {"title": "Book 2"}]})
            return MockResponse(200, {"items": []})

    monkeypatch.setattr(httpx, "AsyncClient", MockAsyncClient)

    flow = FlowModel(
        id="paginated-flow-1",
        name="Paginated API Flow",
        nodes=[
            NodeModel(
                id="n1",
                type="ManualTriggerComponent",
                position=NodePosition(x=0, y=0),
                data={"inputs": {"initial_payload": {"category": "books"}}},
            ),
            NodeModel(
                id="n2",
                type="PaginatedHttpComponent",
                position=NodePosition(x=200, y=0),
                data={
                    "inputs": {
                        "url": "https://api.mock.test/catalog",
                        "pagination_mode": "page_number",
                        "page_param": "page",
                        "items_path": "items",
                        "max_pages": 5,
                    }
                },
            ),
            NodeModel(
                id="n3",
                type="JsonTransformComponent",
                position=NodePosition(x=400, y=0),
                data={
                    "inputs": {
                        "expression": "dict(total=len(payload), items=payload)",
                    }
                },
            ),
        ],
        edges=[
            EdgeModel(id="e1", source="n1", sourceHandle="data", target="n2", targetHandle="params"),
            EdgeModel(id="e2", source="n2", sourceHandle="all_items", target="n3", targetHandle="input_data"),
        ],
    )

    runner = FlowRunner(flow)
    events = []
    async for evt in runner.execute_stream():
        events.append(evt)

    assert runner.context.status == "completed"
    assert "n2" in runner.context.results
    assert "n3" in runner.context.results

    n3_out = runner.context.results["n3"]
    assert n3_out["total"] == 2
    assert len(n3_out["items"]) == 2


@pytest.mark.asyncio
async def test_paginated_http_sanitizes_non_string_headers(monkeypatch):
    """Verifies that non-string header values (e.g. ints, bools) are safely converted to str."""
    received_headers = {}

    class MockAsyncClient:
        def __init__(self, *args, **kwargs):
            pass
        async def __aenter__(self):
            return self
        async def __aexit__(self, exc_type, exc_val, exc_tb):
            pass
        async def request(self, method, url, **kwargs):
            nonlocal received_headers
            received_headers = kwargs.get("headers", {})
            return MockResponse(200, {"items": []})

    monkeypatch.setattr(httpx, "AsyncClient", MockAsyncClient)

    comp = PaginatedHttpComponent(
        inputs={
            "url": "https://api.mock.test/items",
            "headers": {"X-Page-Limit": 10, "X-Enabled": True, "X-Secret": "secret-val"},
            "max_pages": 1,
            "items_path": "items",
        }
    )

    out = await comp.execute()
    assert out["summary"]["stop_reason"] == "empty_items"
    assert received_headers["X-Page-Limit"] == "10"
    assert received_headers["X-Enabled"] == "True"
    assert received_headers["X-Secret"] == "secret-val"
    assert received_headers["User-Agent"] == "FlowBuild/1.0"
    assert all(isinstance(v, str) for v in received_headers.values())
