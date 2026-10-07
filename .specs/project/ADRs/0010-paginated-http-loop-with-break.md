# ADR 0010: Paginated HTTP Client with Loop and Break Condition

## Status
Accepted

## Date
2026-10-06

## Context
Automations frequently need to ingest data from paginated REST APIs (e.g., GitHub commits, Stripe transactions, CRM contacts, ERP inventories) that split records across multiple pages using page numbers (`?page=1`), limit/offset (`?offset=0&limit=50`), or cursor tokens (`?cursor=xyz` or `next_url`).
In a Directed Acyclic Graph (DAG) workflow engine, visual feedback cycles (connecting an edge back to an ancestor node) are strictly prohibited because they violate DAG topology and induce infinite loops or `CyclicGraphError`.
Therefore, pagination and iterative retrieval must be handled cleanly within a dedicated, robust component that performs asynchronous batch fetching with safety termination bounds and an expressive break condition.

## Decision
1. **Create `PaginatedHttpComponent`**:
   - Implement in `backend/src/backend/app/components/builtins/actions.py`.
   - Category: `HTTP` / `Actions`.
   - Inputs:
     - `url`: Base URL (supports interpolation `{{VAR}}` and `{page}`, `{cursor}`).
     - `method`: HTTP method (`GET`, `POST`).
     - `pagination_mode`: `page_number`, `offset_limit`, or `cursor`.
     - `page_param`: Name of query parameter for page/offset (default: `"page"` or `"offset"`).
     - `limit_param`: Name of query parameter for page size (default: `"limit"`).
     - `page_size`: Number of records per page (default: `20`).
     - `start_page`: Initial page or initial offset value (default: `1`).
     - `items_path`: Key or dot-path to locate the items array in the response (e.g., `"data"`, `"items"`, `"results"` or `""` for root lists).
     - `cursor_path`: Key or dot-path for next cursor or URL (e.g., `"next"`, `"next_cursor"`, `"meta.next_cursor"`).
     - `break_condition`: Optional Python expression to break early (e.g., `len(items) == 0` or `not data.get('has_more')`).
     - `max_pages`: Hard limit to prevent runaway loops (default: `25`, max: `100`).
     - `headers`: Dict of HTTP headers (e.g. Authorization).
     - `timeout`: Timeout per request in seconds (default: `15`).
   - Outputs:
     - `all_items`: Consolidated list containing all collected records across all pages (`list[Any]`).
     - `total_items`: Total count of collected records (`int`).
     - `pages_fetched`: Number of successful page requests executed (`int`).
     - `last_page`: Payload of the last page fetched (`dict` or `list`).
     - `summary`: Metadata dict with total_items, pages_fetched, and stop_reason (`dict`).

2. **Early Termination / Break Condition Protocol**:
   - The loop breaks when:
     - `break_condition` expression evaluates to `True`.
     - `items` array is empty (`len(items) == 0`).
     - In `cursor` mode, next cursor is `None` or empty.
     - `pages_fetched >= max_pages` is reached (safety ceiling).

3. **Frontend Integration & Canvas Template**:
   - Component is automatically discovered via `discover_package`.
   - Add pre-configured canvas template `"paginated_api_flow"` (*"Consumo de API Paginada com Loop & Break"*) to `flowStore.ts` and `TopNav.vue`.
   - Display node metrics and full consolidated output array in `ExecutionDrawer.vue` and `NodeInspector.vue`.

## Consequences
- **Positive**: Direct, single-node solution for paginated APIs without violating DAG acyclicity.
- **Positive**: Clean consolidated JSON output ready for downstream nodes (JsonTransform, DB insert, Webhook forward).
- **Positive**: Prevents infinite loops via deterministic `max_pages` and customizable break conditions.
- **Negative**: High page counts (>100) must be handled carefully to avoid memory exhaustion; guarded by `max_pages` ceiling.
