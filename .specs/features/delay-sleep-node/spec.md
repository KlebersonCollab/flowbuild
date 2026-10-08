# Feature Spec: Delay / Sleep Node Component (ADR 0017)

## 1. User Stories & Acceptance Criteria

### US-01: Configurable Delay Execution
As a workflow author, I want to add a Delay node with duration and unit options so that the workflow pauses for the desired amount of time.
- **AC-01.1**: When `delay=0.1` and `unit="seconds"`, execution awaits approximately 0.1 seconds before completing.
- **AC-01.2**: When `delay=100` and `unit="milliseconds"`, execution converts to 0.1 seconds and completes successfully.
- **AC-01.3**: When `delay=0.01` and `unit="minutes"`, execution converts to 0.6 seconds and completes successfully.
- **AC-01.4**: When `delay` is 0 or negative, execution does not fail and completes with `waited_seconds=0.0`.

### US-02: Transparent Data Pass-Through
As a workflow author, I want incoming payload data to pass through the Delay node into downstream nodes without losing properties.
- **AC-02.1**: When `input_data={"order_id": 42, "status": "pending"}` is provided, output `data` equals `{"order_id": 42, "status": "pending"}`.
- **AC-02.2**: When downstream nodes connect to handle `data`, they receive the exact incoming payload.
- **AC-02.3**: Output `waited_seconds` returns the actual duration slept in seconds.

### US-03: Variable Interpolation Support
As a workflow author, I want to supply the delay duration via flow/global variables or template tags (e.g. `{{DELAY_SEC}}`).
- **AC-03.1**: When `delay="{{DELAY_SEC}}"` and `DELAY_SEC="0.05"`, `FlowRunner` interpolates the value and sleeps for 0.05 seconds.

### US-04: Frontend Visual Canvas & Dynamic Inspector
As a canvas builder user, I want to find "Delay / Sleep" in the Logic palette, drag it onto canvas, and configure duration and unit inline or in inspector.
- **AC-04.1**: `DelayComponent` appears in `ComponentPalette.vue` under category `Logic` with a clock icon.
- **AC-04.2**: `CustomNode.vue` displays the clock icon and renders inline numeric input for `delay` and dropdown for `unit`.
- **AC-04.3**: `NodeInspector.vue` allows editing `delay`, `unit`, and viewing outputs during live telemetry.
