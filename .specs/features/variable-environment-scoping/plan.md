# Feature Plan: Variable Environment Scoping & Selection (ADR 0015)

## 1. Executive Summary
Provide complete 3-dimensional variable control in `VariableComponent` by introducing an explicit `environment` selector (`"current"`, `"all"`, `"dev"`, `"qa"`, `"prd"`). This allows workflows to save or retrieve variables scoped to the current flow environment, across all environments, or specifically to DEV, QA, or PRD.

## 2. Architecture & Design Alignment
- **Component**: `VariableComponent` in `backend/src/backend/app/components/builtins/variables.py`.
- **Inputs Added**:
  - `SelectInput(name="environment", label="Environment", options=["current", "all", "dev", "qa", "prd"], default="current")`.
- **Target Environment Resolution**:
  - When `environment == "current"`: dynamically resolves to `_environment` passed by `FlowRunner` (defaults to `"dev"`).
  - When `environment in ("all", "dev", "qa", "prd")`: targets that specific environment in `upsert_variable` and `resolve_variable_value`.
- **Database**: Reuses `db_manager.upsert_variable` and `db_manager.resolve_variable_value` with exact environment filtering.

## 3. Risks & Non-Regression
- Must preserve 100% backward compatibility: default `"current"` behaves identically to existing flow environment propagation.
- Existing tests and flows without explicit `environment` input continue executing without errors.
