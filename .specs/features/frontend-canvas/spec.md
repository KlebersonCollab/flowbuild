# Specification: Frontend Canvas & Dynamic Visual Builder

## 1. User Stories
- **US-1**: As an automation builder, I want to view available automation components grouped by category in a sidebar palette, so that I can add nodes to the canvas.
- **US-2**: As an automation builder, I want to connect output ports of one node to input ports of another node on the canvas, so that data flows between them.
- **US-3**: As an automation builder, I want to select a node and configure its properties in a dynamic inspector panel, so that I can set URLs, parameters, expressions, or scripts without manual UI coding.
- **US-4**: As an automation builder, I want to click "Run Flow" and watch real-time execution feedback (active spinner, green success, red failure) on each node via SSE streaming.

## 2. Business Rules & Invariants
- **BR-1**: The UI must strictly adhere to [DESIGN.md](file:///F:/Projetos/flowbuild/DESIGN.md) (Canvas `#010102`, surface-1 `#0f1011`, surface-2 `#141516`, hairline `#23252a`, primary lavender `#5e6ad2`, text ink `#f7f8f8`).
- **BR-2**: The frontend must never hardcode node configurations. All inputs, controls, and port handles must be dynamically generated from the backend's JSON schema catalog.
- **BR-3**: Every node on the canvas must visually display its execution state (`idle`, `running`, `completed`, `failed`).
- **BR-4**: When saving or running, the canvas graph must serialize to standard FlowModel JSON (`id`, `name`, `nodes`, `edges`).

## 3. Acceptance Criteria (BDD)

### Happy Path (Success Scenarios)
- **AC-1: Dynamic Form Generation**
  - **Given** a component definition with input types `str`, `select`, `int`, `dict`, and `code`
  - **When** the node is selected on the canvas
  - **Then** the inspector panel renders text inputs, select dropdowns, number inputs, key-value editors, and code areas corresponding to each schema field.

- **AC-2: Canvas Graph Serialization**
  - **Given** nodes and edges placed and connected on the canvas
  - **When** the user clicks "Run Flow" or triggers serialization
  - **Then** `useFlowStore.toFlowPayload()` outputs a valid `FlowModel` matching backend schema.

- **AC-3: Real-Time SSE Execution Telemetry**
  - **Given** a flow submitted for execution
  - **When** SSE events (`node_started`, `node_completed`, `node_failed`) arrive
  - **Then** `useExecutionStore` updates node states reactively, triggering visual border highlights and status badges.

### Input & Validation Scenarios
- **AC-4: Invalid Edge Connection Rejection**
  - **Given** two handles on the canvas
  - **When** a user tries to connect an output handle to another output handle (or input to input)
  - **Then** the canvas prevents or invalidates the connection.

### Edge Cases & Exceptions (Resilience)
- **AC-5: Backend Offline Fallback**
  - **Given** the backend API is unreachable
  - **When** the frontend loads
  - **Then** the UI shows a graceful offline warning badge while keeping local canvas editing functional.

## 4. Test Data & Boundary Matrix
| Parameter / Field | Valid Inputs (Happy) | Invalid / Boundary Inputs (Edge) |
|---|---|---|
| `node.data.inputs` | `{"url": "https://api...", "method": "POST"}` | Empty object, missing required keys |
| `edge.sourceHandle` | Valid output handle name (e.g. `"data"`) | Null, undefined, nonexistent handle |
| `SSE Event` | `{"event": "node_completed", "node_id": "n1"}` | Corrupted JSON, unexpected event type |

## 5. Verification Sensors
| Sensor | Command / Target | Success Threshold |
|---|---|---|
| TypeScript Typecheck | `npm run type-check` in `frontend/` | 0 errors |
| Test Suite | `npm run test` in `frontend/` | 100% pass |
| Build | `npm run build` in `frontend/` | Exit 0 |
| SDD Integrity | `node .agents/scripts/verify-sdd-integrity.js` | 100% pass |

## 6. UI & Design System Tokens (DESIGN.md)
- **Colors**: Canvas `{colors.canvas}` `#010102`, Surface 1 `{colors.surface-1}` `#0f1011`, Surface 2 `{colors.surface-2}` `#141516`, Hairline `{colors.hairline}` `#23252a`, Primary `{colors.primary}` `#5e6ad2`, Ink `{colors.ink}` `#f7f8f8`, Ink-muted `{colors.ink-muted}` `#d0d6e0`.
- **Components**: `button-primary` (8px 14px, rounded-md, bg `#5e6ad2`), `feature-card` (surface-1, hairline border, rounded-lg).
