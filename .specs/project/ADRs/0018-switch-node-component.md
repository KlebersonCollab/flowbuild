# ADR 0018: Multi-Branch Switch Routing Component and Generalized Branch Skipping

## Status
Accepted

## Date
2026-10-07

## Context
In ADR 0009, FlowBuild introduced conditional branch skipping for binary IF conditions (`true_branch` and `false_branch`).
However, real-world workflows often require multi-way routing based on status codes, event types, or category labels (e.g. `payment_success`, `payment_pending`, `payment_failed`, or fallback).
Using multiple nested IF nodes is cumbersome, clutters the canvas, and increases workflow maintenance overhead.

## Decision
1. **Component Design (`SwitchNodeComponent`)**:
   - Class name: `SwitchNodeComponent`
   - Display name: `"Switch / Router"`
   - Category: `"Logic"`
   - Description: `"Routes incoming data to one of multiple branches (case_1, case_2, case_3, or default) based on value or expression evaluation."`
   - Icon: `"git-fork"` (or `"split"`)
2. **Inputs**:
   - `input_data` (`BaseInput` / `DictInput`): Incoming payload to route.
   - `expression` (`StrInput`): Python expression or key lookup evaluated against `data` (e.g. `data.get('status')`).
   - `case_1_value` (`StrInput`): Value to match against evaluated expression (default: `"case_1"`).
   - `case_2_value` (`StrInput`): Value to match against evaluated expression (default: `"case_2"`).
   - `case_3_value` (`StrInput`): Value to match against evaluated expression (default: `"case_3"`).
3. **Outputs & Handles**:
   - `case_1`: Emits `input_data` if expression matches `case_1_value`, else `None`.
   - `case_2`: Emits `input_data` if expression matches `case_2_value`, else `None`.
   - `case_3`: Emits `input_data` if expression matches `case_3_value`, else `None`.
   - `default_branch`: Emits `input_data` if none of the cases match, else `None`.
   - `matched_case`: Returns the matched branch name (`"case_1"`, `"case_2"`, `"case_3"`, or `"default_branch"`).
   - `evaluated_value`: Returns the evaluated value.
4. **Generalization of Branch Skipping in `FlowRunner`**:
   - Expand `FlowRunner` conditional handle detection to include `case_1`, `case_2`, `case_3`, `default_branch` (and generic conditional output handles returning `None`).
   - Downstream branches connected to unmatched handles are skipped cleanly without failing the flow.
5. **Frontend Canvas & Node Display**:
   - Map `SwitchNodeComponent` with `GitFork` / `Split` icon and Indigo/Violet accent styling (`text-indigo-400 bg-indigo-500/10 border-indigo-500/30`).
   - Render handles with descriptive labels and distinct port colors.

## Consequences
- **Positive**: Clean multi-way branching without cumbersome chains of nested IF nodes.
- **Backwards Compatibility**: 100% backward compatible with existing binary `IfConditionComponent`.
