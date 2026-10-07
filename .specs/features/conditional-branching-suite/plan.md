# Feature Plan: Conditional Branch Skipping in DAG Runner

## Problem Statement
When an `IfConditionComponent` evaluates to `True` or `False`, nodes on the non-selected branch should not execute. Previously, `FlowRunner` did not evaluate whether an incoming branch was active, executing inactive branch nodes with `None` values and failing or producing corrupt results.

## Goals
1. Implement conditional branch skipping in `FlowRunner` for handles `true_branch` and `false_branch`.
2. Cascade skipped status down all downstream nodes belonging exclusively to the inactive branch.
3. Track skipped nodes in `ExecutionContext` without marking the entire flow as failed.
4. Support clean telemetry in `executionStore.ts` and `ExecutionDrawer.vue` when nodes are skipped.
5. Create a pre-configured canvas template `"if_condition_flow"` in `flowStore.ts` and `TopNav.vue` for testing.
6. Provide comprehensive backend and frontend unit tests.

## Non-Goals
- Merging disparate branches (Join/Merge node) is out of scope for this task and can be added later.

## Proposed Architecture
- `backend/src/backend/app/engine/context.py`: Add `skipped` tracking to `ExecutionContext`.
- `backend/src/backend/app/engine/runner.py`: Add check for inactive conditional edges and cascaded skip logic.
- `frontend/src/stores/executionStore.ts`: Update `node_skipped` event handler.
- `frontend/src/stores/flowStore.ts` & `frontend/src/components/TopNav.vue`: Add `"if_condition_flow"` template.
