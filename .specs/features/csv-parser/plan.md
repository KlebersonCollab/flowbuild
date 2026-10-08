# Plan: CSV Parser Component (ADR 0027)

## 1. Problem Statement & Motivation
Handling tabular text data is essential for data ingestion and report generation. When webhooks receive CSV payloads or when scheduled reports export tabular files, converting between CSV strings and JSON collections requires repetitive parsing logic.

The `CsvParserComponent` introduces native, bidirectional CSV transformation capabilities directly to FlowBuild workflows.

## 2. Scope & Boundaries
- **In Scope**:
  - Implement `CsvParserComponent` in `backend/src/backend/app/components/builtins/actions.py` and register in `backend/src/backend/app/components/builtins/__init__.py`.
  - Configurable inputs: `mode` (`parse` vs `generate`), `csv_data`, `json_data`, `delimiter`, `has_headers`, `skip_empty_lines`, `custom_headers`.
  - Outputs: `data`, `row_count`, `headers`.
  - RFC 4180 standard parsing via Python's built-in `csv` and `io.StringIO`.
  - UI updates in `CustomNode.vue` and `ComponentPalette.vue` using `FileSpreadsheet` icon and Emerald styling.
  - Comprehensive unit tests in backend and frontend.
- **Out of Scope**:
  - Binary XLSX/Excel parsing (which requires external libraries like openpyxl).

## 3. High-Level Approach
- TDD cycle: test first, verify failure, implement, test frontend, update styling, audit sensors.

## 4. Dependencies & Prerequisites
- Python standard library `csv` and `io` (zero external packages).
- `lucide-vue-next` (has `FileSpreadsheet` icon).

## 5. Architectural Decision Records (ADRs)
- Relates to [ADR 0027: CSV Parser & Generator Component for Tabular Data](../../project/ADRs/0027-csv-parser-component.md).
