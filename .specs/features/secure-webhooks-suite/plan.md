# Feature Plan: Secure Webhook Authentication and Integration Clarity

## 1. Problem Statement
Users need clear, flexible, and secure methods to protect Webhook triggers with API keys or tokens.
Previously, `WebhookTriggerComponent` had a generic `secret_token` with unspecified transport semantics, and the server did not enforce authentication. Users could not tell whether tokens should be sent as headers, Bearer tokens, or query parameters, nor could they customize header names or view cURL examples.

## 2. Goals & Success Criteria
- Add explicit authentication modes to `WebhookTriggerComponent`: `none`, `api_key_header`, `bearer`, `api_key_query`.
- Allow customizable header name (`auth_header_name`) and query parameter name (`auth_query_param`).
- Enforce authentication in `/api/v1/webhooks/{path}`, returning HTTP 401 on unauthorized calls.
- Display authentication status and copyable cURL commands in `FlowsModal.vue`.
- Ensure 100% test pass rate across backend and frontend suites.

## 3. Scope Boundaries
- **In Scope**:
  - `WebhookTriggerComponent` inputs update (`auth_type`, `auth_header_name`, `auth_query_param`, `auth_token`).
  - Webhook route authentication validator with HTTP 401 error responses.
  - `webhook.ts` utility extension for cURL generation and auth summaries.
  - `FlowsModal.vue` UI updates with security badges and cURL copy button.
  - Pytest and Vitest test suites.
- **Out of Scope**:
  - Asymmetric HMAC signature algorithms (Milestone 4+).
