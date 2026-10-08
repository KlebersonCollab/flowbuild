import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import httpx

from backend.app.components.builtins.actions import DiscordWebhookComponent
from backend.app.components.builtins.triggers import ManualTriggerComponent
from backend.app.models.flow import FlowModel, NodeModel, EdgeModel
from backend.app.engine.runner import FlowRunner


@pytest.mark.asyncio
async def test_discord_webhook_component_204_success():
    comp = DiscordWebhookComponent(
        inputs={
            "webhook_url": "https://discord.com/api/webhooks/123/abc",
            "content": "Hello from FlowBuild to Discord!",
        }
    )

    mock_resp = MagicMock()
    mock_resp.status_code = 204
    mock_resp.text = ""

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_resp

        result = await comp.execute()

        assert result["success"] is True
        assert result["status_code"] == 204
        assert result["response"] == "ok"

        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert call_args[0][0] == "https://discord.com/api/webhooks/123/abc"
        payload = call_args[1]["json"]
        assert payload["content"] == "Hello from FlowBuild to Discord!"
        assert payload["username"] == "FlowBuild Bot"


@pytest.mark.asyncio
async def test_discord_webhook_component_rich_embed_and_hex_color():
    comp = DiscordWebhookComponent(
        inputs={
            "webhook_url": "https://discord.com/api/webhooks/123/abc",
            "content": "System Alert",
            "username": "AlertBot",
            "avatar_url": "https://example.com/bot.png",
            "embed_title": "Production Outage",
            "embed_description": "API Gateway returned 502",
            "embed_color": "#FF0000",
        }
    )

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.text = '{"id": "msg_1"}'

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_resp

        result = await comp.execute()

        assert result["success"] is True
        assert result["status_code"] == 200

        payload = mock_post.call_args[1]["json"]
        assert payload["content"] == "System Alert"
        assert payload["username"] == "AlertBot"
        assert payload["avatar_url"] == "https://example.com/bot.png"
        assert len(payload["embeds"]) == 1
        embed = payload["embeds"][0]
        assert embed["title"] == "Production Outage"
        assert embed["description"] == "API Gateway returned 502"
        assert embed["color"] == 16711680  # 0xFF0000 converted to decimal


@pytest.mark.asyncio
async def test_discord_webhook_component_custom_embeds_list():
    comp = DiscordWebhookComponent(
        inputs={
            "webhook_url": "https://discord.com/api/webhooks/123/abc",
            "embeds": [{"title": "Custom Embed", "color": 5814783}],
        }
    )

    mock_resp = MagicMock()
    mock_resp.status_code = 204
    mock_resp.text = ""

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_resp

        result = await comp.execute()

        assert result["success"] is True
        payload = mock_post.call_args[1]["json"]
        assert len(payload["embeds"]) == 1
        assert payload["embeds"][0]["title"] == "Custom Embed"


@pytest.mark.asyncio
async def test_discord_webhook_component_missing_required_fields():
    # Missing webhook_url
    comp1 = DiscordWebhookComponent(inputs={"webhook_url": "", "content": "Valid content"})
    res1 = await comp1.execute()
    assert res1["success"] is False
    assert res1["status_code"] == 0
    assert "webhook_url" in res1["response"]

    # Missing content AND embeds
    comp2 = DiscordWebhookComponent(inputs={"webhook_url": "https://discord.com/api/webhooks/123/abc"})
    res2 = await comp2.execute()
    assert res2["success"] is False
    assert res2["status_code"] == 0
    assert "content or embed" in res2["response"]


@pytest.mark.asyncio
async def test_discord_webhook_component_http_error():
    comp = DiscordWebhookComponent(
        inputs={
            "webhook_url": "https://discord.com/api/webhooks/123/abc",
            "content": "Test error",
        }
    )

    mock_resp = MagicMock()
    mock_resp.status_code = 400
    mock_resp.text = '{"message": "Invalid Webhook Token", "code": 50027}'

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_resp

        result = await comp.execute()

        assert result["success"] is False
        assert result["status_code"] == 400
        assert "Invalid Webhook Token" in result["response"]


@pytest.mark.asyncio
async def test_discord_webhook_component_network_exception():
    comp = DiscordWebhookComponent(
        inputs={
            "webhook_url": "https://discord.com/api/webhooks/123/abc",
            "content": "Network timeout message",
        }
    )

    with patch("httpx.AsyncClient.post", side_effect=httpx.ConnectTimeout("Connection timed out")):
        result = await comp.execute()

        assert result["success"] is False
        assert result["status_code"] == 0
        assert "Connection timed out" in result["response"]


@pytest.mark.asyncio
async def test_discord_webhook_in_flow_runner():
    flow = FlowModel(
        id="flow_discord_1",
        name="Discord Alert Flow",
        nodes=[
            NodeModel(
                id="trigger_1",
                type="ManualTriggerComponent",
                data={"inputs": {}},
            ),
            NodeModel(
                id="discord_1",
                type="DiscordWebhookComponent",
                data={
                    "inputs": {
                        "webhook_url": "https://discord.com/api/webhooks/123/abc",
                        "content": "Pipeline {{PIPELINE_NAME}} finished with code {{STATUS_CODE}}",
                        "username": "DiscordNotifier",
                    }
                },
            ),
        ],
        edges=[
            EdgeModel(id="e1", source="trigger_1", target="discord_1"),
        ],
    )

    mock_resp = MagicMock()
    mock_resp.status_code = 204
    mock_resp.text = ""

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_resp

        runner = FlowRunner(flow, variables={"PIPELINE_NAME": "DeployPRD", "STATUS_CODE": "0"})
        summary = await runner.execute_flow()

        assert summary["status"] == "completed"
        assert "discord_1" in summary["results"]
        discord_result = summary["results"]["discord_1"]
        assert discord_result["success"] is True
        assert discord_result["status_code"] == 204

        # Verify template interpolation worked
        payload = mock_post.call_args[1]["json"]
        assert payload["content"] == "Pipeline DeployPRD finished with code 0"
