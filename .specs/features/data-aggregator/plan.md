# Plan: Data Aggregator Component (ADR 0026)

## 1. Problem Statement & Motivation
Pipelines ingesting data from REST APIs, database queries, or spreadsheets frequently need summary calculations (e.g. total cart value, average execution latency, maximum temperature, or concatenating user IDs into a comma-separated list).

Providing a native `DataAggregatorComponent` simplifies collection processing into a reliable, declarative node.

## 2. Scope & Boundaries
- **In Scope**:
  - Implement `DataAggregatorComponent` in `backend/src/backend/app/components/builtins/actions.py` and register in `backend/src/backend/app/components/builtins/__init__.py`.
  - Configurable inputs: `items`, `items_path`, `field`, `operation`, `group_by`, `delimiter`.
  - Outputs: `result`, `summary`, and `count`.
  - Operations supported: `all`, `sum`, `avg`, `min`, `max`, `count`, `concat`.
  - Partitioned summaries when `group_by` is specified.
  - Integration with `CustomNode.vue` and `ComponentPalette.vue` using `Calculator` icon and Emerald styling.
  - Tests covering numeric conversions, empty datasets, grouped summaries, and FlowRunner integration.
- **Out of Scope**:
  - Advanced multidimensional OLAP slicing or pandas DataFrames (FlowBuild is focused on lightweight event-driven automation).

## 3. High-Level Approach
- Implement robust parsing, numeric extraction with fallback, and grouping dictionaries.
- TDD cycle: test first, verify failure, implement, test frontend, update styling, audit sensors.

## 4. Dependencies & Prerequisites
- Standard Python built-in math and statistics.
- `lucide-vue-next` (has `Calculator` icon).

## 5. Architectural Decision Records (ADRs)
- Relates to [ADR 0026: Data Aggregator Component for Collection Metrics & Grouping](../../project/ADRs/0026-data-aggregator-component.md).
