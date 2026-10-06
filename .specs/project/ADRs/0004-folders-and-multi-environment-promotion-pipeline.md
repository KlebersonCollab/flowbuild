# ADR 0004: Folders Organization and Multi-Environment Promotion Pipeline (DEV -> QA -> PRD)

## Status
Accepted

## Context
As automation projects scale, users need:
1. **Flows Grouping by Folders / Projects**: Ability to organize multiple workflows into logical folders (e.g., "Financeiro", "E-Commerce", "Notificações") to prevent clutter.
2. **Multi-Environment Promotion Pipeline**:
   - A structured software release lifecycle: **DEV (Desenvolvimento)** -> **QA (Homologação / Testes)** -> **PRD (Produção)**.
   - Workflows developed in DEV must be promoted to QA for testing, and once approved, promoted to PRD.
   - When a workflow is promoted, its structural logic (nodes, handles, edges) is replicated as a frozen/versioned artifact (`v1.0.0`, `v1.1.0`), but when executed in QA or PRD, it must automatically bind to that environment's specific variables (e.g., DEV uses `https://dev-api.internal`, QA uses `https://qa-api.internal`, PRD uses `https://api.company.com`).

## Decision

1. **Folder Organization**:
   - Add `folder: str` column to `flows` table in `backend/app/db.py` (default: `"Geral"`).
   - In `FlowModel` and `FlowRecord`, expose `folder: str = "Geral"`.
   - Frontend `FlowsModal.vue` and `flowStore.ts` support creating folders, assigning flows to folders, and filtering by folder.

2. **Canonical Environments (DEV, QA, PRD) & Versioning**:
   - Add `environment: str` column to `flows` table (values: `'dev'`, `'qa'`, `'prd'`, default `'dev'`).
   - Add `version: str` column to `flows` table (default: `'v1.0.0'`).
   - Add `source_flow_id: str | None` to track parent flow lineage across promotions.
   - TopNav global environment selector (`DEV`, `QA`, `PRD`) with visual color-coded badges (Emerald for DEV, Amber for QA, Indigo for PRD).

3. **Multi-Environment Variables Resolution**:
   - Add `environment: str` column to `variables` table (values: `'dev'`, `'qa'`, `'prd'`, `'all'`, default `'all'`).
   - Update `DatabaseManager.get_all_resolved_variables(flow_id, environment)` with strict 4-tier resolution hierarchy:
     1. Local Flow Variable matching current `environment`.
     2. Local Flow Variable configured for `'all'` environments.
     3. Global Variable matching current `environment`.
     4. Global Variable configured for `'all'` environments.
   - FlowRunner receives current `environment` and injects exact environment variables into template strings `{{VAR}}`.

4. **Promotion Pipeline API & Engine**:
   - Endpoint `POST /api/v1/flows/{flow_id}/promote`:
     - Payload: `{"target_environment": "qa" | "prd", "version": "v1.1.0", "notes": str}`.
     - Creates or updates the target environment flow record with the promoted structure.
     - Logs promotion event in audit history.

5. **Frontend Management Interface**:
   - TopNav displays current Environment Switcher (`DEV`, `QA`, `PRD`).
   - `FlowsModal.vue` organizes flows by Folders with promotion action buttons ("Promover para QA", "Promover para PRD").
   - `VariablesModal.vue` includes Environment filter/badges (`DEV`, `QA`, `PRD`, `TODOS`) allowing developers to configure distinct credentials per environment.

## Consequences
- **Positive**:
  - Enterprise-grade CI/CD and release governance for workflows.
  - Zero accidental production executions during development.
  - Clean credentials isolation: no DEV credentials leaked to PRD and vice versa.
  - Intuitive navigation of flows by project/folder.
- **Negative / Considerations**:
  - Database schema migration for existing SQLite `flows` and `variables` tables handled automatically via SQLAlchemy inspection / default columns.
