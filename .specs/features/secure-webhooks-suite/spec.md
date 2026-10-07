# Feature Specification: Secure Webhook Authentication and Integration Clarity

## 1. WebhookTriggerComponent Schema Specification
Component: `WebhookTriggerComponent`
Category: `Triggers`

| Input Name | Type | Default | Description |
|---|---|---|---|
| `path` | StrInput | `"/webhook/default"` | Path suffix for incoming webhook HTTP calls |
| `method` | SelectInput | `"POST"` | Allowed HTTP method: `POST`, `GET`, `PUT`, `DELETE`, `PATCH`, `ANY` |
| `auth_type` | SelectInput | `"none"` | Security mode: `none`, `api_key_header`, `bearer`, `api_key_query` |
| `auth_header_name` | StrInput | `"X-API-Key"` | Custom header name when `auth_type` is `api_key_header` |
| `auth_query_param` | StrInput | `"api_key"` | Custom query parameter name when `auth_type` is `api_key_query` |
| `auth_token` | StrInput | `""` | Expected secret key or token for authorization |
| `secret_token` | StrInput | `""` | Deprecated fallback alias for `auth_token` |
| `payload` | DictInput | `{}` | Injected incoming request payload |

## 2. Server-Side Authentication Verification
Route: `/api/v1/webhooks/{webhook_path:path}`
Methods: `POST`, `GET`, `PUT`, `DELETE`, `PATCH`

### Verification Matrix
- If `auth_type == "none"` (or resolved token is empty):
  - Request is accepted.
- If `auth_type == "api_key_header"`:
  - Header `request.headers.get(auth_header_name)` must equal `auth_token`.
  - Mismatch or absent: HTTP 401 Unauthorized (`detail: "Invalid or missing API key in '{auth_header_name}' header"`).
- If `auth_type == "bearer"`:
  - Header `request.headers.get("authorization")` must be `Bearer <auth_token>`.
  - Mismatch or absent: HTTP 401 Unauthorized (`detail: "Invalid or missing Bearer token in 'Authorization' header"`).
- If `auth_type == "api_key_query"`:
  - Query parameter `request.query_params.get(auth_query_param)` must equal `auth_token`.
  - Mismatch or absent: HTTP 401 Unauthorized (`detail: "Invalid or missing query parameter '{auth_query_param}'"`).

## 3. Frontend Integration Requirements
- In `FlowsModal.vue`:
  - Display security badge alongside HTTP method badge:
    - `none`: `🔓 Aberto` (cinza)
    - `api_key_header`: `🔒 Header: <header_name>` (azul)
    - `bearer`: `🔒 Bearer Token` (roxo)
    - `api_key_query`: `🔒 Query: ?<query_param>` (âmbar)
  - Provide a "Copiar cURL" button in addition to "Copiar URL":
    - Produces a complete curl snippet with method, URL, headers/query param with token, and `-d '{"test": "payload"}'`.
