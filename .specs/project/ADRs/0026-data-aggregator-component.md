# ADR 0026: Data Aggregator Component for Collection Metrics & Grouping

## Status
Accepted

## Date
2026-10-07

## Context
Automation flows often process collections of items—such as order rows, invoice line items, metrics reports, or user lists—and need to compute statistical summaries before passing data downstream.

Typical operations include:
1. Calculating totals (`sum`), averages (`avg`), extrema (`min`, `max`), and cardinalities (`count`, `distinct`).
2. Grouping collections by category or status (`group_by: "category"`).
3. Concatenating string fields into formatted summaries (`concat` with customizable delimiter).

Previously, users had to write custom loops in `PythonScriptComponent` to calculate basic sums or averages.

A native `DataAggregatorComponent` simplifies collection metrics into a declarative, robust node on the FlowBuild canvas.

## Decision
1. **Component Design (`DataAggregatorComponent`)**:
   - Class name: `DataAggregatorComponent`
   - Display name: `"Data Aggregator"`
   - Category: `"Transform"`
   - Description: `"Calculates mathematical and statistical aggregations (sum, avg, min, max, count, concat, group_by) on collections."`
   - Icon: `"calculator"`
2. **Inputs**:
   - `items` (`DictInput` / `BaseInput`, required=True, default=[]): List of records or object containing a collection.
   - `items_path` (`StrInput`, default=""): Optional dot path to extract items list (e.g. `"data.orders"`).
   - `field` (`StrInput`, default=""): Dot-notation path to the target property to aggregate (e.g. `"price"`, `"amount"`).
   - `operation` (`SelectInput`, options=`["all", "sum", "avg", "min", "max", "count", "concat"]`, default=`"all"`): Main aggregation calculation.
   - `group_by` (`StrInput`, default=""): Optional field to partition and group aggregations by.
   - `delimiter` (`StrInput`, default=", "): Separator for `"concat"` operations.
3. **Outputs**:
   - `result` (`Output`, type="any"): The primary calculated metric (or grouped dictionary).
   - `summary` (`Output`, type="dict"): Comprehensive metrics dictionary (`{"count": ..., "sum": ..., "avg": ..., "min": ..., "max": ...}`).
   - `count` (`Output`, type="int"): Number of items aggregated.
4. **Execution Semantics & Resilience**:
   - Automatically coerces numeric strings to `float`/`int`, skipping `None` or non-numeric entries gracefully without runtime failure.
   - For empty collections, defaults `sum=0`, `avg=0`, `min=0`, `max=0`, `count=0`.
   - When `group_by` is configured, builds grouped sub-aggregates with count and metrics per key.
5. **Frontend Canvas & Palette Integration**:
   - Map `aggregator` in `ComponentPalette.vue` and `CustomNode.vue` to `Calculator` icon with Emerald Transform styling (`text-emerald-400 bg-emerald-500/10 border-emerald-500/30`).

## Consequences
- **Positive**: Direct zero-code mathematical and statistical aggregation of datasets.
- **Completeness**: Seamlessly combines with `PaginatedHttpComponent`, `DataFilterComponent`, and `DataMapperComponent` in automated ETL pipelines.
- **Safety**: Safe numeric coercion; zero crashes on missing or null values.
- **Backwards Compatibility**: 100% additive; no breaking changes.
