import pytest
from unittest.mock import MagicMock, patch
import smtplib

from backend.app.components.builtins.actions import EmailNotificationComponent
from backend.app.components.builtins.triggers import ManualTriggerComponent
from backend.app.models.flow import FlowModel, NodeModel, EdgeModel
from backend.app.engine.runner import FlowRunner


@pytest.mark.asyncio
async def test_email_notification_starttls_success():
    comp = EmailNotificationComponent(
        inputs={
            "smtp_host": "smtp.example.com",
            "smtp_port": 587,
            "smtp_user": "test_user",
            "smtp_password": "test_password",
            "use_tls": True,
            "use_ssl": False,
            "from_email": "alerts@flowbuild.dev",
            "to_email": "admin@flowbuild.dev",
            "subject": "System Status: Healthy",
            "body_html": "<h1>All systems operational</h1>",
            "body_text": "All systems operational",
        }
    )

    mock_server = MagicMock()

    with patch("smtplib.SMTP", return_value=mock_server) as mock_smtp:
        result = await comp.execute()

        assert result["success"] is True
        assert result["status_code"] == 250
        assert result["recipients_count"] == 1
        assert "successfully" in result["response"]

        mock_smtp.assert_called_once_with("smtp.example.com", 587, timeout=20)
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once_with("test_user", "test_password")
        mock_server.sendmail.assert_called_once()
        sendmail_args = mock_server.sendmail.call_args[0]
        assert sendmail_args[0] == "alerts@flowbuild.dev"
        assert sendmail_args[1] == ["admin@flowbuild.dev"]
        assert "Subject: System Status: Healthy" in sendmail_args[2]
        mock_server.quit.assert_called_once()


@pytest.mark.asyncio
async def test_email_notification_ssl_multi_recipients():
    comp = EmailNotificationComponent(
        inputs={
            "smtp_host": "smtp.sendgrid.net",
            "smtp_port": 465,
            "use_ssl": True,
            "from_email": "noreply@example.com",
            "to_email": "dev1@example.com, dev2@example.com, dev3@example.com",
            "subject": "Multi-recipient Notification",
            "body_text": "Greetings to the engineering team.",
        }
    )

    mock_server = MagicMock()

    with patch("smtplib.SMTP_SSL", return_value=mock_server) as mock_ssl:
        result = await comp.execute()

        assert result["success"] is True
        assert result["status_code"] == 250
        assert result["recipients_count"] == 3

        mock_ssl.assert_called_once_with("smtp.sendgrid.net", 465, timeout=20)
        sendmail_args = mock_server.sendmail.call_args[0]
        assert sendmail_args[1] == ["dev1@example.com", "dev2@example.com", "dev3@example.com"]
        mock_server.quit.assert_called_once()


@pytest.mark.asyncio
async def test_email_notification_missing_required_fields():
    # Missing smtp_host
    comp1 = EmailNotificationComponent(inputs={"smtp_host": "", "from_email": "a@b.com", "to_email": "c@d.com", "subject": "Hi", "body_text": "Hi"})
    res1 = await comp1.execute()
    assert res1["success"] is False
    assert res1["status_code"] == 0
    assert "smtp_host" in res1["response"]

    # Missing from_email
    comp2 = EmailNotificationComponent(inputs={"smtp_host": "smtp.ex.com", "from_email": "", "to_email": "c@d.com", "subject": "Hi", "body_text": "Hi"})
    res2 = await comp2.execute()
    assert res2["success"] is False
    assert "from_email" in res2["response"]

    # Missing to_email
    comp3 = EmailNotificationComponent(inputs={"smtp_host": "smtp.ex.com", "from_email": "a@b.com", "to_email": "", "subject": "Hi", "body_text": "Hi"})
    res3 = await comp3.execute()
    assert res3["success"] is False
    assert "to_email" in res3["response"]

    # Missing subject
    comp4 = EmailNotificationComponent(inputs={"smtp_host": "smtp.ex.com", "from_email": "a@b.com", "to_email": "c@d.com", "subject": "", "body_text": "Hi"})
    res4 = await comp4.execute()
    assert res4["success"] is False
    assert "subject" in res4["response"]

    # Missing body_html AND body_text
    comp5 = EmailNotificationComponent(inputs={"smtp_host": "smtp.ex.com", "from_email": "a@b.com", "to_email": "c@d.com", "subject": "Hi", "body_text": "", "body_html": ""})
    res5 = await comp5.execute()
    assert res5["success"] is False
    assert "body" in res5["response"]


