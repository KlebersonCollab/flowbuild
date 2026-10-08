# Feature Spec: Data Filter Component (ADR 0019)

## 1. User Stories & Acceptance Criteria

### US-01: Declarative Comparison Operators
As a workflow author, I want to filter arrays of objects using standard comparison operators without writing code.
- **AC-01.1**: When `operator="equals"` and `value="active"`, items where `item[field] == "active"` are placed in `filtered_items`.
- **AC-01.2**: When `operator="not_equals"`, items differing from `value` are retained.
- **AC-01.3**: When `operator="greater_than"` and `value="100"`, items where `float(item[field]) > 100` are retained.
- **AC-01.4**: When `operator="less_than"` and `value="50"`, items where `float(item[field]) < 50` are retained.
- **AC-01.5**: When `operator="contains"` and `value="vip"`, items containing `"vip"` in `str(item[field])` or list are retained.
- **AC-01.6**: When `operator="is_empty"`, items where the field is `None`, `""`, or `[]` are retained.
- **AC-01.7**: When `operator="is_not_empty"`, items where the field has a non-empty value are retained.

### US-02: Collection Extraction & Telemetry
As a workflow author, I want to extract nested collections from payload dictionaries and inspect filter counts.
- **AC-02.1**: When `input_data={"results": [{"id": 1}, {"id": 2}]}` and `items_path="results"`, the component extracts and filters the nested list.
- **AC-02.2**: Output `count` equals `len(filtered_items)`.
- **AC-02.3**: Output `total_count` equals the number of items received before filtering.
- **AC-02.4**: Output `discarded_items` contains all non-matching items.

### US-03: Custom Expression Filtering
As an advanced workflow author, I want to use custom Python expressions for complex multi-field criteria.
- **AC-03.1**: When `operator="expression"` and `custom_expression="item.get('price', 0) > 20 and item.get('in_stock') is True"`, only items matching both conditions are retained.

### US-04: Frontend Visual Canvas & Dynamic Inspector
As a canvas builder user, I want to find "Data Filter" in the Transform category with a Filter icon.
- **AC-04.1**: `DataFilterComponent` appears in `ComponentPalette.vue` under category `Transform`.
- **AC-04.2**: `CustomNode.vue` displays the `Filter` icon with Emerald theme styling.
