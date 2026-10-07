# Task List: Secure Webhook Authentication and Integration Clarity

## Sequence Guidelines (MetaGPT SOP)
- **Strict Sequential Order**: Tasks must be executed top-to-bottom without reordering.
- **Atomic File Boundaries**: Each task modifies at most 1–3 specific target files.
- **Decoupled Test Setup**: Test tasks (`Type: test`) precede implementation tasks (`Type: feat`).
- **Sensor Evidence Gate**: Mark complete `[x]` ONLY after passing build, lint, and test sensors with recorded evidence.

## Implementation Tasks

| Status | ID | Type | Description | Target Files | Dependencies | Evidence |
|---|---|---|---|---|---|---|
| [x] | TASK-01 | test | Add backend integration tests for webhook authentication modes (api_key_header, bearer, api_key_query, and 401 responses) | `backend/tests/test_webhook_security.py` | None | `d01b026` + `pytest tests/test_webhook_security.py 5 passed` |
| [x] | TASK-02 | feat | Update WebhookTriggerComponent inputs with auth_type, auth_header_name, auth_query_param, and auth_token | `backend/src/backend/app/components/builtins/triggers.py` | TASK-01 | `d01b026` + `triggers.py inputs validated with backward compatibility` |
| [x] | TASK-03 | feat | Enforce webhook authentication in FastAPI routes with 401 Unauthorized handling on missing or invalid tokens | `backend/src/backend/app/api/routes.py` | TASK-02 | `d01b026` + `routes.py 401 Unauthorized enforcement verified` |
| [x] | TASK-04 | feat | Extend webhook.ts with auth metadata and cURL command generator, and add security badges and copy cURL to FlowsModal | `frontend/src/utils/webhook.ts`, `frontend/src/components/FlowsModal.vue` | TASK-03 | `d01b026` + `webhook.ts & FlowsModal.vue auth badge & copy cURL button added` |
| [x] | TASK-05 | test | Add frontend unit tests for webhook auth metadata parsing, security badges and cURL generation | `frontend/tests/flows_modal_webhook.test.ts` | TASK-04 | `d01b026` + `vitest tests/flows_modal_webhook.test.ts 13 passed` |
| [x] | TASK-06 | review | Run full sensor verification (Pytest suite, Vitest suite, Vue build, and SDD integrity sensor) | `backend/`, `frontend/`, `.specs/` | TASK-05 | `d01b026` + `62 pytest passed, 46 vitest passed, vue-tsc & vite build OK, sdd sensor OK` |

## Schema Dictionary
- **Status**: `[ ]` (Pending) | `[x]` (Verified Complete).
- **ID**: `TASK-01`, `TASK-02`, etc.
- **Type**: `test` | `feat` | `fix` | `refactor` | `docs` | `rules` | `skill` | `review`.
- **Target Files**: Concrete comma-separated file paths (relative to workspace root).
- **Dependencies**: Comma-separated list of preceding task IDs or `None`.
- **Evidence**: Commit hash (`git rev-parse --short HEAD`) + sensor output snippet.
