# Plan: Loop Iterator Component (ADR 0030)

## 1. Problem Statement & Motivation
When processing datasets in FlowBuild, large collections cannot always be sent to downstream components all at once. For example, triggering a bulk email dispatch on 5,000 users or posting 1,000 webhooks in a single step leads to socket timeouts, third-party rate limits, and memory bloat.

The `LoopIteratorComponent` provides declarative batching, slicing, and pagination metrics without requiring cyclic graphs.

## 2. Scope & Boundaries
- **In Scope**:
  - Implement `LoopIteratorComponent` in `backend/src/backend/app/components/builtins/logic.py` and register in `backend/src/backend/app/components/builtins/__init__.py`.
  - Configurable inputs: `items`, `items_path`, `batch_size`, `batch_index`, `max_batches`.
  - Outputs: `current_batch`, `batches`, `total_items`, `total_batches`, `has_more`, `batch_info`.
  - Dot-notation extraction via `items_path`.
  - UI updates in `CustomNode.vue` and `ComponentPalette.vue` using `Repeat` icon and Indigo styling.
  - Comprehensive unit and integration tests in backend and frontend.
- **Out of Scope**:
  - Unbounded cyclic recursion in the canvas (which violates DAG invariants).

## 3. High-Level Approach
- TDD cycle: test first, verify failure, implement in `logic.py`, register in builtins, test frontend canvas, audit sensors.

## 4. Dependencies & Prerequisites
- Python standard library (slicing and math).
- `lucide-vue-next` (has `Repeat` icon).

## 5. Architectural Decision Records (ADRs)
- Relates to [ADR 0030: Loop Iterator Component for Collection Chunking and Batch Processing](../../project/ADRs/0030-loop-iterator-component.md).
