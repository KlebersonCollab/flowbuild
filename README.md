<div align="center">

# ⚡ FlowBuild

### Visual DAG Workflow Automation Engine & Modern Low-Code Platform
*Construa, execute e promova fluxos de automação com controle visual, telemetria em tempo real e arquitetura empresarial.*

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Vue 3](https://img.shields.io/badge/Vue-3.5+-4FC08D.svg?logo=vue.js&logoColor=white)](https://vuejs.org)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.6+-3178C6.svg?logo=typescript&logoColor=white)](https://www.typescriptlang.org)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-v4-06B6D4.svg?logo=tailwindcss&logoColor=white)](https://tailwindcss.com)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0+-D71F00.svg?logo=sqlalchemy&logoColor=white)](https://www.sqlalchemy.org)
[![Tests](https://img.shields.io/badge/Tests-142%20Passed-brightgreen.svg?logo=pytest&logoColor=white)](#-testes-e-sensores-de-qualidade)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

<br />

[✨ Principais Recursos](#-principais-recursos) •
[📸 Demonstração Visual](#-demonstração-visual) •
[🏗️ Arquitetura](#️-arquitetura) •
[🧩 Catálogo de Nós](#-catálogo-de-nós-built-in) •
[🚀 Como Iniciar](#-como-iniciar) •
[🧪 Testes](#-testes-e-sensores-de-qualidade)

<br />

![FlowBuild Hero Canvas](docs/screenshots/canvas-hero.png)

</div>

---

## 🌟 Visão Geral

O **FlowBuild** é um ecossistema moderno para criação e orquestração de fluxos de trabalho dirigidos por grafos acíclicos dirigidos (**DAGs**). Inspirado no design minimalista e focado em produtividade do [Linear](https://linear.app), o FlowBuild combina a robustez de um backend assíncrono em **Python FastAPI** com uma interface reativa de alta performance em **Vue 3 + TypeScript (@vue-flow)**.

Projetado para automação corporativa, inclui suporte nativo a:
- **Ramificação Condicional (IF / Else)** com anulação em cascata de ramos inativos (*Smart Skipping*).
- **Consumo de APIs Paginadas** com loop seguro em lote e condição de parada dinâmica (*Break Expression*).
- **Triggers com Segurança Configurável** (Webhooks com cabeçalhos de API Key, Bearer Token ou Query Param, além de disparos manuais e agendamento Cron).
- **Gerenciador de Variáveis 3D** (Modo `get`/`set`, Escopos `global`/`flow`, Ambientes `dev`/`qa`/`prd`/`all`) com propagação imediata em memória e persistência em banco.
- **Pipeline de Promoção Multiamplo** (`DEV` → `QA` → `PRD`) com versionamento semântico, gestão de rascunhos e árvore de pastas hierárquica estilo *Worktree*.

---

## 📸 Demonstração Visual

### 1. Canvas Visual de Automação (Hero)
Construa pipelines arrastando nós da barra de ferramentas, conectando portas de entrada/saída tipadas com validação dinâmica de triggers e visualização em minimap.
![FlowBuild Canvas](docs/screenshots/canvas-hero.png)

### 2. Telemetria e Console em Tempo Real (SSE Streaming)
Acompanhe o disparo de nós com medição de latência milissegundo a milissegundo, badges de status (`OK`, `PULADO`, `ERRO`) e logs estruturados transmitidos via Server-Sent Events.
![Live Telemetry](docs/screenshots/execution-drawer-telemetry.png)

### 3. Gerenciador de Fluxos & Worktree de Pastas
Navegue pela árvore hierárquica de pastas (`Financeiro/Cobrança`), visualize a contagem de fluxos, promova versões entre ambientes e copie comandos `cURL` executáveis com um clique.
![Flows Manager](docs/screenshots/flows-manager-worktree.png)

### 4. Gerenciador de Variáveis Tridimensional & Segredos
Administre variáveis criptografadas e abertas separadas por ambiente e escopo, prontas para interpolação dinâmica com a sintaxe `{{NOME_DA_VARIAVEL}}`.
![Variables Manager](docs/screenshots/variables-modal.png)

---

## ✨ Principais Recursos

| Recurso | Descrição | ADR Canônica |
| :--- | :--- | :--- |
| **Execução DAG & Ciclos** | Motor topológico assíncrono com detecção automática de grafos cíclicos e exigência de nó Trigger inicial. | [ADR 0001](.specs/project/ADRs/0001-decoupled-architecture-langflow-pattern.md) / [0006](.specs/project/ADRs/0006-trigger-node-execution-requirement.md) |
| **Ramificação Condicional** | Avaliação segura em Python com roteamento para `true_branch` ou `false_branch` e isolamento gracioso de nós não executados. | [ADR 0009](.specs/project/ADRs/0009-conditional-branching-skip-in-dag-runner.md) |
| **HTTP Paginado com Break** | Paginação assíncrona (`page_number`, `offset_limit`, `cursor`) com limite máximo de segurança e condição de parada. | [ADR 0010](.specs/project/ADRs/0010-paginated-http-loop-with-break.md) |
| **Webhooks Multimétodo Seguros** | Suporte a `POST`, `GET`, `PUT`, `DELETE`, `PATCH` e `ANY`, autenticação via API Key, Bearer Token ou Query Param, e gerador de cURL. | [ADR 0007](.specs/project/ADRs/0007-multi-method-webhook-support.md) / [0011](.specs/project/ADRs/0011-secure-webhook-authentication-modes.md) |
| **Variáveis Tridimensionais** | Nó unificado `Variable` com modos `get` e `set`, escopos `flow` e `global`, seleção de ambiente (`current`, `all`, `dev`, `qa`, `prd`) e persistência DB. | [ADR 0014](.specs/project/ADRs/0014-variable-get-set-mode-and-persistence.md) / [0015](.specs/project/ADRs/0015-variable-environment-scoping.md) |
| **Worktree de Pastas** | Organização com delimitador `/`, busca em tempo real, painel expansível/colapsável e alternador entre Lista e Grid 2-colunas. | [ADR 0012](.specs/project/ADRs/0012-worktree-folder-hierarchy-flows-manager.md) / [0013](.specs/project/ADRs/0013-responsive-flows-manager-viewport-and-grid.md) |
| **Pipeline de Promoção** | Promoção direta com versionamento semântico (`v1.0.0` → `v1.1.0`), rastreamento de linhagem (`source_flow_id`) e ciclo de rascunhos. | [ADR 0004](.specs/project/ADRs/0004-folders-and-multi-environment-promotion-pipeline.md) / [0005](.specs/project/ADRs/0005-reactivity-draft-lifecycle-and-environment-lineage.md) |
| **Persistência Agnostic** | Compatibilidade total com SQLite em modo WAL (padrão) e PostgreSQL via SQLAlchemy 2.0. | [ADR 0002](.specs/project/ADRs/0002-sqlite-persistence-execution-history-and-retry.md) / [0003](.specs/project/ADRs/0003-database-agnostic-sqlalchemy-and-variables-system.md) |

---

## 🏗️ Arquitetura

O sistema adota separação estrita entre o cliente de montagem e o motor de execução assíncrono:

```mermaid
flowchart TD
    subgraph Frontend ["Frontend (Vue 3 + TypeScript)"]
        UI["Canvas Vue Flow (@vue-flow/core)"]
        Inspector["Node Inspector & Parâmetros"]
        Drawer["Execution Drawer (Console SSE)"]
        Modals["Worktree & Modal de Variáveis"]
    end

    subgraph Transport ["Camada de Transporte"]
        REST["REST API (/api/v1/...)"]
        SSE["Server-Sent Events Stream (/execute/stream)"]
    end

    subgraph Backend ["Backend Engine (FastAPI)"]
        Builder["DAGBuilder & Ordenação Topológica"]
        Runner["FlowRunner & Executor Assíncrono"]
        Scheduler["CronSchedulerService (croniter)"]
        Registry["ComponentRegistry (Schemas Dinâmicos)"]
    end

    subgraph Storage ["Camada de Persistência (SQLAlchemy 2.0)"]
        DB[(SQLite / PostgreSQL)]
        Vars[Tabela de Variáveis]
        Execs[Histórico de Execuções]
        Flows[Tabela de Fluxos & Linhagem]
    end

    UI -->|Payload JSON| REST
    REST --> Backend
    Runner -->|Eventos em Tempo Real| SSE
    SSE --> Drawer
    Backend --> Storage
    UI <--> Inspector
```

---

## 🧩 Catálogo de Nós Built-in

| Nó | Categoria | Descrição | Entradas Principais | Saídas |
| :--- | :--- | :--- | :--- | :--- |
| **Manual Trigger** | `Triggers` | Disparo manual imediato a partir do painel ou API. | `initial_payload` (dict) | `data` |
| **Webhook Trigger** | `Triggers` | Endpoint HTTP público/seguro com suporte a múltiplos métodos. | `path`, `method`, `auth_mode`, `auth_header_name`, `secret_token` | `payload`, `headers`, `query_params` |
| **Schedule / Cron** | `Triggers` | Agendador de repetição baseado em expressão cron. | `cron_expression`, `timezone` | `timestamp`, `execution_id` |
| **HTTP Request** | `Actions` | Requisição HTTP assíncrona com timeout e headers. | `url`, `method`, `headers`, `body` | `status_code`, `response`, `headers` |
| **Paginated HTTP Client** | `Actions` | Loop de paginação com condição de break e extração. | `base_url`, `pagination_type`, `break_condition`, `max_pages` | `all_items`, `total_items`, `pages_fetched` |
| **Python Script** | `Actions` | Execução isolada de código Python personalizado. | `code`, `input_data` | `result` |
| **JSON Transform** | `Transform` | Mapeamento e transformação de payloads estruturados. | `input_json`, `expression` | `output` |
| **IF Condition** | `Logic` | Avaliação de expressão booleana com bifurcação de fluxo. | `input_data`, `expression` | `true_branch`, `false_branch`, `result` |
| **Variable** | `Variables` | Leitura (`get`) ou escrita e persistência (`set`) tridimensional. | `mode`, `variable_name`, `value`, `scope`, `environment`, `persist` | `value`, `variable_name`, `success` |

---

## 🚀 Como Iniciar

### Pré-requisitos
- **Python 3.12+** (recomendado gerenciador [`uv`](https://docs.astral.sh/uv/))
- **Node.js 20+** e **npm**

### 1. Clonar o Repositório
```bash
git clone https://github.com/KlebersonCollab/flowbuild.git
cd flowbuild
```

### 2. Configurar e Iniciar o Backend
```bash
cd backend

# Instalar dependências automaticamente com o uv
uv sync

# Iniciar servidor da API FastAPI
uv run python -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 --reload
```
> O backend estará disponível em `http://localhost:8000` e a documentação Swagger interativa em `http://localhost:8000/docs`.

### 3. Configurar e Iniciar o Frontend
Em outro terminal:
```bash
cd frontend

# Instalar dependências
npm install

# Iniciar servidor de desenvolvimento Vite
npm run dev
```
> Acesse a interface visual completa em `http://localhost:5173`.

---

## ⚙️ Variáveis de Ambiente

O FlowBuild utiliza SQLite por padrão (`flowbuild.db`), mas está pronto para produção com PostgreSQL:

| Variável | Padrão | Descrição |
| :--- | :--- | :--- |
| `DATABASE_URL` | `sqlite:///flowbuild.db` | URL de conexão SQLAlchemy (ex: `postgresql://user:pass@host:5432/flowbuild`). |
| `FLOWBUILD_ENV` | `dev` | Ambiente da instância (`dev`, `qa`, `prd`). |
| `FLOWBUILD_PORT` | `8000` | Porta TCP do serviço backend. |

---

## 🧪 Testes e Sensores de Qualidade

O projeto adota o ciclo **Spec Driven Development (SDD)** rigoroso, com 100% dos testes unitários e de integração passando:

```bash
# Executar suíte de testes do Backend (71 testes)
uv run --project backend pytest

# Executar suíte de testes do Frontend (71 testes)
cd frontend && npm test -- --run

# Build de produção do Frontend (TypeScript + Vite)
cd frontend && npm run build

# Validador de integridade e conformidade de especificações SDD
node .agents/scripts/verify-sdd-integrity.js
```

---

## 📜 Histórico Arquitetural (ADRs)

Todas as decisões arquiteturais seguem o padrão formal de Arquitetura Baseada em Decisões (ADR):

- [ADR 0001: Decoupled Architecture & Langflow Pattern](.specs/project/ADRs/0001-decoupled-architecture-langflow-pattern.md)
- [ADR 0002: SQLite Persistence, Execution History and Retry](.specs/project/ADRs/0002-sqlite-persistence-execution-history-and-retry.md)
- [ADR 0003: Database Agnostic SQLAlchemy & Variables System](.specs/project/ADRs/0003-database-agnostic-sqlalchemy-and-variables-system.md)
- [ADR 0004: Folders & Multi-Environment Promotion Pipeline](.specs/project/ADRs/0004-folders-and-multi-environment-promotion-pipeline.md)
- [ADR 0005: Reactivity, Draft Lifecycle and Environment Lineage](.specs/project/ADRs/0005-reactivity-draft-lifecycle-and-environment-lineage.md)
- [ADR 0006: Trigger Node Execution Requirement](.specs/project/ADRs/0006-trigger-node-execution-requirement.md)
- [ADR 0007: Multi-Method Webhook Support](.specs/project/ADRs/0007-multi-method-webhook-support.md)
- [ADR 0008: Modern Toast Notification System](.specs/project/ADRs/0008-modern-toast-notification-system.md)
- [ADR 0009: Conditional Branch Skipping in DAG Runner](.specs/project/ADRs/0009-conditional-branching-skip-in-dag-runner.md)
- [ADR 0010: Paginated HTTP Client with Loop & Break](.specs/project/ADRs/0010-paginated-http-loop-with-break.md)
- [ADR 0011: Secure Webhook Authentication Modes](.specs/project/ADRs/0011-secure-webhook-authentication-modes.md)
- [ADR 0012: Worktree Folder Hierarchy in Flows Manager](.specs/project/ADRs/0012-worktree-folder-hierarchy-flows-manager.md)
- [ADR 0013: Responsive Flows Manager Viewport & Grid Layout](.specs/project/ADRs/0013-responsive-flows-manager-viewport-and-grid.md)
- [ADR 0014: Variable Get/Set Mode Selection & Persistence](.specs/project/ADRs/0014-variable-get-set-mode-and-persistence.md)
- [ADR 0015: Variable Environment Scoping & Target Selection](.specs/project/ADRs/0015-variable-environment-scoping.md)
- [ADR 0016: Canonical GitHub Showcase README & Visual Docs](.specs/project/ADRs/0016-canonical-readme-and-visual-showcase.md)

---

## 📄 Licença

Distribuído sob a licença **MIT**. Consulte `LICENSE` para mais informações.
