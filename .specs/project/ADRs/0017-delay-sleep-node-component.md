# ADR 0017: Delay and Sleep Node Component for Flow Execution

## Status
Accepted

## Date
2026-10-07

## Context
In workflow automation platforms (such as n8n, Zapier, and Langflow), automated sequences frequently require explicit timing intervals between steps. Common real-world scenarios include:
1. Rate limiting and backoff: Throttling requests to third-party APIs to avoid HTTP 429 Too Many Requests.
2. Webhook / event polling: Waiting for external jobs (e.g., asynchronous payment processing, file encoding, LLM generation) to complete before querying status.
3. Debouncing and scheduled sequencing: Introducing deliberate delays between multi-step notifications or messaging pipelines.

Prior to this ADR, FlowBuild lacked a dedicated timing/await component in its component catalog. Workflow authors had to resort to custom Python scripts using synchronous or arbitrary sleeps, which risks blocking or inconsistent behavior.

## Decision
1. **Component Design (`DelayComponent`)**:
   - Class name: `DelayComponent`
   - Display name: `"Delay / Sleep"`
   - Category: `"Logic"`
   - Description: `"Suspends workflow execution for a specified duration before proceeding to downstream nodes."`
   - Icon: `"clock"`
2. **Inputs**:
   - `input_data` (`BaseInput` / `DictInput`): Incoming data payload to pass through transparently to downstream nodes (default: `{}`).
   - `delay` (`FloatInput`): Duration value to wait (default: `1.0`, required: `True`).
   - `unit` (`SelectInput`): Time unit selector (`["seconds", "milliseconds", "minutes"]`, default: `"seconds"`).
3. **Outputs & Data Pass-Through**:
   - `data` (`Output`): Transparent pass-through of `input_data`, ensuring downstream nodes receive the upstream payload intact.
   - `waited_seconds` (`Output`): Elapsed sleep time in seconds (`float`).
4. **Non-Blocking Asynchronous Runtime**:
   - Execution leverages `await asyncio.sleep(seconds)` within `execute()` / `wait()`, preserving the non-blocking nature of FastAPI and the `FlowRunner` async event loop.
5. **Frontend Node Rendering & Theme**:
   - In `ComponentPalette.vue` and `CustomNode.vue`, map `clock` icon with Amber/Orange Linear dark tokens (`text-amber-400 bg-amber-500/10 border-amber-500/30`).
   - Add inline number input support for `int` and `float` field types in `CustomNode.vue` quick inline card controls.

## Consequences
- **Positive**: Native, reliable pause/await capability across all workflows without custom script workarounds.
- **Data Integrity**: Payload passed through transparently without mutation, maintaining complete DAG composability.
- **Reactivity & SSE**: Live execution telemetry in `ExecutionDrawer.vue` smoothly reflects `running` status during the delay and transitions to `completed`.
