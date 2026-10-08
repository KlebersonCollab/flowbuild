# Task List: CSV Parser Component (ADR 0027)

## Sequence Guidelines (MetaGPT SOP)
- **Strict Sequential Order**: Tasks must be executed top-to-bottom without reordering.
- **Atomic File Boundaries**: Each task modifies at most 1–3 specific target files.
- **Decoupled Test Setup**: Test tasks (`Type: test`) precede implementation tasks (`Type: feat`).
- **Sensor Evidence Gate**: Mark complete `[x]` ONLY after passing build, lint, and test sensors with recorded evidence.

## Implementation Tasks

| Status | ID | Type | Description | Target Files | Dependencies | Evidence |
|---|---|---|---|---|---|---|
| [x] | TASK-01 | test | Add backend integration tests for CsvParserComponent (parse mode, generate mode, custom delimiters, quoted cells, empty strings, and FlowRunner) | `backend/tests/test_csv_parser.py` | None | pytest 6 passed in 0.35s |
| [x] | TASK-02 | feat | Implement CsvParserComponent with bidirectional csv.reader and csv.writer in actions.py | `backend/src/backend/app/components/builtins/actions.py`, `backend/src/backend/app/components/builtins/__init__.py` | TASK-01 | 132 passed pytest full suite |
| [x] | TASK-03 | test | Add frontend unit tests verifying CsvParserComponent schema, ports, and palette display | `frontend/tests/csv_parser.test.ts` | TASK-02 | vitest 4 passed in 64ms |
| [x] | TASK-04 | feat | Update CustomNode and ComponentPalette with FileSpreadsheet icon and Emerald styling for CSV Parser | `frontend/src/components/CustomNode.vue`, `frontend/src/components/ComponentPalette.vue` | TASK-03 | vitest 117 passed, vue-tsc exit 0 |
| [x] | TASK-05 | review | Run full sensor verification (Pytest, Vitest, Vue build, and SDD integrity sensor) | `frontend/`, `backend/`, `.specs/` | TASK-04 | Pytest 132 passed, Vitest 117 passed, build ok, SDD sensor ok |

## Schema Dictionary
- **Status**: `[ ]` (Pending) | `[x]` (Verified Complete).
- **ID**: `TASK-01`, `TASK-02`, etc.
- **Type**: `test` | `feat` | `fix` | `refactor` | `docs` | `rules` | `skill` | `review`.
- **Target Files**: Concrete comma-separated file paths (relative to workspace root).
- **Dependencies**: Comma-separated list of preceding task IDs or `None`.
- **Evidence**: Commit hash (`git rev-parse --short HEAD`) + sensor output snippet.
