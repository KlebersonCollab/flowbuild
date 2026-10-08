# Specification: Key-Value Store Component (ADR 0029)

## 1. User Stories
- **US-1**: As a workflow creator, I want to store and retrieve state values by key across workflow executions, so that consecutive runs can remember previous context.
- **US-2**: As an automation builder, I want to atomically increment or decrement a counter, so that I can implement rate limits and sequence counters without race conditions.
- **US-3**: As a pipeline author, I want namespace isolation, so that distinct flows or modules don't accidentally overwrite each other's keys.

## 2. Business Rules & Invariants
- **BR-1**: In `operation = "set"`:
  - Stores `key` with provided `value` within specified `namespace`.
  - Preserves types: JSON objects/lists, numbers, booleans, and strings.
  - Returns `result = value`, `found = bool(previous_existed)`, and `previous_value`.
- **BR-2**: In `operation = "get"`:
  - If `key` exists in `namespace`, returns `result = stored_value`, `found = True`.
  - If `key` does not exist, returns `result = default_value`, `found = False`, `previous_value = None`.
- **BR-3**: In `operation = "delete"`:
  - Removes `key` in `namespace`.
  - Returns `result = True` if key was deleted, `False` if it was not found, `found = was_present`.
- **BR-4**: In `operation = "increment"`:
  - If `key` exists and holds a numeric value, adds `amount` to it.
  - If `key` does not exist, initializes value to `amount`.
  - Returns `result = new_number`, `previous_value = old_number`.
- **BR-5**: In `operation = "list"`:
  - Returns `result = list_of_matching_keys` matching `prefix` (or all keys in `namespace` if `key` is empty or wildcard).
  - Returns `found = len(result) > 0`.
- **BR-6**: Multi-tenant/Namespace Isolation:
  - Identical keys under different `namespace` values are completely independent.

## 3. Acceptance Criteria (BDD)

### Happy Path (Success Scenarios)
- **AC-1: Set and Get Structured JSON Value**
  - **Given** `operation = "set"`, `key = "user_pref"`, `value = {"theme": "dark", "lang": "pt"}`
  - **When** the component executes
  - **Then** `result == {"theme": "dark", "lang": "pt"}`. Subsequently running `get` returns the exact dictionary with `found == True`.

- **AC-2: Atomic Increment Counter**
  - **Given** `key = "api_hits"`, `operation = "increment"`, `amount = 1`
  - **When** the component executes twice
  - **Then** first execution returns `result == 1`, second execution returns `result == 2` with `previous_value == 1`.

- **AC-3: Fallback on Missing Key**
  - **Given** `key = "missing_key"`, `operation = "get"`, `default_value = "default_fallback"`
  - **When** the component executes
  - **Then** `result == "default_fallback"`, `found == False`.

- **AC-4: Namespace Separation**
  - **Given** `key = "status"` in `namespace = "ns1"` set to `"active"`, and in `namespace = "ns2"` set to `"paused"`
  - **When** getting `key = "status"` from `ns1`
  - **Then** `result == "active"`, and from `ns2` `result == "paused"`.

### Edge Cases & Exceptions (Resilience)
- **AC-5: Delete Non-Existent Key**
  - **Given** `operation = "delete"`, `key = "never_existed"`
  - **When** the component executes
  - **Then** `result == False`, `found == False`, without raising exceptions.

- **AC-6: Increment on Non-Numeric Value**
  - **Given** key previously stored as string `"not_a_number"`
  - **When** `operation = "increment"` is invoked
  - **Then** it safely resets or coerces to `amount` or raises a clean descriptive ValueError.

## 4. Test Data & Boundary Matrix
| Parameter / Field | Valid Inputs (Happy) | Invalid / Boundary Inputs (Edge) |
|---|---|---|
| `operation` | `"get"`, `"set"`, `"delete"`, `"increment"`, `"list"` | invalid string (defaults to `"get"`) |
| `key` | `"app.counter"`, `"user_123"` | `""`, special characters |
| `value` | `{"a": 1}`, `[1, 2]`, `42`, `"text"` | `None`, `""` |
| `namespace` | `"default"`, `"billing"` | `""` (defaults to `"default"`) |
| `amount` | `1`, `-5`, `10` | `0` |

## 5. Verification Sensors
| Sensor | Command / Target | Success Threshold |
|---|---|---|
| Pytest Unit & Integration | `backend/.venv/Scripts/pytest backend/tests/test_key_value_store.py` | 100% pass (6+ tests) |
| Full Pytest Suite | `backend/.venv/Scripts/pytest backend/tests/` | 100% pass (145+ tests) |
| Vitest Frontend Suite | `npx vitest run tests/key_value_store.test.ts` | 100% pass (4+ tests) |
| Frontend Typecheck & Build | `npm run build` | Clean exit 0 |
| Pre-Commit Spec Drift Sensor | `node .agents/scripts/check-spec-drift.js` | 0 drift detected |
| SDD Integrity Sensor | `node .agents/scripts/verify-sdd-integrity.js` | 100% integrity |
