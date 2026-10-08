# ADR 0030: Loop Iterator Component for Collection Chunking and Batch Processing

## Status
Accepted

## Date
2026-10-07

## Context
Processing large collections of data (e.g. hundreds of customers from an SQL query, rows from a CSV, or records from an API) in a single monolithic payload causes memory spikes, rate-limit bans on downstream APIs (e.g. email or webhook limits), and lack of operational granularity.

In DAG-based execution engines (where arbitrary back-edges are forbidden to preserve acyclicity), batch chunking and windowed iteration allow workflows to safely slice large collections into manageable batches, track batch offsets across runs with `KeyValueStoreComponent`, or process collections with controlled chunk sizes.

A native `LoopIteratorComponent` provides declarative batching, slicing, and iteration metrics directly within the DAG.

## Decision
1. **Component Design (`LoopIteratorComponent`)**:
   - Class name: `LoopIteratorComponent`
   - Display name: `"Loop Iterator"`
   - Category: `"Logic"`
   - Description: `"Partitions collections into manageable batches, slices subsets, and emits iteration metrics without violating DAG acyclicity."`
   - Icon: `"repeat"`
2. **Inputs**:
   - `items` (`DictInput` / `BaseInput`, default=[], required=True): Input array of items or dict containing a collection.
   - `items_path` (`StrInput`, default=""): Optional dot-notation path to extract collection from nested object (e.g. `data.records`).
   - `batch_size` (`IntInput`, default=10): Number of elements per batch. Must be >= 1.
   - `batch_index` (`IntInput`, default=0): 0-indexed batch number to emit in `current_batch` output.
   - `max_batches` (`IntInput`, default=0): Maximum number of batches to construct (0 = unlimited).
3. **Outputs**:
   - `current_batch` (`Output`, type="list"): Items in the specified `batch_index` (empty if index out of range).
   - `batches` (`Output`, type="list"): All partitioned batches (`list[list[Any]]`).
   - `total_items` (`Output`, type="int"): Total count of items in the input collection.
   - `total_batches` (`Output`, type="int"): Total number of batches created.
   - `has_more` (`Output`, type="bool"): Whether additional batches exist after `batch_index` (`batch_index < total_batches - 1`).
   - `batch_info` (`Output`, type="dict"): Metadata dictionary containing `batch_index`, `batch_size`, `item_count`, `start_index`, and `end_index`.
4. **Execution Semantics & Resilience**:
   - Gracefully handles non-list inputs (coerces single objects to 1-item lists, empty inputs to `[]`).
   - Safe pagination: out-of-range `batch_index` returns `current_batch = []`, `has_more = False` without exceptions.
   - Protects against zero/negative `batch_size` by enforcing minimum `batch_size = 1`.
5. **Frontend Canvas & Palette Integration**:
   - Register under category `"Logic"`.
   - Uses `Repeat` icon from `lucide-vue-next` with Indigo Linear dark styling (`text-indigo-400 bg-indigo-500/10 border-indigo-500/30`, badge `bg-indigo-500/15 text-indigo-300 border-indigo-500/30`, dot `bg-indigo-400`).

## Consequences
- **Positive**: Workflows can partition large arrays into micro-batches for rate-limited APIs and chunked ETL pipelines.
- **DAG Invariant Preservation**: Complies with DAG acyclicity without requiring complex cyclic graph edges.
- **Synergy**: Works seamlessly with `DatabaseQueryComponent`, `CsvParserComponent`, and `KeyValueStoreComponent`.
- **Backwards Compatibility**: 100% additive; no breaking changes.
