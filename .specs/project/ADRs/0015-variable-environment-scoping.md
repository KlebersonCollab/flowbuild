# ADR 0015: Variable Environment Scoping and Target Environment Selection

## Status
Accepted

## Date
2026-10-07

## Context
In ADR 0004 and ADR 0014, FlowBuild established a multi-environment architecture (`dev`, `qa`, `prd`, `all`) and enhanced `VariableComponent` with `get`/`set` modes, scoping (`flow` vs `global`), and database persistence.
However, `VariableComponent` previously lacked an explicit node-level `environment` input selector, meaning the user could not define whether a set or get operation targeted the currently executing environment, a specific environment (`dev`, `qa`, `prd`), or universal availability (`all`).

In multi-stage enterprise pipelines, workflows may need to:
1. Dynamically store credentials or state targeting the active environment (`current`), allowing seamless promotion across DEV -> QA -> PRD without manual node adjustments.
2. Store universal tokens or configuration parameters valid across all environments (`all`).
3. Explicitly target a specific target environment (e.g. rotating a token specifically in `prd` or initializing test data in `qa`).

## Decision
1. **Add `environment` Input Selector to `VariableComponent`**:
   - `SelectInput`:
     - `name="environment"`
     - `label="Environment"`
     - `options=["current", "all", "dev", "qa", "prd"]`
     - `default="current"`
     - `description="Target environment: 'current' (inherits flow environment), 'all' (shared), or specific ('dev', 'qa', 'prd')"`
2. **Runtime Environment Resolution**:
   - In `execute()`:
     - If `environment == "current"`: resolves to `_environment` from `self._raw_inputs` (defaults to `"dev"`).
     - Otherwise, uses the explicitly configured environment (`"all"`, `"dev"`, `"qa"`, `"prd"`).
   - In `mode == "set"`:
     - Passes resolved `target_env` to `db_manager.upsert_variable(..., environment=target_env)`.
   - In `mode == "get"`:
     - Uses resolved `target_env` when resolving against `db_manager.resolve_variable_value(..., environment=target_env)`.
3. **Frontend Integration**:
   - Registered in component definition schema so `NodeInspector.vue` and `CustomNode.vue` automatically expose the dropdown selector.

## Consequences
- **Positive**: Complete 3-dimensional variable control (Mode: get/set, Scope: flow/global, Environment: current/all/dev/qa/prd).
- **Backward Compatibility**: Fully backward compatible; defaults to `"current"`, matching the active flow environment.
