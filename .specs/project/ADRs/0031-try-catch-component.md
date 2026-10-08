# ADR 0031: Try / Catch Error Boundary Component and Upstream Resilience

## Status
Accepted

## Date
2026-10-07

## Context
Production workflows interact with unreliable external dependencies: network APIs can time out, external webhooks may respond with 500 Internal Server Errors, and SQL queries can fail when constraints are violated.

In FlowBuild's DAG execution engine, an unhandled node failure normally cascades skips across all downstream nodes (`upstream_error`), immediately terminating the entire workflow with `flow_failed`.

Real-world automations require resilience:
1. Intercepting errors from upstream dependencies without failing the entire workflow.
2. Routing successfully resolved data down a `success_branch` and errors down an `error_branch` (e.g. to notify developers via Slack, Discord, or Email).
3. Supplying an optional default `fallback_value` so subsequent downstream nodes can continue execution seamlessly.
4. Utilizing generalized conditional branch skipping in `FlowRunner` so inactive branches (`success_branch` vs `error_branch`) are skipped cleanly.

## Decision
1. **Component Design (`TryCatchComponent`)**:
   - Class name: `TryCatchComponent`
   - Display name: `"Try / Catch"`
   - Category: `"Logic"`
   - Description: `"Catches upstream failures, provides fallback values, and routes execution between success and error branches."`
   - Icon: `"shield-alert"`
2. **Inputs**:
   - `input_data` (`DictInput` / `BaseInput`, default={}): Normal payload from upstream nodes.
   - `fallback_value` (`DictInput` / `BaseInput`, default={}): Fallback payload emitted when an error is caught.
   - `catch_upstream_errors` (`BoolInput`, default=True): If True, intercepts failures from upstream nodes connected to it.
   - `error_message` (`StrInput`, default=""): Injected or simulated error description.
3. **Outputs**:
   - `success_branch` (`Output`, type="any"): Payload if no error occurred (`None` if error caught, triggering branch skipping).
   - `error_branch` (`Output`, type="dict"): Error metadata dictionary (`None` if execution was successful, triggering branch skipping).
   - `result` (`Output`, type="any"): Either `input_data` (if successful) or `fallback_value` (if error caught).
   - `has_error` (`Output`, type="bool"): True if an error was detected or intercepted.
   - `error_details` (`Output`, type="str"): Error message string.
4. **Engine Integration (`FlowRunner`)**:
   - In `runner.py`: Add `"success_branch"` and `"error_branch"` to `has_conditional_edge` handle list for automatic branch skipping.
   - Error interception: When a predecessor of `TryCatchComponent` fails and `catch_upstream_errors` is True, `FlowRunner` intercepts the failure, injects the error into `TryCatchComponent`'s execution context, and continues flow execution instead of aborting.
5. **Frontend Canvas & Palette Integration**:
   - Register under category `"Logic"`.
   - Uses `ShieldAlert` icon from `lucide-vue-next` with Rose Linear dark styling (`text-rose-400 bg-rose-500/10 border-rose-500/30`, badge `bg-rose-500/15 text-rose-300 border-rose-500/30`, dot `bg-rose-400`).

## Consequences
- **Positive**: Workflows gain industrial-grade fault tolerance, graceful fallbacks, and selective alert routing on failure.
- **Completeness**: Completes Cluster 4 (Controle de Fluxo & Confiabilidade) alongside `LoopIteratorComponent`.
- **DAG Integrity**: Maintains DAG acyclicity while delivering standard try/catch semantics.
- **Backwards Compatibility**: 100% additive; workflows without `TryCatchComponent` behave identically.
