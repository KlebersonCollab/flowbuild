# ADR 0019: Declarative Data Filter Component for Collections and Records

## Status
Accepted

## Date
2026-10-07

## Context
In automation workflows, data frequently arrives from external APIs, webhooks, or database queries in the form of collections (arrays of objects or dicts). Workflow authors need to filter these records before sending notifications, saving to databases, or triggering downstream actions.

Previously in FlowBuild, users had to write custom Python scripts (`PythonScriptComponent`) using list comprehensions to perform simple item filtering, increasing workflow setup friction and requiring programming knowledge for straightforward operations.

## Decision
1. **Component Design (`DataFilterComponent`)**:
   - Class name: `DataFilterComponent`
   - Display name: `"Data Filter"`
   - Category: `"Transform"`
   - Description: `"Filters arrays of objects or data payloads declaratively based on field comparisons or expressions."`
   - Icon: `"filter"`
2. **Inputs**:
   - `input_data` (`BaseInput` / `DictInput`): Incoming list of items or dict payload containing items (default: `[]`).
   - `items_path` (`StrInput`): Optional JSON path/key to extract collection if `input_data` is a dictionary (e.g. `"items"` or `"users"`, default: `""`).
   - `field` (`StrInput`): Property/key name on each item to evaluate (e.g. `"status"`, `"price"`, `"active"`).
   - `operator` (`SelectInput`): Comparison rule:
     - Options: `["equals", "not_equals", "greater_than", "less_than", "greater_or_equal", "less_or_equal", "contains", "not_contains", "is_empty", "is_not_empty", "expression"]`
     - Default: `"equals"`
   - `value` (`StrInput`): Target value to compare against (e.g. `"active"`, `"100"`). Automatically attempts numeric/boolean coercion where applicable.
   - `custom_expression` (`StrInput`): Optional Python expression when operator is `"expression"` (e.g. `item.get('total', 0) > 100`).
3. **Outputs**:
   - `filtered_items` (`Output`): Array of items that satisfied the filter criteria.
   - `discarded_items` (`Output`): Array of items that did not satisfy the criteria.
   - `count` (`Output`): Total number of items kept (`int`).
   - `total_count` (`Output`): Total number of evaluated items (`int`).
4. **Frontend Palette & Node Theme**:
   - In `ComponentPalette.vue` and `CustomNode.vue`, map `filter` icon with Emerald tokens (`text-emerald-400 bg-emerald-500/10 border-emerald-500/30`), aligning with the Transform category styling.

## Consequences
- **Positive**: Declarative, visual data filtering without writing custom Python code.
- **Observability**: Exposes both `filtered_items` and `discarded_items`, allowing dual-branch workflows (e.g. process valid records, log discarded ones).
- **Backwards Compatibility**: 100% backward compatible; does not affect any existing action or transform nodes.
