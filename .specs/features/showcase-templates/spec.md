# Feature Specification: Showcase Workflow Templates Expansion (ADR 0032)

## Acceptance Criteria (BDD)

### Scenario 1: Loading Database CSV Export Template
- **Given** an active FlowBuild canvas session
- **When** the user invokes `flowStore.loadTemplate('database_csv_export_flow')`
- **Then** `flowStore.flowId` is `'flow-db-csv-export'`
- **And** the workflow contains `CronTriggerComponent`, `DatabaseQueryComponent`, `CsvParserComponent`, and `EmailNotificationComponent`
- **And** all nodes are wired with valid edge source and target handles
- **And** `flowStore.hasTriggerNode()` returns `true`

### Scenario 2: Loading Batch Processing KV Discord Template
- **Given** an active FlowBuild canvas session
- **When** the user invokes `flowStore.loadTemplate('batch_kv_discord_flow')`
- **Then** `flowStore.flowId` is `'flow-batch-kv-discord'`
- **And** the workflow contains `ManualTriggerComponent`, `LoopIteratorComponent`, `KeyValueStoreComponent`, and `DiscordWebhookComponent`
- **And** `KeyValueStoreComponent` has operation `'increment'` and namespace `'billing'`
- **And** `flowStore.hasTriggerNode()` returns `true`

### Scenario 3: Loading Resilient Try/Catch Telegram Template
- **Given** an active FlowBuild canvas session
- **When** the user invokes `flowStore.loadTemplate('resilient_try_catch_telegram_flow')`
- **Then** `flowStore.flowId` is `'flow-resilient-try-catch-telegram'`
- **And** the workflow contains `WebhookTriggerComponent`, `DataMapperComponent`, `TryCatchComponent`, `JsonTransformComponent`, and `TelegramWebhookComponent`
- **And** `TryCatchComponent` connects `success_branch` to `JsonTransformComponent` and `error_branch` to `TelegramWebhookComponent`
- **And** `flowStore.hasTriggerNode()` returns `true`

### Scenario 4: TopNav Dropdown Navigation
- **Given** the TopNav component mounted in Vue
- **When** the user opens the templates dropdown
- **Then** all 4 semantic sections are rendered: "Básicos & Conectividade", "Lógica & Controle de Fluxo", "Dados, Filtros & Transformação", and "Banco de Dados, Lotes & Mensageria"
- **And** clicking any template emits or calls `flowStore.loadTemplate` with the appropriate template identifier.
