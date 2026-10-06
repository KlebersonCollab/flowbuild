# Feature Plan: Mandatory Trigger Node Requirement for Workflow Execution

## Problem Statement
Workflows without an explicit trigger node lead to ambiguous execution states, missing initial payloads, and violations of standard automation conventions where every workflow execution must be rooted in an event trigger (Manual, Webhook, Cron).

## Goals
1. Validate presence of at least one Trigger node before executing any workflow from the frontend canvas.
2. Provide immediate, non-intrusive UI feedback (toast/banner + console drawer warning) if execution is attempted without a trigger.
3. Enforce backend runtime validation in `/api/v1/flows/execute/stream` and `FlowRunner` when `require_trigger=True`.
4. Ensure all templates and existing integration flows continue to run seamlessly.

## Non-Goals
- Eliminating disconnected nodes from canvas editing (users can still keep nodes in draft while designing, but execution requires a trigger).

## Proposed Architecture
- **Frontend**:
  - `hasTriggerNode(nodes)` helper in `flowStore.ts` or `executionStore.ts`.
  - Guard in `onRunFlow` in `TopNav.vue` displaying warning and opening console log if missing.
- **Backend**:
  - `has_trigger_node()` check in `FlowRunner` using component registry metadata.
  - Fail-fast streaming response yielding `flow_failed` with descriptive error when trigger is absent.
