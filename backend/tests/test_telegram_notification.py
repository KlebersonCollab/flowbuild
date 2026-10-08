import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import httpx

from backend.app.components.builtins.actions import TelegramWebhookComponent
from backend.app.components.builtins.triggers import ManualTriggerComponent
from backend.app.models.flow import FlowModel, NodeModel, EdgeModel
from backend.app.engine.runner import FlowRunner


@pytest.mark.asyncio
async def test_telegram_webhook_success():
    comp = TelegramWebhookComponent(
        inputs={
            "bot_token": "123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11",
            "chat_id": "-1001234567890",
            "message": "<b>Hello from FlowBuild to Telegram!</b>",
            "parse_mode": "HTML",
        }
    )

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.text = '{"ok": true, "result": {"message_id": 98765, "text": "<b>Hello from FlowBuild to Telegram!</b>"}}'
    mock_resp.json.return_value = {
        "ok": True,
        "result": {"message_id": 98765, "text": "<b>Hello from FlowBuild to Telegram!</b>"},
    }

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_resp

        result = await comp.execute()

        assert result["success"] is True
        assert result["status_code"] == 200
        assert result["message_id"] == 98765
        assert "98765" in result["response"]

        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert call_args[0][0] == "https://api.telegram.org/bot123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11/sendMessage"
        payload = call_args[1]["json"]
        assert payload["chat_id"] == "-1001234567890"
        assert payload["text"] == "<b>Hello from FlowBuild to Telegram!</b>"
        assert payload["parse_mode"] == "HTML"


@pytest.mark.asyncio
async def test_telegram_webhook_silent_and_no_preview():
    comp = TelegramWebhookComponent(
        inputs={
            "bot_token": "123456:ABC-DEF",
            "chat_id": "@my_channel",
            "message": "Silent message without preview",
            "parse_mode": "MarkdownV2",
            "disable_web_page_preview": True,
            "disable_notification": True,
        }
    )

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.text = '{"ok": true, "result": {"message_id": 555}}'
    mock_resp.json.return_value = {"ok": True, "result": {"message_id": 555}}

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_resp

        result = await comp.execute()

        assert result["success"] is True
        assert result["message_id"] == 555

        payload = mock_post.call_args[1]["json"]
        assert payload["chat_id"] == "@my_channel"
        assert payload["text"] == "Silent message without preview"
        assert payload["parse_mode"] == "MarkdownV2"
        assert payload["disable_web_page_preview"] is True
        assert payload["disable_notification"] is True


@pytest.mark.asyncio
async def test_telegram_webhook_parse_mode_none():
    comp = TelegramWebhookComponent(
        inputs={
            "bot_token": "123456:ABC-DEF",
            "chat_id": "12345678",
            "message": "Plain message",
            "parse_mode": "None",
        }
    )

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.text = '{"ok": true, "result": {"message_id": 111}}'
    mock_resp.json.return_value = {"ok": True, "result": {"message_id": 111}}

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_resp

        result = await comp.execute()

        assert result["success"] is True
        payload = mock_post.call_args[1]["json"]
        assert "parse_mode" not in payload


@pytest.mark.asyncio
async def test_telegram_webhook_missing_required_fields():
    # Missing bot_token
    comp1 = TelegramWebhookComponent(inputs={"bot_token": "", "chat_id": "123", "message": "msg"})
    res1 = await comp1.execute()
    assert res1["success"] is False
    assert res1["status_code"] == 0
    assert res1["message_id"] == 0
    assert "bot_token" in res1["response"]

    # Missing chat_id
    comp2 = TelegramWebhookComponent(inputs={"bot_token": "token", "chat_id": "", "message": "msg"})
    res2 = await comp2.execute()
    assert res2["success"] is False
    assert res2["status_code"] == 0
    assert res2["message_id"] == 0
    assert "chat_id" in res2["response"]

    # Missing message
    comp3 = TelegramWebhookComponent(inputs={"bot_token": "token", "chat_id": "123", "message": ""})
    res3 = await comp3.execute()
    assert res3["success"] is False
    assert res3["status_code"] == 0
    assert res3["message_id"] == 0
    assert "message" in res3["response"]


@pytest.mark.asyncio
async def test_telegram_webhook_api_error():
    comp = TelegramWebhookComponent(
        inputs={
            "bot_token": "123456:ABC-DEF",
            "chat_id": "invalid_chat",
            "message": "Test message",
        }
    )

    mock_resp = MagicMock()
    mock_resp.status_code = 400
    mock_resp.text = '{"ok": false, "error_code": 400, "description": "Bad Request: chat not found"}'
    mock_resp.json.return_value = {
        "ok": False,
        "error_code": 400,
        "description": "Bad Request: chat not found",
    }

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_resp

        result = await comp.execute()

        assert result["success"] is False
        assert result["status_code"] == 400
        assert result["message_id"] == 0
        assert "chat not found" in result["response"]


@pytest.mark.asyncio
async def test_telegram_webhook_network_exception():
    comp = TelegramWebhookComponent(
        inputs={
            "bot_token": "123456:ABC-DEF",
            "chat_id": "12345678",
            "message": "Test timeout",
        }
    )

    with patch("httpx.AsyncClient.post", side_effect=httpx.ConnectTimeout("Telegram connection timed out")):
        result = await comp.execute()

        assert result["success"] is False
        assert result["status_code"] == 0
        assert result["message_id"] == 0
        assert "Telegram connection timed out" in result["response"]


@pytest.mark.asyncio
async def test_telegram_webhook_in_flow_runner():
    flow = FlowModel(
        id="flow_telegram_1",
        name="Telegram Alert Flow",
        nodes=[
            NodeModel(
                id="trigger_1",
                type="ManualTriggerComponent",
                data={"inputs": {}},
            ),
            NodeModel(
                id="telegram_1",
                type="TelegramWebhookComponent",
                data={
                    "inputs": {
                        "bot_token": "bot_{{BOT_KEY}}",
                        "chat_id": "{{TARGET_CHAT}}",
                        "message": "Deployment {{DEPLOY_ID}} status: {{STATUS}}",
                        "parse_mode": "HTML",
                    }
                },
            ),
        ],
        edges=[
            EdgeModel(id="e1", source="trigger_1", target="telegram_1"),
        ],
    )

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.text = '{"ok": true, "result": {"message_id": 4321}}'
    mock_resp.json.return_value = {"ok": True, "result": {"message_id": 4321}}

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_resp

        runner = FlowRunner(
            flow,
            variables={
                "BOT_KEY": "secret_token_123",
                "TARGET_CHAT": "-100998877",
                "DEPLOY_ID": "d-8899",
                "STATUS": "SUCCESS",
            },
        )
        summary = await runner.execute_flow()

        assert summary["status"] == "completed"
        assert "telegram_1" in summary["results"]
        tg_result = summary["results"]["telegram_1"]
        assert tg_result["success"] is True
        assert tg_result["message_id"] == 4321

        # Verify template interpolation worked on URL and body
        call_args = mock_post.call_args
        assert call_args[0][0] == "https://api.telegram.org/botbot_secret_token_123/sendMessage"
        payload = call_args[1]["json"]
        assert payload["chat_id"] == "-100998877"
        assert payload["text"] == "Deployment d-8899 status: SUCCESS"
