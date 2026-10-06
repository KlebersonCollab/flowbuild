import pytest
from backend.app.components.builtins.actions import HttpRequestComponent
from backend.app.components.builtins.logic import IfConditionComponent
from backend.app.components.builtins.triggers import CronTriggerComponent

@pytest.mark.asyncio
async def test_http_request_bearer_auth(monkeypatch):
    captured_request = {}

    class MockResponse:
        status_code = 200
        headers = {"content-type": "application/json"}
        def json(self):
            return {"authenticated": True}
        @property
        def text(self):
            return '{"authenticated": true}'

    class MockAsyncClient:
        def __init__(self, *args, **kwargs):
            pass
        async def __aenter__(self):
            return self
        async def __aexit__(self, exc_type, exc_val, exc_tb):
            pass
        async def request(self, method, url, **kwargs):
            captured_request["method"] = method
            captured_request["url"] = url
            captured_request["headers"] = kwargs.get("headers", {})
            return MockResponse()

    import httpx
    monkeypatch.setattr(httpx, "AsyncClient", MockAsyncClient)

    comp = HttpRequestComponent()
    res = await comp.execute(
        url="https://api.example.com/data",
        method="GET",
        auth_type="bearer",
        auth_token="test_bearer_token"
    )

    assert res["status_code"] == 200
    assert captured_request["headers"]["Authorization"] == "Bearer test_bearer_token"

@pytest.mark.asyncio
async def test_http_request_api_key_header(monkeypatch):
    captured_request = {}

    class MockResponse:
        status_code = 200
        headers = {}
        def json(self):
            return {"ok": True}
        @property
        def text(self):
            return "{}"

    class MockAsyncClient:
        def __init__(self, *args, **kwargs):
            pass
        async def __aenter__(self):
            return self
        async def __aexit__(self, exc_type, exc_val, exc_tb):
            pass
        async def request(self, method, url, **kwargs):
            captured_request["headers"] = kwargs.get("headers", {})
            return MockResponse()

    import httpx
    monkeypatch.setattr(httpx, "AsyncClient", MockAsyncClient)

    comp = HttpRequestComponent()
    await comp.execute(
        url="https://api.example.com/data",
        method="GET",
        auth_type="api_key_header",
        auth_token="api_key_secret_99",
        auth_header_name="X-Custom-Key"
    )

    assert captured_request["headers"]["X-Custom-Key"] == "api_key_secret_99"

@pytest.mark.asyncio
async def test_if_condition_logic():
    comp = IfConditionComponent()

    # Truthy condition
    true_res = await comp.execute(
        input_data={"amount": 150},
        expression="data.get('amount', 0) > 100"
    )
    assert true_res["result"] is True
    assert true_res["branch"] == "true"
    assert true_res["true_branch"] == {"amount": 150}
    assert true_res["false_branch"] is None

    # Falsy condition
    false_res = await comp.execute(
        input_data={"amount": 50},
        expression="data.get('amount', 0) > 100"
    )
    assert false_res["result"] is False
    assert false_res["branch"] == "false"
    assert false_res["true_branch"] is None
    assert false_res["false_branch"] == {"amount": 50}

@pytest.mark.asyncio
async def test_cron_trigger_calculation():
    comp = CronTriggerComponent()
    res = await comp.execute(
        cron_expression="*/15 * * * *",
        timezone_str="UTC"
    )
    assert res["cron"] == "*/15 * * * *"
    assert "next_run" in res
    assert "timestamp" in res
