# Feature Plan: Data Filter Component (ADR 0019)

## 1. Executive Summary
Introduce `DataFilterComponent` ("Data Filter") in the "Transform" category of FlowBuild. This node enables workflows to filter collections of objects or individual payloads declaratively using common comparison operators (`equals`, `contains`, `greater_than`, etc.) or custom expressions, outputting both `filtered_items` and `discarded_items` alongside item counts.

## 2. Architecture & Design Alignment
- **Component**: `DataFilterComponent` in `backend/src/backend/app/components/builtins/actions.py`.
- **Inputs**:
  - `input_data`: `BaseInput(name="input_data", label="Incoming Collection", default=[])`
  - `items_path`: `StrInput(name="items_path", label="Items Key / Path", default="", placeholder="e.g. items or results")`
  - `field`: `StrInput(name="field", label="Field Name", default="status", placeholder="e.g. status or price")`
  - `operator`: `SelectInput(name="operator", label="Comparison Operator", options=["equals", "not_equals", "greater_than", "less_than", "greater_or_equal", "less_or_equal", "contains", "not_contains", "is_empty", "is_not_empty", "expression"], default="equals")`
  - `value`: `StrInput(name="value", label="Comparison Value", default="active", placeholder="Target value")`
  - `custom_expression`: `StrInput(name="custom_expression", label="Custom Expression", default="item.get('status') == 'active'", placeholder="e.g. item.get('price', 0) > 50")`
- **Outputs**:
  - `filtered_items`: Array of matching items.
  - `discarded_items`: Array of non-matching items.
  - `count`: Number of matching items (`int`).
  - `total_count`: Total number of input items evaluated (`int`).
- **Frontend Integration**:
  - Mapped with `Filter` icon and Emerald Transform styling in `ComponentPalette.vue` and `CustomNode.vue`.

## 3. Risks & Non-Regression
- Robust type coercion for numbers and booleans when comparing against string input values.
- Gracefully handles non-list inputs (e.g. wraps single dict item or extracts from `items_path`).
- 100% backward compatible with existing components.
