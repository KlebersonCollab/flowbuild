# Plan: Discord Notification Component (ADR 0022)

## 1. Problem Statement & Motivation
Discord is one of the most widely used platforms for developer communities, open-source projects, and engineering team alerts. FlowBuild workflows currently support Slack via `SlackWebhookComponent`, but sending notifications to Discord required manual configuration using generic HTTP nodes and manual conversion of Discord's specific payload structures (such as `content` instead of `text`, decimal color embeds, and handling HTTP 204 No Content).

A native `DiscordWebhookComponent` delivers seamless, dedicated Discord messaging on the visual canvas.

## 2. Scope & Boundaries
- **In Scope**:
  - Implement `DiscordWebhookComponent` in `backend/src/backend/app/components/builtins/actions.py` and register it in `backend/src/backend/app/components/builtins/__init__.py`.
  - Configurable inputs: `webhook_url`, `content`, `username`, `avatar_url`, `embed_title`, `embed_description`, `embed_color`, `embeds`, and `timeout`.
  - Hex color to decimal integer parsing.
  - Acceptance of HTTP 200 and HTTP 204 as successful delivery states.
  - Network error and timeout catching without workflow aborts.
  - Integration into `CustomNode.vue` and `ComponentPalette.vue` with `MessageCircle` icon and Blurple/Indigo styling.
  - Full backend and frontend test suites.
- **Out of Scope**:
  - Discord OAuth Bot Gateway WebSocket connections (Incoming Webhook URL protocol is standard for notifications).

## 3. High-Level Approach
- Utilize `httpx.AsyncClient` inside `DiscordWebhookComponent.send_notification()`.
- Validate required fields and construct standard Discord JSON payload (`content`, `username`, `avatar_url`, `embeds`).
- Map `discord` in Vue components to `MessageCircle` with Blurple styling.

## 4. Dependencies & Prerequisites
- `httpx` and `lucide-vue-next` (already present).
- Zero external package additions.

## 5. Architectural Decision Records (ADRs)
- Relates to [ADR 0022: Discord Notification & Webhook Messaging Component](../../project/ADRs/0022-discord-notification-component.md).
