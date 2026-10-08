# ADR 0021: Showcase Workflow Templates for Advanced Logic, Data Filtering and Messaging Nodes

## Status
Accepted

## Date
2026-10-07

## Context
Following the implementation of foundational components (`DelayComponent` - ADR 0017, `SwitchNodeComponent` - ADR 0018, `DataFilterComponent` - ADR 0019, and `SlackWebhookComponent` - ADR 0020), FlowBuild now possesses advanced workflow orchestration capabilities including multi-way branch routing, non-blocking asynchronous pauses, declarative collection filtering, and outbound communication webhooks.

However, the existing canvas template catalog only provided basic flows (`http_enrich`, `python_pipeline`, `webhook_flow`, `if_condition_flow`, `paginated_api_flow`), which did not demonstrate these newly introduced components. Users lack pre-built visual examples showing how to compose complex multi-node automations combining routing, delays, filters, and alerts.

## Decision
1. **Expand Canvas Templates Library in `flowStore.ts`**:
   Introduce 4 new production-grade showcase templates while maintaining full backwards compatibility with existing templates:
   - `switch_router_flow` (**Roteamento Inteligente & Multi-Branch**):
     - Demonstrates `SwitchNodeComponent` triage with 4 branches (`case_1`, `case_2`, `case_3`, `default_branch`), cascading skips, and `SlackWebhookComponent` urgent escalation.
   - `data_filter_alert_flow` (**Filtragem de Coleções & Alerta Slack**):
     - Demonstrates `DataFilterComponent` extracting items via `items_path`, filtering records with comparison operators, dual branches (`filtered_items` vs `discarded_items`), count metrics, and Slack delivery.
   - `delay_polling_flow` (**Automação com Delay & Polling Assíncrono**):
     - Demonstrates `DelayComponent` non-blocking timer pauses with visible inline canvas duration controls, sequential API steps, and completion alert.
   - `etl_pagination_filter_flow` (**ETL Completo: Paginação → Filtro → Slack**):
     - End-to-end enterprise scenario: Ingests GitHub/REST API items with `PaginatedHttpComponent`, filters high-priority records with `DataFilterComponent`, formats summary payload with `JsonTransformComponent`, and sends alert with `SlackWebhookComponent`.
2. **Categorized Template Menu in `TopNav.vue`**:
   Group templates visually in the dropdown into three distinct sections:
   - *Fluxos Básicos & APIs*: `http_enrich`, `python_pipeline`, `webhook_flow`
   - *Lógica & Controle de Fluxo*: `if_condition_flow`, `switch_router_flow`, `delay_polling_flow`
   - *Dados, ETL & Notificações*: `data_filter_alert_flow`, `paginated_api_flow`, `etl_pagination_filter_flow`
3. **Type Safety & Backwards Compatibility**:
   - Update `templateType` union signature in `flowStore.ts` to include the new template keys:
     `'http_enrich' | 'webhook_flow' | 'python_pipeline' | 'if_condition_flow' | 'paginated_api_flow' | 'switch_router_flow' | 'data_filter_alert_flow' | 'delay_polling_flow' | 'etl_pagination_filter_flow'`
   - Guarantee all existing template IDs, ports, and node models remain completely unchanged.

## Consequences
- **Positive**: First-time and returning users immediately visualize the advanced architectural power and real-world applicability of FlowBuild.
- **Developer Experience**: One-click exploration of production patterns without manually wiring complex node topologies from scratch.
- **Safety**: Fully backward compatible; zero regressions to existing test suites or saved workflows.
