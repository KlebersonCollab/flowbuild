# Specification: Try / Catch Error Boundary Component (ADR 0031)

## 1. User Stories
- **US-1**: As a workflow creator, I want to route data down a `success_branch` when an operation succeeds and down an `error_branch` when it fails, so that I can send alerts when failures happen without crashing the workflow.
- **US-2**: As an integration developer, I want to emit a `fallback_value` in `result` when an upstream node fails, so that subsequent steps can continue operating with default mock or cached values.
- **US-3**: As a system administrator, I want to inspect error details (`error_details`, `has_error`) so that logs and alerts clearly communicate the root cause.

## 2. Business Rules & Invariants
- **BR-1**: Success path:
  - When no error is present (and no upstream error was intercepted):
    - `success_branch = input_data`.
    - `error_branch = None` (triggering branch skipping for nodes connected to `error_branch`).
    - `result = input_data`.
    - `has_error = False`.
    - `error_details = ""`.
- **BR-2**: Error/Catch path:
  - When an error is caught from upstream or provided in `error_message`:
    - `success_branch = None` (triggering branch skipping for nodes connected to `success_branch`).
    - `error_branch = {"error": str(error_details), "fallback": fallback_value, "caught": True}`.
    - `result = fallback_value`.
    - `has_error = True`.
    - `error_details = str(error_details)`.
- **BR-3**: Engine Interception:
  - When an upstream node of `TryCatchComponent` fails and `catch_upstream_errors` is True:
    - `FlowRunner` does NOT mark `TryCatchComponent` as skipped.
    - `FlowRunner` injects `_upstream_error = error_string` into `TryCatchComponent` inputs.
    - `TryCatchComponent` executes successfully and emits the error branch output.
- **BR-4**: Branch skipping:
  - Edges originating from `success_branch` or `error_branch` with `None` values trigger conditional branch skipping downstream.

## 3. Acceptance Criteria (BDD)

### Happy Path (Success Scenarios)
- **AC-1: Successful Execution Routes to Success Branch**
  - **Given** `input_data = {"status": "ok", "user_id": 42}` and no error
  - **When** the component executes
  - **Then** `success_branch == {"status": "ok", "user_id": 42}`, `error_branch is None`, `result == {"status": "ok", "user_id": 42}`, `has_error == False`.

- **AC-2: Error Caught Routes to Error Branch and Emits Fallback**
  - **Given** an intercepted error `"Connection timeout to external API"` and `fallback_value = {"cached_rate": 5.25}`
  - **When** the component executes
  - **Then** `success_branch is None`, `error_branch["error"] == "Connection timeout to external API"`, `result == {"cached_rate": 5.25}`, `has_error == True`.

- **AC-3: Intercept Upstream Failure in FlowRunner**
  - **Given** a flow where Node 1 fails (e.g. invalid Python script or failing HTTP call) connected to Node 2 (`TryCatchComponent`)
  - **When** the flow executes
  - **Then** the flow does not fail; Node 2 catches the error and executes, emitting `result = fallback_value` with flow status `"completed"`.

- **AC-4: Branch Skipping Cascades Down Inactive Branch**
  - **Given** Node 2 (`TryCatchComponent`) with `success_branch` connected to Node 3 and `error_branch` connected to Node 4
  - **When** Node 1 succeeds
  - **Then** Node 3 runs and Node 4 is skipped (`reason: "condition_not_met"`).
  - **When** Node 1 fails
  - **Then** Node 3 is skipped (`reason: "condition_not_met"`) and Node 4 runs.

### Edge Cases & Exceptions (Resilience)
- **AC-5: Catch Upstream Errors Disabled**
  - **Given** `catch_upstream_errors = False` and an upstream node fails
  - **When** the flow executes
  - **Then** `TryCatchComponent` is skipped as an ordinary node due to upstream error.

## 4. Test Data & Boundary Matrix
| Parameter / Field | Valid Inputs (Happy) | Invalid / Boundary Inputs (Edge) |
|---|---|---|
| `input_data` | `{"data": 123}`, `"text"` | `{}` |
| `fallback_value` | `{"default": True}`, `[]` | `{}` |
| `catch_upstream_errors` | `True`, `False` | `None` |
| `error_message` | `""`, `"Failed: 500 error"` | `None` |

## 5. Verification Sensors
| Sensor | Command / Target | Success Threshold |
|---|---|---|
| Pytest Unit & Integration | `backend/.venv/Scripts/pytest backend/tests/test_try_catch.py` | 100% pass (6+ tests) |
| Full Pytest Suite | `backend/.venv/Scripts/pytest backend/tests/` | 100% pass (158+ tests) |
| Vitest Frontend Suite | `npx vitest run tests/try_catch.test.ts` | 100% pass (4+ tests) |
| Frontend Typecheck & Build | `npm run build` | Clean exit 0 |
| Pre-Commit Spec Drift Sensor | `node .agents/scripts/check-spec-drift.js` | 0 drift detected |
| SDD Integrity Sensor | `node .agents/scripts/verify-sdd-integrity.js` | 100% integrity |
