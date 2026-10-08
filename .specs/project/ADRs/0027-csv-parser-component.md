# ADR 0027: CSV Parser & Generator Component for Tabular Data

## Status
Accepted

## Date
2026-10-07

## Context
CSV (Comma-Separated Values) remains the most common interchange format for batch exports, financial reports, spreadsheets, and database dumps.

FlowBuild workflows frequently need to:
1. Parse incoming CSV strings (from HTTP downloads, Webhook uploads, or file readers) into structured JSON arrays of objects so downstream nodes (`DataFilterComponent`, `DataMapperComponent`, `DatabaseQueryComponent`) can process each row.
2. Generate formatted CSV text from JSON arrays of objects to attach to emails (`EmailNotificationComponent`) or upload to external storage.

Currently, converting CSV to JSON or vice-versa requires custom code inside `PythonScriptComponent`.

A dedicated `CsvParserComponent` provides bidirectional conversion with configurable delimiters, header detection, and row metrics directly on the visual canvas.

## Decision
1. **Component Design (`CsvParserComponent`)**:
   - Class name: `CsvParserComponent`
   - Display name: `"CSV Parser"`
   - Category: `"Transform"`
   - Description: `"Parses CSV text into JSON collections, or converts JSON collections into formatted CSV strings."`
   - Icon: `"file-spreadsheet"`
2. **Inputs**:
   - `mode` (`SelectInput`, options=`["parse", "generate"]`, default=`"parse"`): Operational direction (`"parse"`: CSV -> JSON, `"generate"`: JSON -> CSV).
   - `csv_data` (`StrInput`, default=""): Input CSV text string (used in `"parse"` mode).
   - `json_data` (`DictInput` / `BaseInput`, default=[]): Input collection of objects (used in `"generate"` mode).
   - `delimiter` (`StrInput`, default=","): Column delimiter character (e.g. `","`, `";"`, `"\t"`).
   - `has_headers` (`BoolInput`, default=True): Whether the CSV includes a header row.
   - `skip_empty_lines` (`BoolInput`, default=True): Ignore blank lines.
   - `custom_headers` (`StrInput`, default=""): Optional comma-separated list of column headers for ordering in generate mode.
3. **Outputs**:
   - `data` (`Output`, type="any"): Parsed list of dictionaries (or CSV text string in generate mode).
   - `row_count` (`Output`, type="int"): Total number of data rows processed (excluding header).
   - `headers` (`Output`, type="list"): Extracted or generated column header names.
4. **Execution Semantics & Resilience**:
   - Uses Python standard library `csv.reader`, `csv.DictReader`, and `csv.DictWriter` with `io.StringIO`.
   - Automatically handles quoted fields, internal commas, and multiline cells according to RFC 4180.
   - Gracefully handles empty inputs or malformed lines without throwing unhandled exceptions.
5. **Frontend Canvas & Palette Integration**:
   - Map `csv` in `ComponentPalette.vue` and `CustomNode.vue` to `FileSpreadsheet` icon with Emerald Transform styling (`text-emerald-400 bg-emerald-500/10 border-emerald-500/30`).

## Consequences
- **Positive**: Native bidirectional CSV parsing and generation without writing custom scripts.
- **Completeness**: Completes the Transform & Manipulation cluster alongside `DataFilterComponent`, `DataMapperComponent`, and `DataAggregatorComponent`.
- **Safety**: Robust RFC 4180 compliance with zero unhandled exceptions.
- **Backwards Compatibility**: 100% additive; no breaking changes.
