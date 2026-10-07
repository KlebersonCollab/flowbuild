# Feature Specification: Paginated HTTP Client with Loop and Break Condition

## 1. Component Schema & Inputs
Component: `PaginatedHttpComponent`
Category: `HTTP` / `Actions`

| Input Name | Type | Default | Description |
|---|---|---|---|
| `url` | StrInput | `""` | Target API URL (supports `{{VAR}}` interpolation) |
| `method` | StrInput | `"GET"` | HTTP method (`GET`, `POST`) |
| `pagination_mode` | StrInput | `"page_number"` | Mode: `page_number`, `offset_limit`, or `cursor` |
| `page_param` | StrInput | `"page"` | Parameter name for page number or offset |
| `limit_param` | StrInput | `"limit"` | Parameter name for limit/page size |
| `page_size` | IntInput | `20` | Items per page |
| `start_page` | IntInput | `1` | Initial page or starting offset |
| `items_path` | StrInput | `"items"` | Path to items array in response (e.g. `items`, `data`, `results`, or empty for root list) |
| `cursor_path` | StrInput | `"next_cursor"` | Path to next cursor or next URL in response |
| `break_condition` | StrInput | `""` | Custom Python expression evaluated per page (e.g. `len(items) == 0` or `page >= 5`) |
| `max_pages` | IntInput | `25` | Maximum number of pages to fetch (safety bound) |
| `headers` | DictInput | `{}` | HTTP Request Headers |
| `timeout` | IntInput | `15` | Request timeout in seconds |

## 2. Component Outputs

| Output Name | Type | Description |
|---|---|---|
| `all_items` | list | Flat list containing all aggregated items from all fetched pages |
| `total_items` | int | Total number of items retrieved |
| `pages_fetched` | int | Number of page HTTP requests made |
| `last_page` | dict / list | Payload received in the last request |
| `summary` | dict | Summary dictionary with metadata, items count, pages count, and reason for stop |

## 3. Acceptance Criteria (BDD)

### Scenario 1: Page Number Pagination until Empty
- **Given** an API returning 10 items on page 1, 5 items on page 2, and 0 items on page 3.
- **When** `PaginatedHttpComponent` executes with `pagination_mode = "page_number"` and `start_page = 1`.
- **Then** it makes 3 requests (pages 1, 2, 3), collects 15 items in `all_items`, and terminates because page 3 returned 0 items.

### Scenario 2: Break Condition Early Termination
- **Given** an API returning continuous pages of items.
- **When** `PaginatedHttpComponent` executes with `break_condition = "total_items >= 25"` or `page >= 3`.
- **Then** it breaks immediately after reaching the condition without requesting remaining pages.

### Scenario 3: Offset / Limit Pagination
- **Given** an API using `offset` and `limit`.
- **When** `PaginatedHttpComponent` executes with `start_page = 0`, `page_size = 20`.
- **Then** page 1 sends `offset=0&limit=20`, page 2 sends `offset=20&limit=20`, etc.

### Scenario 4: Cursor-based Pagination
- **Given** an API returning `{ "items": [...], "next_cursor": "abc123" }` and then `{ "items": [...], "next_cursor": null }`.
- **When** `PaginatedHttpComponent` executes with `pagination_mode = "cursor"`, `cursor_path = "next_cursor"`.
- **Then** it passes cursor tokens until `next_cursor` is null and terminates with all items.

### Scenario 5: Safety Max Pages Limit
- **Given** an API that never returns empty items.
- **When** `PaginatedHttpComponent` executes with `max_pages = 5`.
- **Then** execution terminates after 5 pages with `stop_reason = "max_pages_reached"` and preserves all items fetched so far.
