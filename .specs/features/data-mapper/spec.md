# Specification: Data Mapper Component (ADR 0025)

## 1. User Stories
- **US-1**: As an automation developer, I want to map fields from an incoming JSON object into a new structure using dot-notation paths, so that downstream nodes receive cleaned data in the expected schema.
- **US-2**: As a data engineer, I want to transform an array of records using the same mapping schema, so that batch data from APIs or databases is uniformly reshaped.
- **US-3**: As a workflow creator, I want an option to pass through unmapped fields, so that I can rename specific keys while retaining the rest of the original object.

## 2. Business Rules & Invariants
- **BR-1**: `mapping` is a dictionary where each key represents the output property name and the value represents a dot-separated path in the source item (e.g. `{"user_name": "data.profile.fullName"}`).
- **BR-2**: Path resolution must handle dictionaries and zero-based numerical list indexing (e.g. `"tags.0"`).
- **BR-3**: If a path cannot be resolved or is `None`, the output key is set to `None` without raising an exception.
- **BR-4**: If `pass_unmapped` is True, all top-level keys from the source object that are not overridden by `mapping` are preserved in the output object.
- **BR-5**: If `items_path` is specified, the component first resolves that path to extract the collection, then transforms each element within that collection.
- **BR-6**: `mapped_count` reports the number of records transformed (1 for a single object, or `len(items)` for an array).

## 3. Acceptance Criteria (BDD)

### Happy Path (Success Scenarios)
- **AC-1: Single Object Nested Path Mapping**
  - **Given** input `{"user": {"id": 42, "profile": {"name": "Alice"}}}` and mapping `{"userId": "user.id", "userName": "user.profile.name"}`
  - **When** the node executes
  - **Then** `output_data` is `{"userId": 42, "userName": "Alice"}` and `mapped_count` is 1.

- **AC-2: Array of Objects Mapping with Items Path**
  - **Given** input `{"data": {"items": [{"sku": "A1", "price": 10}, {"sku": "B2", "price": 25}]}}`, `items_path="data.items"`, and mapping `{"product_code": "sku", "cost": "price"}`
  - **When** the node executes
  - **Then** `output_data` is `[{"product_code": "A1", "cost": 10}, {"product_code": "B2", "cost": 25}]` and `mapped_count` is 2.

- **AC-3: Pass Unmapped Fields**
  - **Given** input `{"id": 1, "extra": "keep_me", "old_key": "val"}` with mapping `{"new_key": "old_key"}` and `pass_unmapped=True`
  - **When** the node executes
  - **Then** `output_data` is `{"id": 1, "extra": "keep_me", "old_key": "val", "new_key": "val"}`.

### Edge Cases & Exceptions (Resilience)
- **AC-4: Missing / Null Source Fields**
  - **Given** mapping `{"missing": "user.non_existent.key"}`
  - **When** the node executes against `{"user": {}}`
  - **Then** `output_data["missing"]` is `None` without raising exceptions.

- **AC-5: Empty or Invalid Input Data**
  - **Given** empty input `{}` or `None`
  - **When** the component executes
  - **Then** `output_data` is `{}` and `mapped_count` is 0.

## 4. Test Data & Boundary Matrix
| Parameter / Field | Valid Inputs (Happy) | Invalid / Boundary Inputs (Edge) |
|---|---|---|
| `input_data` | `{"a": 1}`, `[{"a": 1}]`, `{"items": [...]}` | `{}`, `None`, `[]` |
| `mapping` | `{"x": "a.b"}`, `{"code": "items.0.sku"}` | `{}` |
| `items_path` | `""`, `"items"`, `"response.records"` | `"invalid.non_existent"` |
| `pass_unmapped` | `True`, `False` | `None` |
| `mode` | `"auto"`, `"single"`, `"array"` | `""` (defaults to `"auto"`) |

## 5. Verification Sensors
| Sensor | Command / Target | Success Threshold |
|---|---|---|
| Backend Test Suite | `uv run pytest backend/tests/test_data_mapper.py` | 100% pass |
| Frontend Test Suite | `npx vitest run frontend/tests/data_mapper.test.ts` | 100% pass |
| Full Vitest Suite | `npx vitest run` | 100% pass |
| Frontend Build | `npm run build` in `frontend/` | Exit 0, 0 type errors |
| Backend Pytest Suite | `uv run pytest` in `backend/` | 100% pass |
