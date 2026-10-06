# ADR 0002: Persistence, Execution History, Logic Nodes, and Freeze/Unfreeze Replay

## Status
Accepted

## Context
FlowBuild requires advanced production automation capabilities:
1. Persistent Flow CRUD (create, read, update, delete, activate/deactivate flows).
2. Advanced HTTP Request Authentication (None, Bearer Token, Basic Auth, Header API Key, Query API Key).
3. Logical control flow nodes (`IfConditionComponent`, `DelayComponent`).
4. Dedicated Webhook Trigger router (`/api/v1/webhooks/{token_or_path}`).
5. Automated Cron execution (`CronTriggerComponent` + background scheduler using `croniter`).
6. Execution History database recording start, duration, trigger type, and per-node input/output state snapshots.
7. Idempotent Retry Engine with two distinct modes:
   - **Freeze Retry**: Re-executes the flow resuming strictly from failed or pending nodes, injecting the exact frozen output snapshots of already successful upstream nodes. Prevents duplicate charges on paid third-party APIs or external side-effects.
   - **Unfreeze Retry**: Re-executes the entire flow afresh with the original initial inputs.

## Decision
1. **Persistence Layer**:
   - Use Python's built-in `sqlite3` database engine stored at `backend/flowbuild.db` (with WAL mode enabled for high concurrent read/write throughput).
   - Tables:
     - `flows`: `id`, `name`, `description`, `is_active`, `flow_data` (JSON), `created_at`, `updated_at`.
     - `executions`: `id`, `flow_id`, `trigger_type`, `status`, `started_at`, `completed_at`, `duration_ms`, `error_message`, `node_states` (JSON snapshot).
2. **Dynamic HTTP Authentication**:
   - Extend `HttpRequestComponent` with:
     - `auth_type`: select (`none`, `bearer`, `basic`, `api_key_header`, `api_key_query`).
     - `auth_token`: string (for Bearer or API Key).
     - `auth_username`, `auth_password`: string (for Basic Auth).
     - `auth_header_name`, `auth_query_param`: string.
     - `headers`, `params`: dict inputs.
3. **Control Flow / Logic Nodes**:
   - `IfConditionComponent`: evaluates dynamic expressions or field comparisons against incoming data, outputting to two distinct handles (`true` or `false`).
4. **Webhook Triggering**:
   - Router `ANY /api/v1/webhooks/{token_or_path}` matches active flows with `WebhookTriggerComponent`, injects request headers, query params, and body into the flow DAG, and executes asynchronously.
5. **Cron Scheduler**:
   - Background `asyncio` task monitoring active flows with `CronTriggerComponent`, scheduling jobs via `croniter` and firing automated executions without user presence.
6. **Freeze / Unfreeze Replay Engine**:
   - `POST /api/v1/executions/{id}/retry?mode=freeze|unfreeze`:
     - If `mode=freeze`: passes precomputed successful node outputs into the DAG context, skipping upstream nodes and executing only failed/unexecuted branches.
     - If `mode=unfreeze`: resets context and executes the complete DAG from scratch.
7. **Frontend Management Suite**:
   - Modal/Panel for Flow CRUD & Activation toggle.
   - Execution History tab in `ExecutionDrawer.vue` with list of executions and Retry (Freeze / Unfreeze) buttons.

## Consequences
- **Positive**:
  - Full production readiness: automated triggers, audit trails, and resilient disaster recovery.
  - Cost and side-effect safety via Freeze replay.
  - Zero external database daemon setup required (SQLite WAL provides sub-millisecond local operations).
- **Negative / Considerations**:
  - SQLite concurrent write locks must be handled cleanly using WAL mode and connection pooling/context managers.
