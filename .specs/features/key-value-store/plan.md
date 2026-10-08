# Plan: Key-Value Store Component (ADR 0029)

## 1. Problem Statement & Motivation
Workflows need a simple, durable mechanism to retain state across execution cycles — such as deduplicating incoming events, maintaining rate-limit counters, holding pagination cursors, and storing feature flags.

Currently, achieving this requires either defining an environment variable in `VariableComponent` (which is oriented toward static configuration) or writing raw SQL via `DatabaseQueryComponent`.

The `KeyValueStoreComponent` introduces dedicated, high-performance key-value operations with namespace isolation and atomic counter support.

## 2. Scope & Boundaries
- **In Scope**:
  - Add `kv_store` table and helper methods (`kv_get`, `kv_set`, `kv_delete`, `kv_increment`, `kv_list`) in `DatabaseManager` (`backend/src/backend/app/db.py`).
  - Implement `KeyValueStoreComponent` in `backend/src/backend/app/components/builtins/actions.py` and register in `backend/src/backend/app/components/builtins/__init__.py`.
  - Operations supported: `get`, `set`, `delete`, `increment`, `list`.
  - Type preservation for JSON, numbers, booleans, and strings.
  - UI updates in `CustomNode.vue` and `ComponentPalette.vue` using `HardDrive` icon and Teal styling.
  - Backend integration tests and frontend Vitest suite.
- **Out of Scope**:
  - External Redis cluster drivers or distributed lock algorithms (deferred to future distributed execution milestones).

## 3. High-Level Approach
- TDD cycle: write unit tests for `DatabaseManager` KV methods and `KeyValueStoreComponent`, implement DB table and component, test frontend canvas, audit sensors.

## 4. Dependencies & Prerequisites
- SQLAlchemy 2.0 (already integrated).
- `lucide-vue-next` (has `HardDrive` icon).

## 5. Architectural Decision Records (ADRs)
- Relates to [ADR 0029: Key-Value Store Component for Cross-Execution State and Counters](../../project/ADRs/0029-key-value-store-component.md).
