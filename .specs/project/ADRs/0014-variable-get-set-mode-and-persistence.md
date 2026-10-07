# ADR 0014: Variable Get/Set Mode Selection and Execution Persistence

## Status
Accepted

## Date
2026-10-07

## Context
In ADR 0003 and ADR 0004, a database-agnostic variables system with a 4-tier resolution hierarchy was introduced. Currently, `VariableComponent` operates solely in read ("get") mode, emitting the value of a pre-existing variable.

In real-world workflow automation, a fundamental requirement is dynamic variable writing ("set"). For instance, when a workflow calls an authentication endpoint (via `HttpRequestComponent`), it receives a session token, bearer token, or OAuth secret that needs to be stored either for subsequent nodes in the same execution or saved to the database (flow-scoped or global) for future workflow executions.

## Decision
1. **Unified Variable Component with Mode Selector**:
   - Enhance `VariableComponent` in `variables.py` with a `mode` input (`SelectInput: ["get", "set"]`, default `"get"` for 100% backward compatibility).
   - In `mode == "get"`:
     - Inputs: `variable_name` (required), `default_value` (fallback).
     - Resolves variable from runtime inputs, active environment, flow scope, or global database.
     - Outputs: `value` (the resolved value).
   - In `mode == "set"`:
     - Inputs: `variable_name` (required), `value` (the data to store, connectable from upstream handles or typed), `scope` (`SelectInput: ["flow", "global"]`, default `"flow"`), and `persist` (`BoolInput`, default `True`).
     - Emits outputs: `value` (the written value, allowing pipeline chaining), `variable_name`, `success` (`True`).
2. **Runtime Propagation & FlowRunner Integration**:
   - When a node executes `mode == "set"`:
     - `FlowRunner` updates its active execution variables map (`self.custom_variables[var_name] = value`), making the updated value immediately available to downstream nodes in the DAG and within string template interpolation `{{var_name}}`.
     - When `persist == True`:
       - Persists to the database via `db_manager.upsert_variable(key=var_name, value=str(value), scope=scope, flow_id=self.flow.id, environment=self.environment)`.
3. **Database Upsert Utility**:
   - Add `upsert_variable` in `db_manager` to atomically insert or update existing records by key, scope, flow ID, and environment without constraint conflicts.

## Consequences
- **Positive**: Enables dynamic authentication flows, token caching, state accumulation, and parameter passing without leaving the FlowBuild visual canvas.
- **Backward Compatibility**: Fully backward compatible with existing flows using `VariableComponent` (which default to `mode == "get"`).
