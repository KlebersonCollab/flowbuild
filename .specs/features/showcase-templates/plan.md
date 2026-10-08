# Feature Plan: Showcase Workflow Templates Expansion (ADR 0032)

## Executive Summary
Expand the workflow template library to provide first-class canvas demonstrations of the newly built clusters: Database SQL Query, CSV Parser, Key-Value Store, Loop Iterator, Try/Catch, Telegram, and Email components. Reorganize the TopNav dropdown menu into 4 thematic sections for intuitive navigation.

## Scope & Target Deliverables
1. **Templates in `flowStore.ts`**:
   - `database_csv_export_flow`: CronTrigger -> DatabaseQuery -> CsvParser -> EmailNotification.
   - `batch_kv_discord_flow`: ManualTrigger -> LoopIterator -> KeyValueStore -> DiscordWebhook.
   - `resilient_try_catch_telegram_flow`: WebhookTrigger -> DataMapper -> TryCatch -> (JsonTransform / TelegramWebhook).
2. **TopNav Dropdown UI in `TopNav.vue`**:
   - Reorganize templates into 4 clear sections with Linear dark aesthetic badges, icons, and titles.
3. **Frontend Automated Tests in `frontend/tests/showcase_templates.test.ts`**:
   - Verify all 12 templates load correctly, have valid nodes and edges, valid trigger nodes, and correct node types.
