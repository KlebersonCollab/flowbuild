# ADR 0023: Telegram Notification & Webhook Messaging Component

## Status
Accepted

## Date
2026-10-07

## Context
FlowBuild automation workflows frequently need to send real-time alerts and notifications to Telegram channels, groups, and direct chats. Telegram is widely used for DevOps alerts, monitoring notifications, trading signals, and customer communication due to its reliable Bot API and rich formatting options.

While `HttpRequestComponent` exists, interacting with Telegram's Bot API (`https://api.telegram.org/bot<bot_token>/sendMessage`) involves specific conventions:
1. Authentication via bot token embedded directly in the API URL path (`/bot<bot_token>/sendMessage`).
2. Recipient addressing via `chat_id` (numeric chat ID or public channel username `@channel`).
3. Message formatting via `parse_mode` (`"HTML"`, `"MarkdownV2"`, `"Markdown"` or plain text).
4. Notification control flags such as `disable_web_page_preview` and `disable_notification` (silent alert).
5. Response payload containing an `ok` boolean flag and a `result` object holding the dispatched `message_id`.

A dedicated `TelegramWebhookComponent` (display name: "Telegram Notification") simplifies configuration, eliminates boilerplate URL and payload construction, supports variable interpolation (`{{VAR}}`), and gives Telegram nodes a first-class visual identity with dedicated iconography and branding.

## Decision
1. **Component Design (`TelegramWebhookComponent`)**:
   - Class name: `TelegramWebhookComponent`
   - Display name: `"Telegram Notification"`
   - Category: `"Actions"`
   - Description: `"Sends messages or alerts to Telegram chats or channels via Telegram Bot API."`
   - Icon: `"send"`
2. **Inputs**:
   - `bot_token` (`StrInput`, required=True): Telegram Bot Token provided by @BotFather.
   - `chat_id` (`StrInput`, required=True): Target Telegram Chat ID (numeric or `@channel_name`).
   - `message` (`StrInput`, required=True): Message text content (supports formatting & `{{VARIABLES}}`).
   - `parse_mode` (`SelectInput`, options=`["HTML", "MarkdownV2", "Markdown", "None"]`, default=`"HTML"`): Formatting syntax for message text.
   - `disable_web_page_preview` (`BoolInput`, default=False): If true, disables link preview generation.
   - `disable_notification` (`BoolInput`, default=False): If true, sends the message silently without sound.
   - `timeout` (`IntInput`, default=15): HTTP client timeout in seconds.
3. **Outputs**:
   - `success` (`Output`, type="bool"): True if Telegram returned HTTP 200 and `"ok": true`.
   - `status_code` (`Output`, type="int"): HTTP status code.
   - `response` (`Output`, type="str"): Raw response text from the Telegram Bot API.
   - `message_id` (`Output`, type="int"): ID of the sent message if successful, or 0.
4. **Execution Semantics & Resilience**:
   - Validates that `bot_token`, `chat_id`, and `message` are non-empty before dispatching.
   - Constructs POST request to `https://api.telegram.org/bot{bot_token}/sendMessage`.
   - Uses `httpx.AsyncClient` with configurable timeout.
   - Gracefully catches network errors, DNS failures, or invalid JSON, returning `success: False` with descriptive error text without aborting the workflow runner.
5. **Frontend Canvas & Palette Integration**:
   - In `ComponentPalette.vue` and `CustomNode.vue`, map `telegram` to `Send` icon and Telegram Sky/Cyan styling (`text-sky-400 bg-sky-500/10 border-sky-500/30`).

## Consequences
- **Positive**: Native, reliable Telegram alerts without custom HTTP node configuration.
- **Completeness**: Expands FlowBuild's messaging suite alongside Slack and Discord.
- **Safety**: Fully async, non-blocking, and isolated error handling.
- **Backwards Compatibility**: 100% additive; no breaking changes.
