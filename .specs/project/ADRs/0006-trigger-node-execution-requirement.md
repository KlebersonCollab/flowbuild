# ADR 0006: Mandatory Trigger Node Requirement for Workflow Execution

## Status
Accepted

## Context
In DAG-based workflow automation engines (such as n8n, Make, Langflow, and Zapier):
1. **Workflow Origin**: Every automated or manual workflow execution originates from an initial trigger node (e.g. `ManualTriggerComponent`, `WebhookTriggerComponent`, or `CronTriggerComponent`).
2. **Missing Invariants**: Previously, FlowBuild allowed running canvas payloads containing arbitrary action nodes without any trigger, or with orphan nodes having `in_degree == 0`. This caused confusion regarding entry points, payload sources, and execution semantics.
3. **User Intent**: The user explicitly confirmed that workflows must begin with an initial trigger node and follow the graph through connected edges.

## Decision
1. **Frontend Trigger Validation**:
   - In `TopNav.vue` and `executionStore.ts`, prior to dispatching execution, validate whether `flowStore.nodes` contains at least one trigger node (node whose `type` contains `"Trigger"` or whose category in `ComponentRegistry` is `"Triggers"`).
   - If no trigger node is present (or canvas is empty), abort execution immediately, display a visible feedback notification, and append an informative warning event in `ExecutionDrawer.vue` guiding the user to add a Trigger from the component palette.
2. **Backend Execution Guard**:
   - In `FlowRunner` and `/api/v1/flows/execute/stream`, enforce trigger validation when `require_trigger=True` (enabled by default for runtime executions).
   - If a flow contains nodes but zero triggers, reject execution with `WorkflowValidationError` / stream `flow_failed` event with message: `"O workflow precisa de pelo menos um nó Trigger inicial (ex: Manual Trigger, Webhook ou Cron) para ser executado."`.
   - Maintain backward compatibility for isolated topological sort unit tests by defaulting `require_trigger=False` in low-level `FlowRunner` constructor when called directly in tests unless specified.
3. **Visual Cues & Feedback**:
   - Provide direct feedback in the execution console drawer explaining the requirement.

## Consequences
- **Positive**: Strict workflow semantics matching standard industry patterns (n8n/Zapier), clear entry points for initial payloads, and immediate feedback preventing ambiguous execution of headless flows.
- **Negative**: Workflows composed purely of standalone action nodes must be prepended with a `ManualTriggerComponent` to be executed.
