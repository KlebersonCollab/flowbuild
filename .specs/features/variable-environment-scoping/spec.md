# Feature Spec: Variable Environment Scoping & Selection (ADR 0015)

## 1. User Stories & Acceptance Criteria

### US-01: Explicit Environment Selection in Set Mode
As a workflow author, I want to configure whether a variable is saved to the current flow environment (`current`), all environments (`all`), or a specific stage (`dev`, `qa`, `prd`).
- **AC-01.1**: When `environment="current"` and `_environment="qa"`, `VariableComponent` in `mode="set"` persists the variable to QA.
- **AC-01.2**: When `environment="all"`, `VariableComponent` persists the variable with `environment="all"`, accessible across all stages.
- **AC-01.3**: When `environment="prd"`, `VariableComponent` explicitly persists to PRD even if the active flow is in DEV.

### US-02: Target Environment Resolution in Get Mode
As a workflow author, I want `VariableComponent` in `mode="get"` to resolve variables according to the selected environment.
- **AC-02.1**: When `environment="current"`, resolves using the active flow environment via the 4-tier hierarchy.
- **AC-02.2**: When `environment` is explicit (`dev`, `qa`, `prd`, `all`), queries with that target environment.

### US-03: Frontend Component Schema & Inspector Display
As a frontend user, I want to see and adjust the `environment` dropdown in the Node Inspector.
- **AC-03.1**: The `VariableComponent` schema includes the `environment` input with options `["current", "all", "dev", "qa", "prd"]`.
- **AC-03.2**: Serialized flow JSON includes the configured `environment` value under node inputs.
