# Specification: Conditional Branch Skipping in DAG Runner

## Acceptance Criteria (BDD)

### Scenario 1: True branch executes, False branch is skipped
- **Given** a flow with a `ManualTriggerComponent` producing `{"amount": 150}`
- **And** an `IfConditionComponent` evaluating `data.get('amount') > 100` (evaluates True)
- **And** Node `VIP` connected to `true_branch`
- **And** Node `Standard` connected to `false_branch`
- **When** the workflow executes
- **Then** Node `VIP` executes successfully and produces a result
- **And** Node `Standard` is skipped with reason `"branch_inactive"`
- **And** the overall flow completes with status `"completed"`

### Scenario 2: False branch executes, True branch is skipped
- **Given** a flow with a `ManualTriggerComponent` producing `{"amount": 50}`
- **And** an `IfConditionComponent` evaluating `data.get('amount') > 100` (evaluates False)
- **And** Node `VIP` connected to `true_branch`
- **And** Node `Standard` connected to `false_branch`
- **When** the workflow executes
- **Then** Node `Standard` executes successfully and produces a result
- **And** Node `VIP` is skipped with reason `"branch_inactive"`
- **And** the overall flow completes with status `"completed"`

### Scenario 3: Cascaded skipping down the inactive branch
- **Given** an inactive branch node that is skipped
- **And** downstream nodes connected to that skipped node
- **When** the workflow reaches the downstream nodes
- **Then** all downstream nodes on that branch are cascaded as skipped with reason `"upstream_skipped"`

### Scenario 4: Pre-configured template in frontend
- **Given** the user selects the `"Decisão Condicional IF / Else"` template in the UI
- **When** loaded on the canvas
- **Then** it renders a working 4-node flow (`ManualTrigger -> IfCondition -> TrueAction / FalseAction`)
