# ADR 0009: Conditional Branch Skipping in DAG Runner

## Status
Accepted

## Context
1. **The Problem**: In DAG-based automation engines (such as n8n, Make, Langflow), an `IF Condition` node evaluates incoming data and routes execution to either a `true_branch` or `false_branch`.
2. **Current Limitation**: Previously, `IfConditionComponent` produced `None` for the inactive branch handle, but `FlowRunner` did not implement branch skipping. Downstream nodes connected exclusively to the inactive branch were executed anyway with `input_data = None`. Furthermore, when a node was skipped, `ExecutionContext` and `executionStore` treated it as a failure (`status = 'failed'`) rather than an intentional conditional skip.
3. **User Intent**: The user explicitly requested proper `IF Condition` flow execution, verifying that only the active branch runs and downstream nodes on the inactive branch are cleanly skipped.

## Decision
1. **Conditional Branch Detection in `FlowRunner`**:
   - In `FlowRunner.execute_stream()`, check incoming edges before executing a node:
     - If an incoming edge originates from a conditional handle (`true_branch` or `false_branch`) whose value in `self.context.results[edge.source]` is `None`, mark the target node as skipped (`reason: "condition_not_met"`).
     - If an incoming edge originates from an upstream node that was already skipped, cascade the skipped state down the path (`reason: "upstream_skipped"`).
   - Yield a `node_skipped` event with the specific skip reason without marking the workflow execution as failed.
2. **Skipped State in `ExecutionContext`**:
   - Add `self.skipped: set[str]` to `ExecutionContext`.
   - Ensure conditional skipping preserves `status = 'completed'` for the overall flow when the active branch succeeds.
3. **Frontend Telemetry & Logging in `executionStore`**:
   - In `executionStore.ts`, handle `node_skipped` cleanly with level `info`/`warn` explaining whether it was due to an inactive conditional branch or an upstream error.
4. **Pre-configured Canvas Template**:
   - Add template `"if_condition_flow"` (*"Decisão Condicional IF / Else"*) in `TopNav.vue` and `flowStore.ts` allowing immediate 1-click testing of conditional branching directly on the canvas.

## Consequences
- **Positive**: Real conditional branching matching industry automation standards (n8n, Make). Inactive branches are skipped without unwanted side-effects or API calls.
- **Positive**: Clear visual telemetry in execution console logs explaining which branch was taken and which nodes were skipped.
- **Neutral**: Nodes intended to run regardless of the condition should not be connected exclusively downstream of an inactive branch.
