# ADR 0022: Discord Notification & Webhook Messaging Component

## Status
Accepted

## Date
2026-10-07

## Context
Workflows frequently need to notify developer communities, engineering guilds, gaming teams, or operations channels on Discord when builds complete, server alerts occur, daily summary crons finish, or incoming webhooks arrive.

While `HttpRequestComponent` and `SlackWebhookComponent` exist, Discord's Incoming Webhook API has specific payload conventions:
1. Message body parameter is named `content` (instead of Slack's `text`).
2. Supports rich Embed cards (`embeds` with `title`, `description`, `color` in decimal integer, `fields`, `footer`, etc.).
3. Default successful response from Discord Incoming Webhooks is HTTP 204 No Content (empty body).
4. Custom bot appearance parameters (`username`, `avatar_url`).

Providing a first-class `DiscordWebhookComponent` eliminates the need for manual payload construction, handles Discord's 204 No Content response semantics, and brings dedicated canvas visual identity.

## Decision
1. **Component Design (`DiscordWebhookComponent`)**:
   - Class name: `DiscordWebhookComponent`
   - Display name: `"Discord Notification"`
   - Category: `"Actions"`
   - Description: `"Sends formatted messages, embeds, and alerts to Discord channels via Webhooks."`
   - Icon: `"message-circle"`
2. **Inputs**:
   - `webhook_url` (`StrInput`, required=True): Discord Webhook URL (`https://discord.com/api/webhooks/...`).
   - `content` (`StrInput`): Message text body (supports markdown and `{{VARIABLES}}`).
   - `username` (`StrInput`, default="FlowBuild Bot"): Webhook bot display name override.
   - `avatar_url` (`StrInput`, default=""): Webhook bot avatar image URL override.
   - `embed_title` (`StrInput`, default=""): Rich embed card title.
   - `embed_description` (`StrInput`, default=""): Rich embed card description.
   - `embed_color` (`StrInput`, default="5814783"): Embed card accent color (Hex string like `"#5865F2"` or decimal int like `5814783`).
   - `embeds` (`DictInput` / `BaseInput`, default=None): Advanced custom embeds array or dictionary.
   - `timeout` (`IntInput`, default=15): HTTP client timeout in seconds.
3. **Outputs**:
   - `success` (`Output`, type="bool"): True if Discord returned HTTP 200 OK or 204 No Content.
   - `status_code` (`Output`, type="int"): HTTP status code.
   - `response` (`Output`, type="str"): Raw response text or `"ok"` for HTTP 204.
4. **Execution Semantics & Resilience**:
   - Validates that `webhook_url` and at least one message payload field (`content`, `embed_title`, `embed_description`, or `embeds`) are provided.
   - Automatically converts hex color codes (`#5865F2`, `0x5865F2`) to Discord's required decimal integer format.
   - Uses `httpx.AsyncClient` with configurable timeout.
   - Treats both HTTP 200 and HTTP 204 as successful delivery.
   - Catches connection and DNS exceptions gracefully without unhandled crashes, emitting `success: False` with descriptive diagnostics.
5. **Frontend Canvas & Palette Integration**:
   - In `ComponentPalette.vue` and `CustomNode.vue`, map `discord` to `MessageCircle` icon and Discord Blurple/Indigo styling (`text-[#828fff] bg-[#5e6ad2]/10 border-[#5e6ad2]/30`).

## Consequences
- **Positive**: Native integration with Discord webhooks alongside Slack.
- **Completeness**: Developers and communities can broadcast events to both primary communication platforms (Slack and Discord).
- **Safety**: Fully async, non-blocking, and isolated error handling.
- **Backwards Compatibility**: 100% additive; no breaking changes.
