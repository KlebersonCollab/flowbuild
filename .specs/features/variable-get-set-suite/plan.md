# Feature Plan: Variable Get/Set Mode Selection and Execution Persistence

## 1. Problem Statement
The current `VariableComponent` only supports reading variables. Workflows cannot dynamically capture values produced during execution (such as an auth token from an HTTP response, a counter, or an API result) and save them into a variable for downstream nodes or future executions.

## 2. Goals & Success Criteria
- Add `mode` input (`"get"` or `"set"`) to `VariableComponent`.
- In `"set"` mode, accept `variable_name`, `value`, `scope` (`"flow"` or `"global"`), and `persist` (default `True`).
- In `"set"` mode, return `value` in outputs to allow seamless pipeline chaining.
- Implement `upsert_variable` in `db_manager` to support database writing without duplicate key errors.
- In `FlowRunner`, propagate variables written during execution to downstream nodes and interpolation immediately.
- Preserve 100% backward compatibility with existing workflows using `VariableComponent`.
- 100% test pass rate across backend and frontend test suites.

## 3. Scope Boundaries
- **In Scope**:
  - `backend/src/backend/app/db.py`: `upsert_variable` implementation.
  - `backend/src/backend/app/components/builtins/variables.py`: `VariableComponent` enhancement with `mode`, `scope`, `persist`, `value`.
  - `backend/src/backend/app/engine/runner.py`: runtime propagation of set variables into `self.custom_variables`.
  - `backend/tests/test_variable_get_set.py`: comprehensive integration tests.
  - `frontend/tests/variables_get_set.test.ts`: frontend schema and flow tests.
- **Out of Scope**:
  - Encrypted asymmetric secret vaults (Milestone 4+).
