# ADR 0032: Showcase Workflow Templates for Modern Data, Storage, Messaging and Flow Control Components

## Status
Accepted

## Context
FlowBuild has gained a rich library of specialized enterprise components:
1. **Messaging & Notifications**: Telegram Bot API (`TelegramWebhookComponent`), SMTP Email delivery (`EmailNotificationComponent`), Slack (`SlackWebhookComponent`), Discord (`DiscordWebhookComponent`).
2. **Data Transformation**: Record restructuring (`DataMapperComponent`), Collections aggregation & metrics (`DataAggregatorComponent`), RFC 4180 parsing/serialization (`CsvParserComponent`), Filtering (`DataFilterComponent`).
3. **Database & Storage**: Parameterized SQL queries via SQLAlchemy (`DatabaseQueryComponent`), Isolated persistent key-value store & atomic counters (`KeyValueStoreComponent`).
4. **Flow Control & Reliability**: Collection batching (`LoopIteratorComponent`), Error boundary fallback routing (`TryCatchComponent`), Multi-branch routing (`SwitchNodeComponent`), Non-blocking sleep (`DelayComponent`).

To enable users to immediately understand and harness the full potential of these new native components, the visual canvas template library in `flowStore.ts` and `TopNav.vue` must be expanded with realistic, production-grade workflows showcasing these capabilities.

## Decision
1. **Introduce 3 New Showcase Templates**:
   - `database_csv_export_flow`: `CronTriggerComponent` → `DatabaseQueryComponent` → `CsvParserComponent` → `EmailNotificationComponent`. Demonstrates periodic SQL queries, conversion to RFC 4180 CSV, and automated transactional email dispatch.
   - `batch_kv_discord_flow`: `ManualTriggerComponent` → `LoopIteratorComponent` → `KeyValueStoreComponent` → `DiscordWebhookComponent`. Demonstrates collection batching, stateful execution with persistent atomic counters in Key-Value Store, and rich Embed alerts in Discord.
   - `resilient_try_catch_telegram_flow`: `WebhookTriggerComponent` → `DataMapperComponent` → `TryCatchComponent` → (`success_branch` to `JsonTransformComponent` vs `error_branch` to `TelegramWebhookComponent`). Demonstrates declarative record mapping, error boundary encapsulation, fallback values, and real-time Telegram bot incident alerts.
2. **Reorganize Templates Menu in `TopNav.vue`**:
   Categorize into 4 clear thematic sections:
   - *Básicos & Conectividade* (HTTP, Python Script, Webhook Lead)
   - *Lógica & Controle de Fluxo* (IF/Condition, Switch Router, Delay Polling, Try/Catch Resiliente)
   - *Dados, Filtros & Transformação* (Data Filter & Slack, API Paginada, ETL Completo)
   - *Banco de Dados, Lotes & Mensageria* (Exportação SQL para CSV & Email, Processamento em Lote com KV & Discord)
3. **Type & Store Safety**:
   - Extend `TemplateType` union in `flowStore.ts` to include `'database_csv_export_flow'`, `'batch_kv_discord_flow'`, and `'resilient_try_catch_telegram_flow'`.
   - Ensure complete node positioning, port-level handle wiring (`sourceHandle`, `targetHandle`), default input values, and DAG validity.

## Consequences
- **Positive**: Users have immediate 1-click access to complex, real-world workflow architectures without manually configuring ports and schema inputs.
- **Positive**: Every native component in Clusters 1, 2, 3, and 4 is prominently highlighted in the UI.
- **Negative / Constraints**: Canvas templates must be maintained in sync with any future component input schema changes.
