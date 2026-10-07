# ADR 0007: Multi-Method Webhook Support (GET, POST, PUT, DELETE, ANY)

## Status
Accepted

## Context
1. **Initial Limitation**: The FlowBuild webhook listener was initially bound exclusively to `@router.post("/webhooks/{webhook_path:path}")`.
2. **Real-World Integration Constraints**: Industry-standard automation platforms (such as n8n, Zapier, Make, and webhook providers like Stripe, WhatsApp Cloud API, GitHub, and Shopify) often require HTTP `GET` for webhook challenge verification or query-string ingestion, `PUT` for state synchronization, and `DELETE` for resource deprecation events.
3. **User Feedback**: The user experienced a `405 Method Not Allowed` when changing the trigger method to `GET`, highlighting that webhooks must not be locked solely to `POST`.
4. **Existing Schema Readiness**: `WebhookTriggerComponent` already defines an `HTTP Method` input field, but the backend routing was hardcoded to `POST` and did not evaluate or match HTTP methods.

## Decision
1. **FastAPI Route Generalization**:
   - Change `@router.post(...)` to `@router.api_route("/webhooks/{webhook_path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])`.
2. **Payload Extraction Strategy**:
   - For `GET`: Parse query parameters (`request.query_params`) into the input payload dictionary.
   - For `POST` / `PUT` / `PATCH` / `DELETE`: Attempt JSON body parsing; if the body is empty and query parameters exist, use query parameters as payload.
   - Inject request headers into `WebhookTriggerComponent` inputs (`headers`).
3. **Method Matching & Validation**:
   - When resolving the target active flow for a given webhook path, evaluate the configured `method` (case-insensitive):
     - If the node's configured method is `ANY` or `*`, accept any HTTP method.
     - If the node's configured method matches the incoming request method, execute the flow.
     - If the path matches an active flow but the HTTP method does not match, return `405 Method Not Allowed` with a clear explanation (`"Webhook configured to accept {allowed_method}, but received {incoming_method}"`).
     - If no active flow matches the path at all, return `404 Not Found`.
4. **UI Visibility**:
   - In `FlowsModal.vue`, display the accepted HTTP method tag alongside the webhook URL endpoint banner (e.g. `[GET] /api/v1/webhooks/...` or `[POST] /api/v1/webhooks/...`).

## Consequences
- **Positive**: Comprehensive webhook compatibility across all modern integration providers and verification callbacks without requiring dedicated routing hacks.
- **Positive**: Clear 405 error messages identifying method mismatches rather than generic FastAPI rejections.
- **Positive**: Seamless handling of query parameters for lightweight GET webhooks.
- **Neutral**: None. Existing POST webhooks remain 100% backward compatible.
