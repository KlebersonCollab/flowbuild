# Specification: Data Aggregator Component (ADR 0026)

## 1. User Stories
- **US-1**: As a pipeline author, I want to calculate totals and averages on a collection of records without writing custom scripts, so that financial and operational calculations are straightforward.
- **US-2**: As an operations engineer, I want to group items by a category attribute and compute statistics per group, so that breakdowns can be analyzed.
- **US-3**: As a notification builder, I want to concatenate string values with a delimiter into a single text output, so that I can send a consolidated message listing all affected items.

## 2. Business Rules & Invariants
- **BR-1**: `items` can be passed directly as a list of dicts/scalars, or as an object with `items_path` specifying the dot path to the collection.
- **BR-2**: When `field` is provided, the value is extracted from each item using dot-notation traversal. If items are primitive numbers/strings, `field` can be omitted.
- **BR-3**: Non-numeric values in numeric operations (`sum`, `avg`, `min`, `max`) are skipped. If a value is a numeric string (e.g. `"42.5"`), it is coerced to float.
- **BR-4**: If `operation` is `"all"`, `result` returns the comprehensive `summary` dict: `{"count": N, "sum": S, "avg": A, "min": Min, "max": Max}`.
- **BR-5**: If `group_by` is specified, `result` returns a dict keyed by the group value, each containing sub-aggregates.
- **BR-6**: For empty inputs, returns `result = 0` (or `""` for concat), `count = 0`, and summary with zero values without throwing errors.

## 3. Acceptance Criteria (BDD)

### Happy Path (Success Scenarios)
- **AC-1: Sum and Avg Calculation on Record Field**
  - **Given** items `[{"price": 10}, {"price": 20}, {"price": 30}]` and `field="price"` with `operation="sum"`
  - **When** the node executes
  - **Then** output `result` is `60`, `count` is `3`, and `summary["avg"]` is `20.0`.

- **AC-2: Grouped Aggregations**
  - **Given** items `[{"category": "A", "val": 10}, {"category": "B", "val": 20}, {"category": "A", "val": 15}]`, `field="val"`, `group_by="category"`, and `operation="sum"`
  - **When** the node executes
  - **Then** output `result` contains `{"A": {"sum": 25, "count": 2}, "B": {"sum": 20, "count": 1}}`.

- **AC-3: String Concatenation with Delimiter**
  - **Given** items `[{"name": "Alice"}, {"name": "Bob"}, {"name": "Charlie"}]`, `field="name"`, `operation="concat"`, and `delimiter=" | "`
  - **When** the node executes
  - **Then** output `result` is `"Alice | Bob | Charlie"` and `count` is `3`.

### Edge Cases & Exceptions (Resilience)
- **AC-4: Empty Collection or Missing Path**
  - **Given** empty items `[]` or non-existent `items_path`
  - **When** the component executes
  - **Then** `count` is `0`, `result` is `0` (or empty summary), and no exceptions are raised.

- **AC-5: Mixed Non-Numeric Data**
  - **Given** items `[{"val": 10}, {"val": "invalid"}, {"val": None}, {"val": "20.5"}]` and `field="val"`, `operation="sum"`
  - **When** the node executes
  - **Then** only valid numbers (10 and 20.5) are included, yielding `sum=30.5`.

## 4. Test Data & Boundary Matrix
| Parameter / Field | Valid Inputs (Happy) | Invalid / Boundary Inputs (Edge) |
|---|---|---|
| `items` | `[{"price": 10}]`, `[1, 2, 3]`, `{"items": [...]}` | `[]`, `None`, `{}` |
| `field` | `"price"`, `"data.amount"`, `""` | `"missing.field"` |
| `operation` | `"all"`, `"sum"`, `"avg"`, `"min"`, `"max"`, `"count"`, `"concat"` | `""` (defaults to `"all"`) |
| `group_by` | `"category"`, `"status"`, `""` | `"missing_group"` |
| `delimiter` | `", "`, `" - "`, `"\n"` | `""` |

## 5. Verification Sensors
| Sensor | Command / Target | Success Threshold |
|---|---|---|
| Backend Test Suite | `uv run pytest backend/tests/test_data_aggregator.py` | 100% pass |
| Frontend Test Suite | `npx vitest run frontend/tests/data_aggregator.test.ts` | 100% pass |
| Full Vitest Suite | `npx vitest run` | 100% pass |
| Frontend Build | `npm run build` in `frontend/` | Exit 0, 0 type errors |
| Backend Pytest Suite | `uv run pytest` in `backend/` | 100% pass |
