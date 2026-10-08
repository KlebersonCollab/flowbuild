# Plan: Email Notification Component (ADR 0024)

## 1. Problem Statement & Motivation
Email notifications and transactional dispatches are fundamental to automated systems, from database failure alerts to scheduled weekly reports and confirmation messages. While webhooks exist for chat apps, email is universally required in enterprise systems.

The `EmailNotificationComponent` gives FlowBuild users the ability to send emails directly via standard SMTP servers (Gmail, SendGrid, Mailgun, Amazon SES, or self-hosted Postfix) with HTML, plaintext, authentication, and TLS/SSL configuration.

## 2. Scope & Boundaries
- **In Scope**:
  - Implement `EmailNotificationComponent` in `backend/src/backend/app/components/builtins/actions.py` and register in `backend/src/backend/app/components/builtins/__init__.py`.
  - Configurable parameters: `smtp_host`, `smtp_port`, `smtp_user`, `smtp_password`, `use_tls`, `use_ssl`, `from_email`, `to_email`, `subject`, `body_html`, `body_text`, `timeout`.
  - Non-blocking execution via `asyncio.to_thread` using Python standard library `smtplib` and `email.mime`.
  - Outputs: `success`, `status_code`, `response`, and `recipients_count`.
  - Support comma-separated recipient addresses in `to_email`.
  - Exception handling for authentication, connection, and TLS errors.
  - Template variable interpolation (`{{VARIABLE}}`) through `FlowRunner`.
  - UI updates in `CustomNode.vue` and `ComponentPalette.vue` with `Mail` icon and Violet styling.
  - Integration tests for backend and frontend.
- **Out of Scope**:
  - IMAP/POP3 inbound email polling (trigger node for future roadmap item).

## 3. High-Level Approach
- Use standard library `smtplib` and `email.mime` inside `asyncio.to_thread`.
- TDD cycle: test first with mock SMTP servers, verify failures, implement, test frontend, update styling, audit sensors.

## 4. Dependencies & Prerequisites
- Python standard library `smtplib` and `email.mime` (zero new external packages needed).
- `lucide-vue-next` (has `Mail` icon).

## 5. Architectural Decision Records (ADRs)
- Relates to [ADR 0024: Email Notification Component (SMTP Delivery)](../../project/ADRs/0024-email-notification-component.md).
