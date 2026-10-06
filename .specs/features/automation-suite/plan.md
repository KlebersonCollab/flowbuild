# Feature Plan: Automation Engine Suite (Persistence, Logic, Crons, History & Retry)

## 1. Executive Summary
Expand FlowBuild into a full-scale automation engine inspired by Langflow and modern iPaaS platforms (n8n, Make). This includes persistent Flow CRUD with active/inactive flags, advanced HTTP authentication, logical branching nodes, dedicated webhooks, background cron scheduling, execution history auditing, and freeze vs. unfreeze replay capabilities.

## 2. Problem Statement
The initial implementation provided an in-memory runtime and dynamic canvas. To support real-world production automations, users need:
- Persistent storage for flows and activation state.
- Flexible HTTP authentication (Bearer, Basic, API Key) and custom headers.
- Branching logic (`IfConditionComponent`) to handle conditional workflows.
- Webhook endpoints that accept payloads and run workflows asynchronously.
- Independent, headless cron scheduling for periodic tasks.
- Detailed audit logs and execution history.
- Smart disaster recovery via Freeze replay (preserving successful upstream data) vs Unfreeze replay (fresh restart).

## 3. High-Level Scope
- **Database & Persistence**: SQLite with WAL mode (`flows` and `executions` tables).
- **HTTP Component Enhancements**: Auth schemes (Bearer, Basic, API Key), headers, params.
- **Control Flow & Automation Nodes**:
  - `IfConditionComponent` (conditional branching).
  - `CronTriggerComponent` (scheduled periodic triggers).
- **Automation Services**:
  - `FlowService` (CRUD, activation).
  - `ExecutionService` (run tracking, history, freeze/unfreeze replay).
  - `SchedulerService` (background asyncio cron engine).
  - `WebhookRouter` (dynamic route matching).
- **Frontend Management**:
  - Flows management modal / drawer with activation toggle.
  - Execution History tab with live telemetry and Retry (Freeze / Unfreeze) buttons.
