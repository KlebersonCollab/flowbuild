# Feature Spec: Switch / Router Node Component (ADR 0018)

## 1. User Stories & Acceptance Criteria

### US-01: Multi-Branch Routing
As a workflow author, I want to route execution to one of multiple branches based on an evaluated property or expression.
- **AC-01.1**: When `expression="data.get('status')"` and `data={"status": "paid"}`, if `case_1_value="paid"`, output `case_1` emits the input payload and `matched_case="case_1"`.
- **AC-01.2**: When `case_2_value="pending"`, output `case_2` emits the input payload if status is pending, while `case_1`, `case_3`, and `default_branch` are `None`.
- **AC-01.3**: When `case_3_value="cancelled"`, output `case_3` emits the input payload if status is cancelled.
- **AC-01.4**: When the evaluated value matches none of `case_1`, `case_2`, or `case_3`, output `default_branch` emits the input payload and `matched_case="default_branch"`.

### US-02: Cascading Branch Skipping in FlowRunner
As a workflow engine, I want nodes connected to unselected branches of a SwitchNode to be skipped cleanly without failing the flow execution.
- **AC-02.1**: A node connected to `case_1` executes when `case_1` matches.
- **AC-02.2**: A node connected to `case_2` is skipped (`status: "skipped"`, reason: `"condition_not_met"`) when `case_1` matches.
- **AC-02.3**: Downstream nodes connected to skipped nodes are also skipped recursively (`reason: "upstream_skipped"`).

### US-03: Frontend Palette & Canvas Display
As a frontend user, I want to find "Switch / Router" in the Logic palette and inspect its branch ports on the canvas.
- **AC-03.1**: `SwitchNodeComponent` appears under `Logic` with `GitFork` icon and Indigo badges.
- **AC-03.2**: Output handles for `case_1`, `case_2`, `case_3`, and `default_branch` are visually exposed for edge connections.
