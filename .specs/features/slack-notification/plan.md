# Plan: Slack Notification Component (ADR 0020)

## 1. Problem Statement & Motivation
Workflows need to alert engineers, operations, or business teams when tasks complete, anomalies occur, or webhooks/crons run. While generic HTTP requests are possible, setting up a Slack webhook using `HttpRequestComponent` requires repetitive JSON configuration, does not validate Slack payloads, lacks clear canvas identity, and is difficult for non-developers to configure.

A specialized `SlackWebhookComponent` delivers a first-class notification interface tailored to Slack's Incoming Webhooks protocol.

## 2. Scope & Boundaries
- **In Scope**:
  - Implementation of `SlackWebhookComponent` in `backend/src/backend/app/components/builtins/actions.py` and registration in `backend/src/backend/app/components/builtins/__init__.py`.
  - Configurable inputs for `webhook_url`, `text`, `channel`, `username`, `icon_emoji`, `blocks`, `attachments`, and `timeout`.
  - Verified outputs for `success` (`bool`), `status_code` (`int`), and `response` (`str`).
  - Network failure / timeout resilience (returns `success: False` without unhandled exception crashes).
  - Frontend visual representation in `CustomNode.vue` and `ComponentPalette.vue` with `MessageSquare` icon and Rose theme.
  - Comprehensive unit and integration test suites for both backend (`pytest`) and frontend (`vitest`).
- **Out of Scope**:
  - Full Slack Bot OAuth token exchange (Incoming Webhook URL model is sufficient and standard).
  - Discord/Telegram specific formatting (can be added in future specialized notification components).

## 3. High-Level Approach
- Leverage `httpx.AsyncClient` inside `SlackWebhookComponent.execute()`.
- Dynamically build the Slack webhook payload dictionary omitting empty/None optional fields.
- Parse Slack response (HTTP 200 with text `"ok"` indicates success).
- Expose `MessageSquare` icon in Vue components with high-contrast Rose color palette to distinguish notifications from logic, transform, and trigger nodes.

## 4. Dependencies & Prerequisites
- `httpx` (already in `backend` dependencies).
- `lucide-vue-next` (already in `frontend` dependencies).
- Zero new external packages required.

## 5. Architectural Decision Records (ADRs)
- Relates to [ADR 0020: Slack Notification & Webhook Messaging Component](../../project/ADRs/0020-slack-notification-component.md).
