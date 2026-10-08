import pytest
from unittest.mock import AsyncMock, patch, MagicMock
import httpx

from backend.app.components.builtins.actions import SlackWebhookComponent
from backend.app.components.builtins.triggers import ManualTriggerComponent
from backend.app.engine.runner import FlowRunner


@pytest.mark.asyncio
async def test_slack_webhook_component_success():
    comp = SlackWebhookComponent(
        inputs={
            "webhook_url": "https://hooks.slack.com/services/T00/B00/X00",
            "text": "Hello from FlowBuild!",
        }
    )

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.text = "ok"

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_resp

        result = await comp.execute()

        assert result["success"] is True
        assert result["status_code"] == 200
        assert result["response"] == "ok"

        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert call_args[0][0] == "https://hooks.slack.com/services/T00/B00/X00"
        payload = call_args[1]["json"]
        assert payload["text"] == "Hello from FlowBuild!"
        assert payload["username"] == "FlowBuild Bot"
        assert payload["icon_emoji"] == ":robot_face:"


@pytest.mark.asyncio
async def test_slack_webhook_component_custom_identity_and_blocks():
    comp = SlackWebhookComponent(
        inputs={
            "webhook_url": "https://hooks.slack.com/services/T00/B00/X00",
            "text": "Deployment notice",
            "channel": "#deploys",
            "username": "DeployBot",
            "icon_emoji": ":rocket:",
            "blocks": [{"type": "section", "text": {"type": "mrkdwn", "text": "*Prod deployed!*"}}],
            "attachments": [{"color": "#36a64f", "text": "All tests green"}],
        }
    )

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.text = "ok"

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_resp

        result = await comp.execute()

        assert result["success"] is True
        assert result["status_code"] == 200

        payload = mock_post.call_args[1]["json"]
        assert payload["channel"] == "#deploys"
        assert payload["username"] == "DeployBot"
        assert payload["icon_emoji"] == ":rocket:"
        assert len(payload["blocks"]) == 1
        assert len(payload["attachments"]) == 1


@pytest.mark.asyncio
async def test_slack_webhook_component_missing_required_fields():
    # Missing webhook_url
    comp1 = SlackWebhookComponent(inputs={"webhook_url": "", "text": "Valid text"})
    res1 = await comp1.execute()
    assert res1["success"] is False
    assert res1["status_code"] == 0
    assert "webhook_url" in res1["response"]

    # Missing text
    comp2 = SlackWebhookComponent(inputs={"webhook_url": "https://hooks.slack.com/services/...", "text": ""})
    res2 = await comp2.execute()
    assert res2["success"] is False
    assert res2["status_code"] == 0
    assert "text" in res2["response"]


@pytest.mark.asyncio
async def test_slack_webhook_component_http_error():
    comp = SlackWebhookComponent(
        inputs={
            "webhook_url": "https://hooks.slack.com/services/T00/B00/X00",
            "text": "Failing message",
        }
    )

    mock_resp = MagicMock()
    mock_resp.status_code = 400
    mock_resp.text = "invalid_payload"

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_resp

        result = await comp.execute()

        assert result["success"] is False
        assert result["status_code"] == 400
        assert result["response"] == "invalid_payload"


@pytest.mark.asyncio
async def test_slack_webhook_component_network_exception():
    comp = SlackWebhookComponent(
        inputs={
            "webhook_url": "https://hooks.slack.com/services/T00/B00/X00",
            "text": "Network error message",
        }
    )

    with patch("httpx.AsyncClient.post", side_effect=httpx.ConnectError("Connection refused")):
        result = await comp.execute()

        assert result["success"] is False
        assert result["status_code"] == 0
        assert "Connection refused" in result["response"]


from backend.app.models.flow import FlowModel, NodeModel, EdgeModel


@pytest.mark.asyncio
async def test_slack_webhook_in_flow_runner():
    flow = FlowModel(
        id="flow_slack_1",
        name="Slack Flow",
        nodes=[
            NodeModel(
                id="trigger_1",
                type="ManualTriggerComponent",
                data={"inputs": {}},
            ),
            NodeModel(
                id="slack_1",
                type="SlackWebhookComponent",
                data={
                    "inputs": {
                        "webhook_url": "https://hooks.slack.com/services/T00/B00/X00",
                        "text": "Flow completed for job {{JOB_NAME}}",
                        "username": "FlowBot",
                    }
                },
            ),
        ],
        edges=[
            EdgeModel(id="e1", source="trigger_1", target="slack_1"),
        ],
    )

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.text = "ok"

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_resp

        runner = FlowRunner(flow, variables={"JOB_NAME": "NightlyBackup"})
        summary = await runner.execute_flow()

        assert summary["status"] == "completed"
        assert "slack_1" in summary["results"]
        slack_result = summary["results"]["slack_1"]
        assert slack_result["success"] is True

        # Verify template interpolation worked
        payload = mock_post.call_args[1]["json"]
        assert payload["text"] == "Flow completed for job NightlyBackup"