@pytest.mark.asyncio
async def test_email_notification_auth_failure():
    comp = EmailNotificationComponent(
        inputs={
            "smtp_host": "smtp.example.com",
            "smtp_user": "wrong_user",
            "smtp_password": "bad_password",
            "from_email": "a@b.com",
            "to_email": "c@d.com",
            "subject": "Notice",
            "body_text": "Content",
        }
    )

    mock_server = MagicMock()
    mock_server.login.side_effect = smtplib.SMTPAuthenticationError(535, b"Authentication credentials invalid")

    with patch("smtplib.SMTP", return_value=mock_server):
        result = await comp.execute()

        assert result["success"] is False
        assert result["status_code"] == 0
        assert result["recipients_count"] == 0
        assert "Authentication credentials invalid" in result["response"]


@pytest.mark.asyncio
async def test_email_notification_connect_error():
    comp = EmailNotificationComponent(
        inputs={
            "smtp_host": "unreachable.smtp.host",
            "from_email": "a@b.com",
            "to_email": "c@d.com",
            "subject": "Notice",
            "body_text": "Content",
        }
    )

    with patch("smtplib.SMTP", side_effect=smtplib.SMTPConnectError(421, b"Connection refused")):
        result = await comp.execute()

        assert result["success"] is False
        assert result["status_code"] == 0
        assert result["recipients_count"] == 0
        assert "Connection refused" in result["response"]


@pytest.mark.asyncio
async def test_email_notification_in_flow_runner():
    flow = FlowModel(
        id="flow_email_1",
        name="Email Alert Flow",
        nodes=[
            NodeModel(
                id="trigger_1",
                type="ManualTriggerComponent",
                data={"inputs": {}},
            ),
            NodeModel(
                id="email_1",
                type="EmailNotificationComponent",
                data={
                    "inputs": {
                        "smtp_host": "smtp.internal.corp",
                        "from_email": "bot@{{COMPANY_DOMAIN}}",
                        "to_email": "oncall@{{COMPANY_DOMAIN}}",
                        "subject": "Alert: [{{SEVERITY}}] on cluster {{CLUSTER_NAME}}",
                        "body_html": "<p>Cluster {{CLUSTER_NAME}} reported {{INCIDENT}}.</p>",
                    }
                },
            ),
        ],
        edges=[
            EdgeModel(id="e1", source="trigger_1", target="email_1"),
        ],
    )

    mock_server = MagicMock()

    with patch("smtplib.SMTP", return_value=mock_server):
        runner = FlowRunner(
            flow,
            variables={
                "COMPANY_DOMAIN": "example.com",
                "SEVERITY": "CRITICAL",
                "CLUSTER_NAME": "k8s-prod-us",
                "INCIDENT": "Pod OOMKilled",
            },
        )
        summary = await runner.execute_flow()

        assert summary["status"] == "completed"
        assert "email_1" in summary["results"]
        email_result = summary["results"]["email_1"]
        assert email_result["success"] is True

        sendmail_args = mock_server.sendmail.call_args[0]
        assert sendmail_args[0] == "bot@example.com"
        assert sendmail_args[1] == ["oncall@example.com"]
        raw_msg = sendmail_args[2]
        assert "Subject: Alert: [CRITICAL] on cluster k8s-prod-us" in raw_msg
        assert "Cluster k8s-prod-us reported Pod OOMKilled." in raw_msg
