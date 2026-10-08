# Feature Plan: Delay / Sleep Node Component (ADR 0017)

## 1. Executive Summary
Introduce a native `DelayComponent` ("Delay / Sleep") in the "Logic" category of FlowBuild. This node enables workflows to pause execution for a configurable duration (`seconds`, `milliseconds`, `minutes`) and transparently forwards the incoming payload data to subsequent nodes, facilitating rate limiting, polling intervals, and timed automations without custom code.

## 2. Architecture & Design Alignment
- **Component**: `DelayComponent` in `backend/src/backend/app/components/builtins/logic.py`.
- **Inputs**:
  - `input_data`: `DictInput(name="input_data", label="Incoming Data", default={}, description="Data payload to pass through to downstream nodes")`
  - `delay`: `FloatInput(name="delay", label="Duration", default=1.0, required=True, description="Amount of time to wait")`
  - `unit`: `SelectInput(name="unit", label="Time Unit", options=["seconds", "milliseconds", "minutes"], default="seconds", description="Unit of time for duration")`
- **Outputs**:
  - `data`: `Output(name="data", label="Output Data", type="dict", method="get_data")`
  - `waited_seconds`: `Output(name="waited_seconds", label="Waited Seconds", type="float", method="get_waited_seconds")`
- **Execution Engine**:
  - Executes `await asyncio.sleep(seconds)` inside `execute()`.
  - Computes `seconds` based on `unit` (`ms`: `delay / 1000`, `min`: `delay * 60`, `seconds`: `delay`), clamped to `>= 0.0`.
  - Supports template variable interpolation (e.g., `{{WAIT_TIME}}`) via `FlowRunner._interpolate_value`.
- **Frontend Integration**:
  - Palette and Canvas node mappings in `ComponentPalette.vue` and `CustomNode.vue` with `Clock` icon and Linear styling.
  - Quick inline number input support for `int` and `float` in `CustomNode.vue`.

## 3. Risks & Non-Regression
- **Zero Event Loop Blocking**: Using `asyncio.sleep()` ensures the FastAPI thread and other concurrent workflows continue uninterrupted.
- **Payload Preservation**: The incoming payload from `input_data` is emitted unaltered via the `data` output port.
- **Zero Breaking Changes**: Existing workflows and components remain completely unaffected.
