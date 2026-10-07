# Feature Specification: Variable Get/Set Mode Selection and Execution Persistence

## 1. VariableComponent Schema Specification
Component: `VariableComponent`
Category: `Variables`

### 1.1 Inputs

| Input Name | Type | Default | Required | Description |
|---|---|---|---|---|
| `mode` | SelectInput | `"get"` | Yes | Behavior mode: `"get"` (read) or `"set"` (write) |
| `variable_name` | StrInput | `""` | Yes | Name/key of the variable (e.g. `AUTH_TOKEN`, `API_KEY`) |
| `value` | StrInput / AnyInput | `""` | No | Data to assign when `mode == "set"`. Accepts upstream handles |
| `scope` | SelectInput | `"flow"` | No | Target scope when `mode == "set"`: `"flow"` or `"global"` |
| `persist` | BoolInput | `True` | No | Whether to persist in database for future executions |
| `default_value` | StrInput | `""` | No | Fallback value when `mode == "get"` and variable is not found |

### 1.2 Outputs

| Output Name | Type | Description |
|---|---|---|
| `value` | Any | The resolved value (in `get` mode) or the saved value (in `set` mode) |
| `variable_name` | String | Name of the variable accessed or written |
| `success` | Boolean | `True` on successful execution |

## 2. Behavioral Specifications

### 2.1 Mode: "get"
- Retrieves variable following the 4-tier hierarchy:
  1. Flow-scoped for environment
  2. Flow-scoped for 'all'
  3. Global for environment
  4. Global for 'all'
- If missing, returns `default_value`.
- Output: `{"value": resolved_value, "variable_name": var_name, "success": True}`.

### 2.2 Mode: "set"
- Extracts `var_name`, `value`, `scope` (`"flow"` or `"global"`), and `persist`.
- If `persist` is `True`:
  - Calls `db_manager.upsert_variable(key=var_name, value=str(value), scope=scope, flow_id=flow_id, environment=environment)`.
- Updates runner execution state so subsequent nodes and string interpolation `{{var_name}}` receive the new value immediately.
- Returns `{"value": value, "variable_name": var_name, "success": True}`.

## 3. Acceptance Criteria & Test Matrix
1. **Backward Compatibility**: Existing flows with `VariableComponent` execute in `get` mode without changes.
2. **Set and Propagate**: In a DAG: Node A (Set Variable `TOKEN="secret123"`) -> Node B (Get Variable `TOKEN` or HTTP Request with `{{TOKEN}}`) executes with `secret123`.
3. **Database Persistence**: Setting with `persist=True` creates or updates the variable in the database; subsequent independent flow runs can retrieve it.
4. **Scope Isolation**: Flow-scoped variable set in Flow 1 does not overwrite Flow 2 unless `scope="global"`.
