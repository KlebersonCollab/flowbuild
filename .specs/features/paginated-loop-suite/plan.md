# Feature Plan: Paginated HTTP Client with Loop and Break Condition

## 1. Problem Statement
Workflows often need to ingest data from REST APIs that paginate their output across multiple pages or batches.
Because FlowBuild is a DAG engine, visual feedback cycles on the canvas are forbidden to prevent graph cycles.
Users need a first-class component that executes an internal asynchronous pagination loop, supports standard pagination protocols (page numbers, offset/limit, cursors), evaluates an optional break condition per page, and returns all consolidated records in a single payload.

## 2. Goals & Success Criteria
- Provide `PaginatedHttpComponent` with support for `page_number`, `offset_limit`, and `cursor` modes.
- Support extraction of records via `items_path` and `cursor_path`.
- Support early exit via customizable Python `break_condition` expression.
- Enforce loop termination safeguards via `max_pages`.
- Emit outputs: `all_items`, `total_items`, `pages_fetched`, `last_page`, and `summary`.
- Provide a pre-configured template in the frontend canvas (`paginated_api_flow`).
- Maintain 100% test pass rate with full unit and integration coverage.

## 3. Scope Boundaries
- **In Scope**:
  - `PaginatedHttpComponent` in `actions.py`.
  - Mocked and real HTTP pagination loop handling with httpx.
  - Break conditions: custom Python expression + automatic empty-items and missing-cursor break.
  - Template in `flowStore.ts` and `TopNav.vue`.
  - Comprehensive Pytest and Vitest test suites.
- **Out of Scope**:
  - Canvas graph cyclic edges (DAG architecture remains strictly acyclic).
  - Background distributed scraping jobs (Milestone 4+).
