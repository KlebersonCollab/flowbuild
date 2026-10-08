# Plan: Telegram Notification Component (ADR 0023)

## 1. Problem Statement & Motivation
Telegram is one of the most prominent messaging platforms used worldwide for DevOps monitoring, trade alerts, incident response, and personal notifications. Currently, FlowBuild supports Slack and Discord via specialized action components, but sending Telegram messages requires tedious manual setup using `HttpRequestComponent`, manual JSON construction, and manual URL formatting.

A first-class `TelegramWebhookComponent` provides a developer-friendly, zero-boilerplate experience for sending alerts to Telegram direct messages, supergroups, and channels.

## 2. Scope & Boundaries
- **In Scope**:
  - Implement `TelegramWebhookComponent` in `backend/src/backend/app/components/builtins/actions.py` and register it in `backend/src/backend/app/components/builtins/__init__.py`.
  - Configurable inputs: `bot_token`, `chat_id`, `message`, `parse_mode`, `disable_web_page_preview`, `disable_notification`, and `timeout`.
  - Dedicated outputs: `success`, `status_code`, `response`, and `message_id`.
  - Async delivery via `httpx.AsyncClient` posting to `https://api.telegram.org/bot<bot_token>/sendMessage`.
  - Robust exception handling (timeouts, network errors, invalid tokens, chat not found).
  - Integration with `CustomNode.vue` and `ComponentPalette.vue` with `Send` icon and Sky blue styling.
  - Backend integration tests and frontend unit tests.
- **Out of Scope**:
  - Telegram long-polling / Webhook bot receiver (which is a Trigger node for a future roadmap item; this component is an outbound Action node).

## 3. High-Level Approach
- Follow TDD cycle: test first, then implementation.
- Wire into `backend.app.components.builtins` and verify with Pytest.
- Add frontend tests for registry serialization and node rendering, then update UI components with `Send` icon and Sky theme.
- Audit with SDD integrity and spec drift sensors.

## 4. Dependencies & Prerequisites
- `httpx` (already installed).
- `lucide-vue-next` (already includes `Send` icon).

## 5. Architectural Decision Records (ADRs)
- Relates to [ADR 0023: Telegram Notification & Webhook Messaging Component](../../project/ADRs/0023-telegram-notification-component.md).
