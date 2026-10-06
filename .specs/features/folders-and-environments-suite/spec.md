# Feature Spec: Folders Organization & Multi-Environment Promotion Pipeline (DEV -> QA -> PRD)

## 1. Domain Glossary Alignment
- **Folder / Project**: Logical grouping for multiple related flows (e.g. "Financeiro", "E-Commerce", "Geral").
- **Canonical Environments**: The three standardized software lifecycle environments: `dev` (Development), `qa` (Homologation / Quality Assurance), and `prd` (Production).
- **Promotion Pipeline**: The mechanism that replicates a validated flow definition from a lower environment to a higher environment (`dev` -> `qa` -> `prd`) with version tagging and lineage tracking.
- **Environment-Scoped Variables**: Variables bound to a specific environment (`dev`, `qa`, `prd`) or available across `'all'` environments.

## 2. Business Rules & Invariants
- `BR-1`: A flow promoted from DEV to QA MUST retain its exact node and edge structure while executing against QA environment variables.
- `BR-2`: When resolving variables in environment E for flow F, the resolution hierarchy MUST strictly follow:
  1. Flow-scoped variable for environment E.
  2. Flow-scoped variable for environment `'all'`.
  3. Global variable for environment E.
  4. Global variable for environment `'all'`.
- `BR-3`: Flow promotion is strictly directional: `dev` -> `qa`, and `qa` -> `prd`. Direct promotion from `dev` -> `prd` requires explicit confirmation.
- `BR-4`: Workflows executing in PRD MUST be strictly isolated from DEV credentials and endpoints.

## 3. Acceptance Criteria (BDD)

### AC-1: Folder Organization & Filter
- **Given** flows saved with `folder = "Financeiro"` and `folder = "E-Commerce"`.
- **When** calling `GET /api/v1/flows?folder=Financeiro`.
- **Then** only flows belonging to the "Financeiro" folder are returned.

### AC-2: Multi-Environment Variable Resolution
- **Given** variable `API_HOST = "api.dev.company"` for `environment = "dev"` and `API_HOST = "api.qa.company"` for `environment = "qa"`.
- **When** a flow executes with `environment = "qa"`.
- **Then** template string `https://{{API_HOST}}/users` resolves to `https://api.qa.company/users`.

### AC-3: Flow Promotion API
- **Given** an active flow in DEV with ID `flow-orders` and version `v1.0.0`.
- **When** a promotion request `POST /api/v1/flows/flow-orders/promote` is sent with `{"target_environment": "qa", "version": "v1.1.0"}`.
- **Then** a flow record in QA is created/updated with `environment = "qa"`, `version = "v1.1.0"`, and `source_flow_id = "flow-orders"`.

### AC-4: Frontend TopNav Environment Switcher & Filtering
- **Given** the user selects the "QA" environment in TopNav.
- **When** opening "Meus Fluxos" or running workflows.
- **Then** only flows and variables corresponding to QA are displayed and used for executions.
