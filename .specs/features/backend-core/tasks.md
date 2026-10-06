# Task List: Backend Core & Decoupled Execution Engine

## Sequence Guidelines (MetaGPT SOP)
- **Strict Sequential Order**: Tasks must be executed top-to-bottom without reordering or cherry-picking.
- **Atomic File Boundaries**: Each task must modify at most 1–3 specific target files.
- **Decoupled Test Setup**: Test definition / scaffolding tasks (`Type: test`) MUST precede implementation tasks (`Type: feat`).
- **Sensor Evidence Gate**: Mark complete `[x]` ONLY after passing build, lint, and test sensors with recorded evidence.

## Implementation Tasks

| Status | ID | Type | Description | Target Files | Dependencies | Evidence |
|---|---|---|---|---|---|---|
| [ ] | TASK-01 | test | Scaffold backend project with uv and initialize unit test harness | `backend/pyproject.toml`, `backend/tests/conftest.py` | None | |
| [ ] | TASK-02 | test | Define test suite for component descriptors, registry, and auto-discovery | `backend/tests/test_components.py` | TASK-01 | |
| [ ] | TASK-03 | feat | Implement Component base classes, typed Input hierarchy, and Output descriptors | `backend/app/components/base.py`, `backend/app/components/inputs.py`, `backend/app/components/outputs.py` | TASK-02 | |
| [ ] | TASK-04 | feat | Implement Component Registry with dynamic registration and JSON schema export | `backend/app/components/registry.py` | TASK-03 | |
| [ ] | TASK-05 | test | Define test suite for DAG topological sorting, cycle detection, and async execution runner | `backend/tests/test_dag_engine.py` | TASK-04 | |
| [ ] | TASK-06 | feat | Implement Flow domain models and DAG builder with topological sort and cycle validation | `backend/app/models/flow.py`, `backend/app/engine/dag_builder.py` | TASK-05 | |
| [ ] | TASK-07 | feat | Implement async DAG execution runner with state passing, error handling, and event streaming | `backend/app/engine/runner.py`, `backend/app/engine/context.py` | TASK-06 | |
| [ ] | TASK-08 | feat | Implement built-in automation components (ManualTrigger, HttpRequest, PythonScript, JsonTransform) | `backend/app/components/builtins/triggers.py`, `backend/app/components/builtins/actions.py` | TASK-07 | |
| [ ] | TASK-09 | test | Define integration test suite for FastAPI REST API endpoints | `backend/tests/test_api.py` | TASK-08 | |
| [ ] | TASK-10 | feat | Implement FastAPI application and route controllers for components, validation, and execution | `backend/app/main.py`, `backend/app/api/routes.py` | TASK-09 | |
| [ ] | TASK-11 | review | Audit all acceptance criteria, run ruff linter, pytest suite, and SDD integrity sensor | `backend/`, `.specs/` | TASK-10 | |

## Schema Dictionary
- **Status**: `[ ]` (Pending) | `[x]` (Verified Complete).
- **ID**: `TASK-01`, `TASK-02`, etc.
- **Type**: `test` | `feat` | `fix` | `refactor` | `docs` | `rules` | `skill` | `review`.
- **Target Files**: Concrete comma-separated file paths (relative to workspace root).
- **Dependencies**: Comma-separated list of preceding task IDs or `None`.
- **Evidence**: Commit hash (`git rev-parse --short HEAD`) + sensor output snippet.
