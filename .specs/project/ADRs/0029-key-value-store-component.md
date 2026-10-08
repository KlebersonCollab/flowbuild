# ADR 0029: Key-Value Store Component for Cross-Execution State and Counters

## Status
Accepted

## Date
2026-10-07

## Context
Workflows frequently need lightweight state persistence across independent execution runs:
1. Rate limiting and quota management (e.g., incrementing an hourly invocation counter).
2. Deduplication and idempotent processing (e.g., checking if a message ID or webhook event has already been handled).
3. Pagination checkpoints (e.g., storing the last processed cursor or record ID).
4. Cross-workflow coordination (e.g., sharing a toggle flag or operational token).

While `VariableComponent` manages deployment configuration and global environment variables, it does not provide atomic increments, namespaces, key listing, or dynamic key-value operations suited for rapid transient state.

A dedicated `KeyValueStoreComponent` backed by the internal database provides fast, atomic, and structured key-value storage with operations: `get`, `set`, `delete`, `increment`, and `list`.

## Decision
1. **Database Schema Extension (`kv_store` table)**:
   - Add `kv_store` table in `DatabaseManager` (`backend/src/backend/app/db.py`) with columns:
     - `key` (`String(190)`, primary key)
     - `namespace` (`String(64)`, primary key, default `"default"`)
     - `value` (`Text`, nullable=False)
     - `value_type` (`String(32)`, default `"string"`)
     - `created_at` (`String(64)`, nullable=False)
     - `updated_at` (`String(64)`, nullable=False)
   - Composite primary key `(key, namespace)` ensures namespace isolation and fast indexed lookups.
   - Methods added to `DatabaseManager`: `kv_get`, `kv_set`, `kv_delete`, `kv_increment`, `kv_list`.
2. **Component Design (`KeyValueStoreComponent`)**:
   - Class name: `KeyValueStoreComponent`
   - Display name: `"Key-Value Store"`
   - Category: `"Storage"`
   - Description: `"Persists and manages cross-execution state, flags, and atomic counters across workflow runs."`
   - Icon: `"hard-drive"`
3. **Inputs**:
   - `operation` (`SelectInput`, options=`["get", "set", "delete", "increment", "list"]`, default=`"get"`): The KV operation to perform.
   - `key` (`StrInput`, default="my_key", required=True): Target key identifier.
   - `value` (`StrInput` / `DictInput` / `BaseInput`, default=""): Value to persist in `"set"` operation.
   - `namespace` (`StrInput`, default="default"): Logical grouping or partition namespace.
   - `default_value` (`StrInput`, default=""): Fallback value returned if key does not exist during `"get"`.
   - `amount` (`IntInput`, default=1): Step value for `"increment"` operations (can be negative for decrements).
4. **Outputs**:
   - `result` (`Output`, type="any"): The retrieved value, updated value, incremented counter, or list of keys.
   - `found` (`Output`, type="bool"): Whether the key existed prior to the operation.
   - `key` (`Output`, type="str"): The key name operated on.
   - `previous_value` (`Output`, type="any"): Value before mutation (or None).
5. **Type Preservation**:
   - Automatically detects and serializes JSON objects, lists, numbers, booleans, and strings, maintaining data types across workflow boundaries.
6. **Frontend Canvas & Palette Integration**:
   - Register under category `"Storage"`.
   - Uses `HardDrive` icon from `lucide-vue-next` with Teal / Storage styling (`text-teal-400 bg-teal-500/10 border-teal-500/30`, badge `bg-teal-500/15 text-teal-300 border-teal-500/30`, dot `bg-teal-400`).

## Consequences
- **Positive**: Workflows have instant, native state persistence and atomic counters without setting up external Redis or creating custom SQL tables.
- **Completeness**: Completes Cluster 3 (Banco de Dados & Armazenamento) alongside `DatabaseQueryComponent`.
- **Concurrency**: SQLite WAL mode and atomic transaction handling prevent state corruption.
- **Backwards Compatibility**: 100% additive; no modifications to existing tables.
