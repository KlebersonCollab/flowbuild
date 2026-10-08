# Specification: Showcase Workflow Templates (ADR 0021)

## 1. User Stories
- **US-1**: As a user exploring FlowBuild, I want to click pre-configured templates in the top navigation bar, so that I can immediately load rich, operational workflows showcasing logic routing, data filtering, delay nodes, and Slack notifications.
- **US-2**: As a workflow designer, I want the templates menu to be categorized by domain (APIs, Logic/Control Flow, Data & Alerts), so that I can easily discover relevant templates for my use case.
- **US-3**: As a platform developer, I want all templates to preserve valid port connections and node configurations, so that executing the template on the canvas runs successfully without schema errors.

## 2. Business Rules & Invariants
- **BR-1**: All 9 templates (`http_enrich`, `webhook_flow`, `python_pipeline`, `if_condition_flow`, `paginated_api_flow`, `switch_router_flow`, `data_filter_alert_flow`, `delay_polling_flow`, `etl_pagination_filter_flow`) must produce a valid `FlowModel` with at least one trigger node.
- **BR-2**: All template edges must reference existing node IDs and appropriate source/target handles.
- **BR-3**: Existing 5 template keys and behavior must remain 100% backward compatible without breaking existing tests.
- **BR-4**: Selecting any template from `TopNav.vue` must update `flowStore.nodes`, `flowStore.edges`, `flowStore.flowName`, `flowStore.flowDescription`, and close the dropdown.

## 3. Acceptance Criteria (BDD)

### Happy Path (Success Scenarios)
- **AC-1: Loading Switch Router Template**
  - **Given** the user selects `switch_router_flow`
  - **When** `flowStore.loadTemplate('switch_router_flow')` executes
  - **Then** the canvas loads nodes containing `ManualTriggerComponent`, `SwitchNodeComponent`, `SlackWebhookComponent`, and `JsonTransformComponent`, with 4 edges wired from `case_1`, `case_2`, `case_3`, and `default_branch`.

- **AC-2: Loading Data Filter Alert Template**
  - **Given** the user selects `data_filter_alert_flow`
  - **When** `flowStore.loadTemplate('data_filter_alert_flow')` executes
  - **Then** the canvas loads nodes containing `ManualTriggerComponent`, `DataFilterComponent`, `SlackWebhookComponent`, and `JsonTransformComponent`, with edges connecting `filtered_items` to the Slack notification.

- **AC-3: Loading Delay Polling Template**
  - **Given** the user selects `delay_polling_flow`
  - **When** `flowStore.loadTemplate('delay_polling_flow')` executes
  - **Then** the canvas loads nodes containing `ManualTriggerComponent`, `HttpRequestComponent`, `DelayComponent`, and `SlackWebhookComponent`.

- **AC-4: Loading End-to-End ETL Template**
  - **Given** the user selects `etl_pagination_filter_flow`
  - **When** `flowStore.loadTemplate('etl_pagination_filter_flow')` executes
  - **Then** the canvas loads `ManualTriggerComponent`, `PaginatedHttpComponent`, `DataFilterComponent`, `JsonTransformComponent`, and `SlackWebhookComponent` in an end-to-end pipeline.

### Input & Validation Scenarios
- **AC-5: Categorized Navigation Dropdown**
  - **Given** the user opens the "Modelos" dropdown in `TopNav.vue`
  - **When** the menu renders
  - **Then** all 9 templates are displayed grouped under category headers with distinct color badges conforming to `DESIGN.md`.

### Edge Cases & Exceptions (Resilience)
- **AC-6: Fallback Default Template**
  - **Given** an unhandled or invalid template type
  - **When** `loadTemplate` is invoked
  - **Then** it safely falls back to `http_enrich` without throwing runtime exceptions.

## 4. Test Data & Boundary Matrix
| Template Key | Primary Node Types | Target Category |
|---|---|---|
| `http_enrich` | `ManualTrigger`, `HttpRequest`, `JsonTransform` | Básicos |
| `python_pipeline` | `ManualTrigger`, `PythonScript` | Básicos |
| `webhook_flow` | `WebhookTrigger`, `JsonTransform` | Básicos |
| `if_condition_flow` | `ManualTrigger`, `IfCondition`, `JsonTransform` | Lógica & Controle |
| `switch_router_flow` | `ManualTrigger`, `SwitchNode`, `SlackWebhook`, `JsonTransform` | Lógica & Controle |
| `delay_polling_flow` | `ManualTrigger`, `HttpRequest`, `Delay`, `SlackWebhook` | Lógica & Controle |
| `data_filter_alert_flow` | `ManualTrigger`, `DataFilter`, `JsonTransform`, `SlackWebhook` | Dados & Alertas |
| `paginated_api_flow` | `ManualTrigger`, `PaginatedHttp`, `JsonTransform` | Dados & Alertas |
| `etl_pagination_filter_flow` | `ManualTrigger`, `PaginatedHttp`, `DataFilter`, `JsonTransform`, `SlackWebhook` | Dados & Alertas |

## 5. Verification Sensors
| Sensor | Command / Target | Success Threshold |
|---|---|---|
| Frontend Test Suite | `npx vitest run frontend/tests/showcase_templates.test.ts` | 100% pass |
| Full Frontend Suite | `npx vitest run` | 100% pass (all test files) |
| Frontend Build | `npm run build` in `frontend/` | Exit 0, 0 type errors |
| Backend Test Suite | `uv run pytest` in `backend/` | 100% pass |
| SDD Integrity Sensor | `node .agents/scripts/verify-sdd-integrity.js` | 100% pass |
| Spec Drift Sensor | `node .agents/scripts/check-spec-drift.js` | 100% pass |

## 6. UI & Design System Tokens
- Dropdown backgrounds: `#0f1011` with `#23252a` borders.
- Hover states: `#141516` with text `#f7f8f8`.
- Category headers: `text-[10px] font-semibold uppercase tracking-wider text-[#62666d]`.
- Badges: Indigo (`#828fff`), Purple, Cyan, Amber, Emerald, Rose.
