# Specification: Loop Iterator Component (ADR 0030)

## 1. User Stories
- **US-1**: As a workflow creator, I want to divide an array of records into chunks of size N, so that I can send manageable batches to downstream external APIs without hitting rate limits.
- **US-2**: As an automation builder, I want to retrieve a specific batch by index (`batch_index`) and know whether more batches remain (`has_more`), so that I can implement cursor-based pagination or incremental workflows.
- **US-3**: As a developer, I want to extract nested collections using dot-notation (`items_path`), so that I don't need intermediate nodes to unpack API payloads.

## 2. Business Rules & Invariants
- **BR-1**: Collection extraction:
  - If `items` is a list, it is used directly.
  - If `items` is a dict and `items_path` is specified, traverses the dot-notation path to find the target list.
  - If `items` is a dict without `items_path`, inspects common keys (`"items"`, `"results"`, `"data"`, `"rows"`), falling back to `[items]`.
  - Empty or invalid collection produces `total_items = 0`, `total_batches = 0`, `current_batch = []`, `batches = []`, `has_more = False`.
- **BR-2**: Batching logic:
  - `batch_size` is enforced to be an integer >= 1 (defaults to 10).
  - Total batches `total_batches = ceil(total_items / batch_size)`.
  - If `max_batches > 0`, caps `total_batches` to `min(total_batches, max_batches)`.
- **BR-3**: Batch pagination:
  - `current_batch` is the sub-list at `batches[batch_index]` if `0 <= batch_index < total_batches`, else `[]`.
  - `has_more` is `True` if `batch_index < total_batches - 1`, else `False`.
  - `batch_info` dictionary contains:
    `{"batch_index": int, "batch_size": int, "batch_items_count": int, "start_index": int, "end_index": int, "has_more": bool}`.

## 3. Acceptance Criteria (BDD)

### Happy Path (Success Scenarios)
- **AC-1: Chunk Array into Equal Batches**
  - **Given** an array of 5 items `[1, 2, 3, 4, 5]` and `batch_size = 2`
  - **When** the component executes with `batch_index = 0`
  - **Then** `total_items == 5`, `total_batches == 3`, `current_batch == [1, 2]`, `has_more == True`, and `batches == [[1, 2], [3, 4], [5]]`.

- **AC-2: Access Subsequent Batch Index**
  - **Given** the same array and `batch_size = 2`, with `batch_index = 2`
  - **When** the component executes
  - **Then** `current_batch == [5]`, `has_more == False`.

- **AC-3: Extract Collection via Items Path**
  - **Given** nested payload `{"response": {"records": [{"id": 1}, {"id": 2}]}}` and `items_path = "response.records"`
  - **When** the component executes with `batch_size = 10`
  - **Then** `total_items == 2`, `current_batch == [{"id": 1}, {"id": 2}]`.

- **AC-4: Cap Batches with Max Batches**
  - **Given** 100 items with `batch_size = 10` and `max_batches = 3`
  - **When** the component executes
  - **Then** `total_batches == 3`, `len(batches) == 3`.

### Edge Cases & Exceptions (Resilience)
- **AC-5: Out-of-Range Batch Index**
  - **Given** collection of 3 items with `batch_size = 5` and `batch_index = 99`
  - **When** the component executes
  - **Then** `current_batch == []`, `has_more == False` without raising exceptions.

- **AC-6: Zero or Negative Batch Size**
  - **Given** `batch_size = 0` or `-5`
  - **When** the component executes
  - **Then** it automatically clamps `batch_size` to 1 and processes correctly without division-by-zero errors.

## 4. Test Data & Boundary Matrix
| Parameter / Field | Valid Inputs (Happy) | Invalid / Boundary Inputs (Edge) |
|---|---|---|
| `items` | `[1, 2, 3]`, `{"data": [...]}` | `[]`, `None`, `"string"` |
| `items_path` | `"data.items"`, `""` | non-existent path |
| `batch_size` | `10`, `50`, `1` | `0`, `-1`, `"invalid"` |
| `batch_index` | `0`, `1`, `2` | `-1`, `9999` |
| `max_batches` | `0`, `5` | `-1` |

## 5. Verification Sensors
| Sensor | Command / Target | Success Threshold |
|---|---|---|
| Pytest Unit & Integration | `backend/.venv/Scripts/pytest backend/tests/test_loop_iterator.py` | 100% pass (6+ tests) |
| Full Pytest Suite | `backend/.venv/Scripts/pytest backend/tests/` | 100% pass (151+ tests) |
| Vitest Frontend Suite | `npx vitest run tests/loop_iterator.test.ts` | 100% pass (4+ tests) |
| Frontend Typecheck & Build | `npm run build` | Clean exit 0 |
| Pre-Commit Spec Drift Sensor | `node .agents/scripts/check-spec-drift.js` | 0 drift detected |
| SDD Integrity Sensor | `node .agents/scripts/verify-sdd-integrity.js` | 100% integrity |
