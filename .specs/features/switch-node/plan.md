# Feature Plan: Switch / Router Node Component (ADR 0018)

## 1. Executive Summary
Provide multi-way conditional routing in FlowBuild by introducing `SwitchNodeComponent` ("Switch / Router") in the "Logic" category. The node evaluates incoming data against configured case values (`case_1`, `case_2`, `case_3`, and `default_branch`) and routes the payload only to the matching branch while cascading skips to inactive downstream branches.

## 2. Architecture & Design Alignment
- **Component**: `SwitchNodeComponent` in `backend/src/backend/app/components/builtins/logic.py`.
- **Inputs**:
  - `input_data`: `DictInput(name="input_data", label="Incoming Data", default={})`
  - `expression`: `StrInput(name="expression", label="Switch Expression", default="data.get('status')", required=True)`
  - `case_1_value`: `StrInput(name="case_1_value", label="Case 1 Value", default="case_1")`
  - `case_2_value`: `StrInput(name="case_2_value", label="Case 2 Value", default="case_2")`
  - `case_3_value`: `StrInput(name="case_3_value", label="Case 3 Value", default="case_3")`
- **Outputs**:
  - `case_1`: Emits `data` if matched, else `None`.
  - `case_2`: Emits `data` if matched, else `None`.
  - `case_3`: Emits `data` if matched, else `None`.
  - `default_branch`: Emits `data` if no cases matched, else `None`.
  - `matched_case`: Returns the matched case string (`"case_1"`, `"case_2"`, `"case_3"`, or `"default_branch"`).
  - `evaluated_value`: Returns evaluated expression value.
- **Engine Extension**:
  - Update `FlowRunner.execute_stream` in `backend/src/backend/app/engine/runner.py` to recognize switch branch handles (`case_1`, `case_2`, `case_3`, `default_branch`) alongside `true_branch` and `false_branch`, cascading skips to downstream nodes of unselected handles.
- **Frontend Integration**:
  - Update `ComponentPalette.vue` and `CustomNode.vue` with `GitFork` icon and Indigo badges.

## 3. Risks & Non-Regression
- Zero disruption to `IfConditionComponent` or existing conditional branch test suites.
- Downstream nodes connected to inactive branches must be marked `skipped` and not fail the flow.
