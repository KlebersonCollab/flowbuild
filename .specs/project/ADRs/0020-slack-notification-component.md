# ADR 0020: Slack Notification & Webhook Messaging Component

## Status
Accepted

## Date
2026-10-07

## Context
In automation and monitoring workflows, developers and operations teams require immediate alerts and notifications delivered to team communication channels (such as Slack) upon error detection, cron job completions, webhook triggers, or threshold breaches.

Previously in FlowBuild, users had to use `HttpRequestComponent`, manually setting headers, HTTP POST method, and constructing the Slack webhook JSON structure (`{"text": "..."}`). This created friction, required boilerplate setup, lacked Slack-specific fields (channel overrides, bot usernames, emoji avatars, Block Kit blocks, attachments), and didn't clearly communicate notification intent on the visual canvas.

## Decision
1. **Component Design (`SlackWebhookComponent`)**:
   - Class name: `SlackWebhookComponent`
   - Display name: `"Slack Notification"`
   - Category: `"Actions"`
   - Description: `"Sends formatted alert messages and notifications to Slack channels via Incoming Webhooks."`
   - Icon: `"message-square"`
2. **Inputs**:
   - `webhook_url` (`StrInput`, required=True): Slack Incoming Webhook URL (e.g., `https://hooks.slack.com/services/...`).
   - `text` (`StrInput`, required=True): Notification message body. Supports Slack mrkdwn formatting and `{{VARIABLE}}` template interpolation.
   - `channel` (`StrInput`, default=""): Optional destination channel override (e.g. `"#alerts"` or `"@dev"`).
   - `username` (`StrInput`, default="FlowBuild Bot"): Bot display name.
   - `icon_emoji` (`StrInput`, default=":robot_face:"): Emoji avatar icon (e.g. `:warning:`, `:white_check_mark:`).
   - `blocks` (`DictInput` / `BaseInput`, default=None): Optional Slack Block Kit JSON blocks.
   - `attachments` (`DictInput` / `BaseInput`, default=None): Optional Slack attachments JSON array.
   - `timeout` (`IntInput`, default=15): HTTP client timeout in seconds.
3. **Outputs**:
   - `success` (`Output`, type="bool"): True if Slack accepted the webhook (HTTP 200 and body `"ok"`).
   - `status_code` (`Output`, type="int"): HTTP response status code.
   - `response` (`Output`, type="str"): Raw response text from the Slack API endpoint.
4. **Resilience & Execution Semantics**:
   - Validates that `webhook_url` and `text` are provided.
   - Employs asynchronous HTTP client (`httpx.AsyncClient`) with timeout safeguard.
   - Traps HTTP exceptions and network timeouts gracefully without unhandled crashes, emitting `success: False` and recording diagnostic error text.
5. **Frontend Canvas & Palette Integration**:
   - In `ComponentPalette.vue` and `CustomNode.vue`, map `slack` or `notification` name to `MessageSquare` icon and Rose styling (`text-rose-400 bg-rose-500/10 border-rose-500/20`), giving notifications high-contrast visual distinction.

## Consequences
- **Positive**: First-class notification experience for workflows with minimal configuration.
- **Flexibility**: Supports both simple text messages and advanced Block Kit / attachment payloads.
- **Safety**: Non-blocking async network operations with full exception isolation.
- **Backwards Compatibility**: 100% backward compatible; introduces an additive action component.
