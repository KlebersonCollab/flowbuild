# Task List: Multi-Method Webhook Support (GET, POST, PUT, DELETE, ANY)

## Sequence Guidelines (MetaGPT SOP)
- **Strict Sequential Order**: Tasks must be executed top-to-bottom without reordering.
- **Atomic File Boundaries**: Each task modifies at most 1–3 specific target files.
- **Decoupled Test Setup**: Test tasks (`Type: test`) precede implementation tasks (`Type: feat`).
- **Sensor Evidence Gate**: Mark complete `[x]` ONLY after passing build, lint, and test sensors with recorded evidence.

## Implementation Tasks

| Status | ID | Type | Description | Target Files | Dependencies | Evidence |
|---|---|---|---|---|---|---|
| [x] | TASK-01 | test | Add backend integration tests for multi-method webhooks (GET query params, POST body, ANY method, and 405 method mismatch) | `backend/tests/test_multi_method_webhooks.py` | None | [test_multi_method_webhooks.py] 4 test cases added (GET query params, POST body, ANY wildcard, and 405 method mismatch) |
| [x] | TASK-02 | feat | Update WebhookTriggerComponent to safely receive kwargs and expose headers | `backend/src/backend/app/components/builtins/triggers.py` | TASK-01 | [triggers.py] Updated WebhookTriggerComponent _raw_inputs handling, headers extraction, and method description |
| [x] | TASK-03 | feat | Generalize webhook route to support GET, POST, PUT, DELETE, PATCH, query params extraction, and method matching | `backend/src/backend/app/api/routes.py` | TASK-02 | [routes.py] Converted to api_route, added query params ingestion, case-insensitive method matching, and descriptive 405 |
| [x] | TASK-04 | test | Add frontend unit tests verifying method extraction and display in FlowsModal | `frontend/tests/flows_modal_webhook.test.ts` | TASK-03 | [flows_modal_webhook.test.ts] 4 vitest test cases verifying path/method parsing and ANY wildcard |
| [x] | TASK-05 | feat | Update FlowsModal to display HTTP method badge alongside webhook endpoint | `frontend/src/components/FlowsModal.vue`, `frontend/src/utils/webhook.ts` | TASK-04 | [FlowsModal & webhook.ts] Added getWebhookInfo helper, method badge in Linear Dark cyan palette, and clean build |
| [x] | TASK-06 | review | Run full sensor verification (Pytest, Vitest, Vue build, and SDD integrity sensor) | `backend/`, `frontend/`, `.specs/` | TASK-05 | 47/47 Pytest passing, 28/28 Vitest passing, clean vue-tsc build in 678ms, SDD sensor 100% OK |

## Schema Dictionary
- **Status**: `[ ]` (Pending) | `[x]` (Verified Complete).
- **ID**: `TASK-01`, `TASK-02`, etc.
- **Type**: `test` | `feat` | `fix` | `refactor` | `docs` | `rules` | `skill` | `review`.
- **Target Files**: Concrete comma-separated file paths (relative to workspace root).
- **Dependencies**: Comma-separated list of preceding task IDs or `None`.
- **Evidence**: Commit hash (`git rev-parse --short HEAD`) + sensor output snippet.
