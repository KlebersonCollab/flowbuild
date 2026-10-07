# Feature Plan: Multi-Method Webhook Support (GET, POST, PUT, DELETE, ANY)

## Problem Statement
The FlowBuild webhook trigger was previously hardcoded to accept only `POST` requests, throwing `405 Method Not Allowed` when invoked via `GET`, `PUT`, or `DELETE`. Webhook consumers often require `GET` for challenge handshakes or query-string data ingestion, `PUT` for updates, and `DELETE` for removal triggers.

## Goals
1. Enable `GET`, `POST`, `PUT`, `DELETE`, `PATCH`, and `ANY` HTTP methods on `/api/v1/webhooks/{webhook_path:path}`.
2. Ingest query parameters (`request.query_params`) as the node payload for `GET` requests (and as fallback for empty-body requests).
3. Validate and enforce configured HTTP method matching with descriptive `405 Method Not Allowed` feedback when methods mismatch.
4. Support `ANY` / `*` method wildcard on `WebhookTriggerComponent`.
5. Update `WebhookTriggerComponent` implementation to properly handle input/kwargs updates and headers output.
6. Display HTTP method indicator badge alongside the webhook URL in the frontend `FlowsModal.vue`.
7. Maintain 100% test coverage and ensure all existing tests remain green.

## Non-Goals
- Custom response status codes or custom response bodies per webhook (all webhook executions return the canonical execution summary).

## Proposed Architecture
- **Backend API (`backend/src/backend/app/api/routes.py`)**:
  - Replace `@router.post(...)` with `@router.api_route("/webhooks/{webhook_path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])`.
  - Parse `request.query_params` and `request.json()` intelligently.
  - Implement two-stage matching: path matching and method matching.
  - Return `405 Method Not Allowed` when path matches but method doesn't.
- **Backend Component (`backend/src/backend/app/components/builtins/triggers.py`)**:
  - Fix `execute(**kwargs)` in `WebhookTriggerComponent` to safely update `self._raw_inputs` and retain headers.
- **Frontend UI (`frontend/src/components/FlowsModal.vue`)**:
  - Show the method tag (`GET`, `POST`, `ANY`, etc.) alongside the webhook path.
