# Specification: CSV Parser Component (ADR 0027)

## 1. User Stories
- **US-1**: As a workflow creator, I want to convert a CSV text string into a list of structured JSON objects with dictionary keys corresponding to CSV headers, so that downstream nodes can filter, map, and process records.
- **US-2**: As an alert builder, I want to serialize an array of JSON objects into a formatted CSV string, so that I can send it via email or webhook.
- **US-3**: As a developer, I want to customize the delimiter (e.g. semicolons `;` or tabs `\t`), so that regional or non-standard CSV files are properly parsed.

## 2. Business Rules & Invariants
- **BR-1**: In `"parse"` mode:
  - If `has_headers` is True, output `data` is a list of dictionaries with column names as keys.
  - If `has_headers` is False, output `data` is a list of string lists (`list[list[str]]`), and `headers` is an empty list or auto-generated index names (`col_0`, `col_1`, ...).
  - `row_count` is the number of data rows parsed (excluding the header row).
- **BR-2**: In `"generate"` mode:
  - Input `json_data` must be a list of dictionaries.
  - `custom_headers` (if provided as a comma-separated string) dictates the output column order and selection.
  - If `custom_headers` is empty, keys from the first item (or union of keys) are used as headers.
  - Output `data` is the resulting CSV string formatted according to RFC 4180.
- **BR-3**: Empty lines or empty inputs produce `row_count = 0`, `data = []` (in parse mode) or `""` (in generate mode), without throwing exceptions.

## 3. Acceptance Criteria (BDD)

### Happy Path (Success Scenarios)
- **AC-1: Parse Standard CSV with Headers**
  - **Given** `csv_data = "id,name,role\n1,Alice,Engineer\n2,Bob,Designer\n"` and `mode="parse"`
  - **When** the component executes
  - **Then** output `data` is `[{"id": "1", "name": "Alice", "role": "Engineer"}, {"id": "2", "name": "Bob", "role": "Designer"}]`, `row_count` is 2, and `headers` is `["id", "name", "role"]`.

- **AC-2: Parse Semicolon-Separated CSV**
  - **Given** `csv_data = "sku;price\nA1;10.5\nB2;20.0"`, `delimiter=";"`, and `mode="parse"`
  - **When** the component executes
  - **Then** output `data` contains 2 records and `headers` is `["sku", "price"]`.

- **AC-3: Generate CSV from JSON Array**
  - **Given** `json_data = [{"name": "Server 1", "status": "UP"}, {"name": "Server 2", "status": "DOWN"}]` and `mode="generate"`
  - **When** the component executes
  - **Then** output `data` is `"name,status\r\nServer 1,UP\r\nServer 2,DOWN\r\n"`, `row_count` is 2, and `headers` is `["name", "status"]`.

### Edge Cases & Exceptions (Resilience)
- **AC-4: Quoted Fields with Commas**
  - **Given** `csv_data = 'name,address\nAlice,"123 Main St, Suite 4"\n'`
  - **When** the component executes
  - **Then** `data[0]["address"]` is `"123 Main St, Suite 4"`.

- **AC-5: Empty Input String or Collection**
  - **Given** `csv_data = ""` in parse mode, or `json_data = []` in generate mode
  - **When** the component executes
  - **Then** `row_count` is 0, without runtime errors.

## 4. Test Data & Boundary Matrix
| Parameter / Field | Valid Inputs (Happy) | Invalid / Boundary Inputs (Edge) |
|---|---|---|
| `mode` | `"parse"`, `"generate"` | `""` (defaults to `"parse"`) |
| `csv_data` | `"a,b\n1,2"`, `"x;y\n10;20"` | `""`, `None` |
| `json_data` | `[{"a": 1}]` | `[]`, `None`, `{}` |
| `delimiter` | `","`, `";"`, `"\t"` | `""` (defaults to `","`) |
| `has_headers` | `True`, `False` | `None` |

## 5. Verification Sensors
| Sensor | Command / Target | Success Threshold |
|---|---|---|
| Backend Test Suite | `uv run pytest backend/tests/test_csv_parser.py` | 100% pass |
| Frontend Test Suite | `npx vitest run frontend/tests/csv_parser.test.ts` | 100% pass |
| Full Vitest Suite | `npx vitest run` | 100% pass |
| Frontend Build | `npm run build` in `frontend/` | Exit 0, 0 type errors |
| Backend Pytest Suite | `uv run pytest` in `backend/` | 100% pass |
