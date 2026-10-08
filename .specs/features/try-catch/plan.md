# Plan: Try / Catch Error Boundary Component (ADR 0031)

## 1. Problem Statement & Motivation
Network partitions, HTTP 500 errors, database deadlocks, and invalid payloads are unavoidable in integration workflows. Without error boundary handling, an error anywhere in the DAG kills the entire flow, preventing recovery or notification actions.

The `TryCatchComponent` introduces native error boundary and branch routing to FlowBuild, allowing automations to recover gracefully, emit fallback values, and trigger error notification pipelines.

## 2. Scope & Boundaries
- **In Scope**:
  - Implement `TryCatchComponent` in `backend/src/backend/app/components/builtins/logic.py` and register in `backend/src/backend/app/components/builtins/__init__.py`.
  - Update `FlowRunner` in `backend/src/backend/app/engine/runner.py` to:
    1. Intercept predecessor failures when the downstream node is `TryCatchComponent`.
    2. Support branch skipping on `"success_branch"` and `"error_branch"`.
  - Inputs: `input_data`, `fallback_value`, `catch_upstream_errors`, `error_message`.
  - Outputs: `success_branch`, `error_branch`, `result`, `has_error`, `error_details`.
  - UI updates in `CustomNode.vue` and `ComponentPalette.vue` using `ShieldAlert` icon and Rose styling.
  - Unit and integration tests in backend and frontend.
- **Out of Scope**:
  - Automatic retry with exponential backoff (which is handled at execution run retry or future queue workers).

## 3. High-Level Approach
- TDD cycle: test first, verify failure, implement in `logic.py` and `runner.py`, test frontend canvas, audit sensors.

## 4. Dependencies & Prerequisites
- `FlowRunner` branch skipping mechanism.
- `lucide-vue-next` (has `ShieldAlert` icon).

## 5. Architectural Decision Records (ADRs)
- Relates to [ADR 0031: Try / Catch Error Boundary Component and Upstream Resilience](../../project/ADRs/0031-try-catch-component.md).
