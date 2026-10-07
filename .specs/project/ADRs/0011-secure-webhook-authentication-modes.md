# ADR 0011: Configurable Webhook Authentication and Security Modes

## Status
Accepted

## Date
2026-10-06

## Context
Previously, `WebhookTriggerComponent` included an ambiguous `secret_token` field with no explicit transport protocol. The FastAPI router `/api/v1/webhooks/{webhook_path}` did not enforce token verification, and users had no clarity or control over:
1. Which transport mechanism to use (`Authorization: Bearer`, custom header like `X-API-Key` or `X-Webhook-Token`, or URL query parameter `?api_key=...`).
2. Customizing the header or parameter name to match third-party webhook sender specifications (e.g. Stripe, GitHub, Shopify, custom microservices).
3. Viewing ready-to-run cURL integration snippets with proper authentication flags in the UI.

## Decision
1. **Schema & Configuration in `WebhookTriggerComponent`**:
   - `auth_type`: `SelectInput` with options `["none", "api_key_header", "bearer", "api_key_query"]` (default: `"none"`).
   - `auth_header_name`: `StrInput` (default: `"X-API-Key"`, placeholder: `"X-API-Key ou X-Webhook-Token"`).
   - `auth_query_param`: `StrInput` (default: `"api_key"`, placeholder: `"api_key ou token"`).
   - `auth_token`: `StrInput` (placeholder: `"chave_secreta_webhook"`).
   - `secret_token`: Maintained for backward compatibility (maps to `auth_token` if set).

2. **Server-Side Enforcement in `/api/v1/webhooks/{webhook_path}`**:
   - For `api_key_header`: compares `request.headers.get(auth_header_name)` against `auth_token`. Rejects with HTTP 401 on mismatch.
   - For `bearer`: extracts `Authorization` header, verifies `Bearer <token>` against `auth_token`. Rejects with HTTP 401 on mismatch.
   - For `api_key_query`: extracts `request.query_params.get(auth_query_param)`. Rejects with HTTP 401 on mismatch.
   - For `none` (or empty `auth_token`): allows request to proceed.

3. **Frontend Developer Experience**:
   - In `FlowsModal.vue`, display authentication badge per flow (e.g. `🔓 Público`, `🔒 Header: X-API-Key`, `🔒 Bearer`, `🔒 Query: ?api_key`).
   - Add a "Copiar cURL" action button that generates the exact CLI command with method, headers, auth token, and JSON body.

## Consequences
- **Positive**: High security standard for webhook endpoints, preventing unauthorized trigger invocations.
- **Positive**: Complete flexibility to integrate with any external provider's signature/header format.
- **Positive**: Zero ambiguity for developers: cURL snippets and header names are clearly documented and copyable directly from the UI.
- **Negative**: Callers must send the configured token or receive HTTP 401.
