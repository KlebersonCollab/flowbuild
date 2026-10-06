# Feature Plan: Folders Organization & Multi-Environment Promotion Pipeline (DEV -> QA -> PRD)

## 1. Executive Summary
Empower FlowBuild users with structured project governance by introducing **Folder-based Flow Organization** and an enterprise-grade **Multi-Environment Promotion Pipeline (DEV -> QA -> PRD)**. Enable workflows to be developed in DEV, promoted to QA for homologation with version snapshots (`v1.0.0`, `v1.1.0`), and promoted to PRD, with variables dynamically bound to each specific environment (`dev`, `qa`, `prd`, `all`).

## 2. Problem Statement
1. All flows currently exist in a flat list without folder or project grouping, making navigation difficult in multi-flow projects.
2. There is no concept of environment progression: a developer testing a workflow might accidentally execute against production endpoints or credentials.
3. Variables are only scoped by flow/global, but in real-world automation, an API host or secret differs between Development, Staging/QA, and Production. Users need environment-bound variables and automated variable switching when promoting flows.

## 3. High-Level Scope
- **Folders / Projects Organization**:
  - Support `folder` attribute across flows (defaulting to `"Geral"`).
  - Folder-based grouping and filtering in `FlowsModal.vue`.
  - Folder creation and flow folder assignment in the UI.
- **Canonical Environments & Promotion Engine**:
  - Support `environment` (`'dev'`, `'qa'`, `'prd'`) and `version` (`'v1.0.0'`) in flows.
  - Endpoint `POST /api/v1/flows/{id}/promote` replicating structure to target environment.
  - Global TopNav Environment Switcher (`DEV`, `QA`, `PRD`) with color-coded badges.
- **Multi-Environment Variables Resolution**:
  - Add `environment` column to `variables` (`'dev'`, `'qa'`, `'prd'`, `'all'`).
  - 4-tier resolution hierarchy in `DatabaseManager` and `FlowRunner`.
  - Environment badges and filtering in `VariablesModal.vue`.
- **Sensors & Verification**:
  - Unit tests for folder grouping, promotion API, and environment variable resolution.
  - Vitest tests for store and modal environment switching.
