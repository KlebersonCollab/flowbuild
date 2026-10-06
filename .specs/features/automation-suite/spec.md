# Feature Spec: Automation Engine Suite

## 1. Domain Glossary Alignment
- **Flow**: A directed acyclic graph composed of nodes and edges representing an automation sequence.
- **Freeze Replay**: A retry strategy where only failed or downstream nodes re-execute, injecting the exact cached outputs of previously successful upstream nodes.
- **Unfreeze Replay**: A retry strategy where all nodes re-execute from scratch using the original trigger payload.
- **Execution Snapshot**: Immutable record of an execution containing per-node inputs, outputs, errors, durations, and timestamps.
- **Active Flow**: A persisted flow eligible for automatic triggering via Webhooks or Crons.

## 2. User Stories
- **US-1 (HTTP Auth)**: As an automator, I want to configure Bearer tokens, Basic auth, or API keys directly in the HTTP node, so that I can call protected APIs without manual header formatting.
- **US-2 (Logic Nodes)**: As an automator, I want an IF condition node, so that my workflow can branch conditionally based on incoming data.
- **US-3 (Webhook & Crons)**: As an automator, I want independent triggers (Webhooks and Crons), so that my flows run automatically in background without keeping the browser open.
- **US-4 (Flow CRUD & Activation)**: As an automator, I want to manage multiple saved flows and activate/deactivate them, so that I can control what runs in production.
- **US-5 (History & Freeze Retry)**: As an automator, I want to inspect execution history and retry failed runs with Freeze, so that I don't re-bill expensive upstream API calls or repeat external actions.

## 3. Business Rules & Invariants
- `BR-1`: Inactive flows (`is_active = False`) MUST reject incoming webhook triggers (HTTP 403) and MUST NOT be scheduled by the Cron engine.
- `BR-2`: In `freeze` retry mode, upstream nodes marked as `completed` MUST NOT re-run their `execute()` method; their previous output MUST be injected directly into dependent nodes.
- `BR-3`: In `unfreeze` retry mode, all nodes MUST re-run their `execute()` methods from scratch.
- `BR-4`: All flow persistence operations MUST be transaction-safe using SQLite WAL mode.

## 4. Acceptance Criteria (BDD)

### AC-1: HTTP Request Authentication
- **Given** an `HttpRequestComponent` with `auth_type = 'bearer'` and `auth_token = 'secret123'`.
- **When** the node executes an HTTP request.
- **Then** the request contains header `Authorization: Bearer secret123`.

### AC-2: Conditional Branching Logic
- **Given** an `IfConditionComponent` receiving `input_data = {'status': 'active'}` with expression `data.get('status') == 'active'`.
- **When** the node executes.
- **Then** output port `true` receives the data and output port `false` receives `None` (or remains un-triggered).

### AC-3: Flow Persistence & CRUD
- **Given** a valid flow JSON payload.
- **When** sent to `POST /api/v1/flows`.
- **Then** a 201 response returns the created flow with `is_active = True`, and `GET /api/v1/flows` lists the flow.

### AC-4: Freeze vs Unfreeze Replay
- **Given** an execution record with node A (`completed`, output `{costly_call: 1}`) and node B (`failed`).
- **When** retrying with `POST /api/v1/executions/{id}/retry?mode=freeze`.
- **Then** node A is skipped and node B re-runs with node A's cached output.
