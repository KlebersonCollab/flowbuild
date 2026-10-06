# Technical Concerns, Risks & Fragile Areas (FlowBuild)

## 1. Critical Risks & Security Considerations

### A. Python Code Sandboxing (High Risk)
- **Problem**: Automation platforms often provide a `PythonScript` node allowing users to write custom Python logic. Executing arbitrary Python code without restrictions allows remote code execution (RCE), filesystem tampering, and infinite loops.
- **Mitigation Strategy**:
  - Phase 1: Local / trusted execution with restricted globals and ast parsing (blocking `os.system`, `subprocess`, `open`, `__import__`).
  - Phase 2: Isolated worker containerization (Docker container or WebAssembly/Pyodide sandbox).

### B. Graph Cycles & Deadlocks (Medium Risk)
- **Problem**: Cyclic edges in workflows can cause deadlocks, stack overflows, or infinite execution loops if not caught prior to execution.
- **Mitigation Strategy**:
  - Run topological cycle detection (Tarjan's or Kahn's algorithm) before flow compilation.
  - Reject cyclic graphs unless explicitly wrapped in a controlled `LoopIterator` construct with a hard iteration ceiling (e.g. max 1,000 iterations).

### C. State Serialization & Memory Pressure (Medium Risk)
- **Problem**: Automations transferring huge payloads (e.g. multi-megabyte JSON responses, base64 images, file uploads) between nodes can exhaust backend process memory or overwhelm SSE streaming.
- **Mitigation Strategy**:
  - Store large payloads on disk or object storage with reference tokens (e.g. `file_ref://...`) rather than inlining large raw binary buffers in the memory state.
  - Truncate log output in SSE messages while preserving full execution results in storage.

### D. Handle Compatibility & Type Safety (Low-Medium Risk)
- **Problem**: Connecting an incompatible output type (e.g., boolean) to an input expecting a dictionary or list can cause runtime crashes mid-flow.
- **Mitigation Strategy**:
  - Validate edge connection compatibility on both frontend (visual handle color indicators and connection validation rules in `@vue-flow/core`) and backend (pre-flight validation before graph execution).

### E. Frontend-Backend Schema Drift (Low Risk)
- **Problem**: Changing a Python component's input names or types in code could break older saved flows in the database.
- **Mitigation Strategy**:
  - Version components (`version: "1.0.0"`).
  - Provide fallback default values for missing input keys when loading legacy flow JSON.
