# Specification: Backend Core & Decoupled Execution Engine

## 1. User Stories
- **US-1**: As an automation builder, I want to query the backend component catalog via API, so that I receive self-describing component metadata to dynamically construct UI forms and ports without frontend changes.
- **US-2**: As an automation builder, I want to submit a workflow JSON (nodes and edges) for validation, so that cycles and missing dependencies are caught before execution.
- **US-3**: As an automation builder, I want to execute a flow asynchronously, so that outputs of upstream nodes are automatically piped into inputs of downstream nodes.

## 2. Business Rules & Invariants
- **BR-1**: Workflows must form a valid Directed Acyclic Graph (DAG). Any graph containing cycles must be rejected with `CyclicGraphError`.
- **BR-2**: The Component Registry must serialize all parameters with complete type descriptors (`type`, `label`, `required`, `default`, `is_handle`).
- **BR-3**: Execution of independent branches must proceed concurrently without blocking other execution branches.
- **BR-4**: When an edge connects an upstream output to a downstream input, the upstream runtime output value overrides any static default input value.
- **BR-5**: Any node execution failure must halt downstream dependent nodes while recording a failure record in the execution telemetry.

## 3. Acceptance Criteria (BDD)

### Happy Path (Success Scenarios)
- **AC-1: Component Catalog Serialization**
  - **Given** registered components (`ManualTrigger`, `HttpRequest`, `PythonScript`, `JsonTransform`)
  - **When** `GET /api/v1/components` is requested
  - **Then** the response status is 200 and returns a JSON list of component definitions with all input fields, types, and outputs.

- **AC-2: Linear DAG Execution with Data Passing**
  - **Given** a 2-node flow connecting `ManualTrigger` output to `JsonTransform` input
  - **When** `POST /api/v1/flows/execute` is called with the flow payload
  - **Then** status is 200, execution status is `completed`, and the transform node receives and processes the trigger's output.

### Input & Validation Scenarios
- **AC-3: Cycle Detection Rejection**
  - **Given** a workflow with nodes A, B, and C where A -> B -> C -> A
  - **When** `POST /api/v1/flows/validate` is called
  - **Then** validation fails with status 422/400 indicating cycle detection error.

- **AC-4: Missing Required Input Validation**
  - **Given** a node requiring an input that is neither provided statically nor connected via edge
  - **When** validation or execution is attempted
  - **Then** the engine raises a validation error detailing the missing input.

### Edge Cases & Exceptions (Resilience)
- **AC-5: Node Execution Error Isolation**
  - **Given** a node in a branch that raises an exception during execution
  - **When** the flow is executed
  - **Then** the failed node is marked as `failed`, the error message is captured, and downstream nodes are not executed.

## 4. Test Data & Boundary Matrix
| Parameter / Field | Valid Inputs (Happy) | Invalid / Boundary Inputs (Edge) |
|---|---|---|
| `flow.nodes` | `[{"id": "n1", "type": "ManualTrigger"}, {"id": "n2", "type": "JsonTransform"}]` | `[]`, duplicate IDs, unregistered types |
| `flow.edges` | `[{"source": "n1", "sourceHandle": "data", "target": "n2", "targetHandle": "input_data"}]` | Self-loops, dangling source/target IDs |
| `PythonScript.code` | `"def run(inputs):\n    return {'result': inputs['val'] * 2}"` | Syntax error, empty string, infinite while loop |

## 5. Verification Sensors
| Sensor | Command / Target | Success Threshold |
|---|---|---|
| Linter | `uv run ruff check backend/` | 0 errors |
| Test Suite | `uv run pytest backend/tests/ -v` | 100% pass |
| SDD Integrity | `node .agents/scripts/verify-sdd-integrity.js` | 100% pass |

## 6. UI & Design System Tokens
- N/A for this backend milestone.
