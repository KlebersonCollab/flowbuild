# Plan: Data Mapper Component (ADR 0025)

## 1. Problem Statement & Motivation
Data moving through integration pipelines frequently requires restructuring: converting camelCase to snake_case, flattening deeply nested structures (`user.address.city` -> `city`), discarding sensitive fields, or preparing database rows for external API payloads.

Without a dedicated Data Mapper, users must write Python scripts or complex eval strings. `DataMapperComponent` introduces declarative dictionary mapping with dot-notation path extraction and support for both single objects and arrays of records.

## 2. Scope & Boundaries
- **In Scope**:
  - Implement `DataMapperComponent` in `backend/src/backend/app/components/builtins/actions.py` and register in `backend/src/backend/app/components/builtins/__init__.py`.
  - Configurable inputs: `input_data`, `mapping`, `items_path`, `pass_unmapped`, `mode`.
  - Nested dot-notation traversal (`order.customer.email`) and list indexing (`items.0.sku`).
  - Outputs: `output_data` and `mapped_count`.
  - Single object and array mapping.
  - UI integration in `CustomNode.vue` and `ComponentPalette.vue` with `ArrowRightLeft` icon and Emerald styling.
  - Comprehensive unit tests in backend and frontend.
- **Out of Scope**:
  - Aggregation functions like SUM/AVG (handled by `DataAggregatorComponent` in next step).

## 3. High-Level Approach
- Implement pure, robust recursive path extraction with null safety.
- Follow TDD cycle: test first, verify failure, implement, test frontend, update styling, audit sensors.

## 4. Dependencies & Prerequisites
- Standard Python libraries and existing FlowBuild component primitives.
- `lucide-vue-next` (has `ArrowRightLeft`).

## 5. Architectural Decision Records (ADRs)
- Relates to [ADR 0025: Declarative Data Mapper Component for Record Transformation](../../project/ADRs/0025-data-mapper-component.md).
