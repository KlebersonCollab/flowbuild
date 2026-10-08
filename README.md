<div align="center">

# ⚡ FlowBuild

### Visual DAG Workflow Automation Engine & Modern Low-Code Platform
*Construa, execute e promova fluxos de automação com controle visual, telemetria em tempo real e arquitetura empresarial.*

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Vue 3](https://img.shields.io/badge/Vue-3.5+-4FC08D.svg?logo=vue.js&logoColor=white)](https://vuejs.org)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.6+-3178C6.svg?logo=typescript&logoColor=white)](https://www.typescriptlang.org)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-v4-06B6D4.svg?logo=tailwindcss&logoColor=white)](https://tailwindcss.com)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0+-D71F00.svg?logo=sqlalchemy&logoColor=white)](https://www.sqlalchemy.org)
[![Nodes](https://img.shields.io/badge/Nodes-18%20Built--in-blueviolet.svg)](#-catálogo-de-nós-built-in)
[![Templates](https://img.shields.io/badge/Templates-12%20Showcase-indigo.svg)](#-modelos-de-fluxos-showcase)
[![Tests](https://img.shields.io/badge/Tests-293%20Passed-brightgreen.svg?logo=pytest&logoColor=white)](#-testes-e-sensores-de-qualidade)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

<br />

[✨ Principais Recursos](#-principais-recursos) •
[📸 Demonstração Visual](#-demonstração-visual) •
[🏗️ Arquitetura](#️-arquitetura) •
[🧩 Catálogo de Nós](#-catálogo-de-nós-built-in) •
[📋 Modelos de Fluxos](#-modelos-de-fluxos-showcase) •
[🚀 Como Iniciar](#-como-iniciar) •
[🧪 Testes](#-testes-e-sensores-de-qualidade) •
[📜 Decisões Arquiteturais](#-histórico-arquitetural-adrs)

<br />

![FlowBuild Hero Canvas](docs/screenshots/canvas-hero.png)

</div>

---

## 🌟 Visão Geral

O **FlowBuild** é um ecossistema moderno para criação e orquestração de fluxos de trabalho dirigidos por grafos acíclicos dirigidos (**DAGs**). Inspirado no design minimalista e focado em produtividade do [Linear](https://linear.app), o FlowBuild combina a robustez de um backend assíncrono em **Python FastAPI** com uma interface reativa de alta performance em **Vue 3 + TypeScript (@vue-flow)**.

Projetado para automação empresarial e engenharia de dados, inclui suporte nativo a:
- **Controle de Fluxo & Confiabilidade**: Ramificação condicional (IF / Else), roteamento multi-ramal (`Switch`), pausas assíncronas não-bloqueantes (`Delay`), fatiamento de coleções em lotes (`Loop Iterator`) e encapsulamento de falhas com fallback (`Try / Catch`).
- **Mensageria & Notificações Omnichannel**: Envio automatizado de mensagens para canais do Slack (Incoming Webhooks), Discord (mensagens e Rich Embeds), Telegram Bot API (`sendMessage` com HTML/Markdown) e e-mails corporativos via SMTP (TLS/SSL).
- **Transformação & Manipulação de Dados**: Mapeamento declarativo de campos com dot-notation (`Data Mapper`), agregações matemáticas/estatísticas com particionamento (`Data Aggregator`), parsing e serialização tabular CSV RFC 4180 (`CSV Parser`) e filtragem por operadores de comparação (`Data Filter`).
- **Banco de Dados & Armazenamento de Estado**: Execução de queries SQL parametrizadas via SQLAlchemy 2.0 (`Database Query`) e Key-Value Store persistente para contadores atômicos e cache entre execuções (`Key-Value Store`).
- **Triggers Seguros & Multimétodo**: Webhooks com autenticação configurável (API Key, Bearer Token ou Query Param) para métodos `POST`, `GET`, `PUT`, `DELETE`, `PATCH` e `ANY`, além de disparos manuais e agendamento Cron.
- **Gerenciador de Variáveis Tridimensional**: Modo `get`/`set`, escopos `global`/`flow`, ambientes `dev`/`qa`/`prd`/`all` e interpolação dinâmica com `{{NOME_DA_VARIAVEL}}`.
- **Pipeline de Promoção & Governança**: Promoção semântica (`DEV` → `QA` → `PRD`), controle de rascunhos (*drafts*), árvore de pastas hierárquica estilo *Worktree* e biblioteca nativa com 12 templates prontos.

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
| **Controle de Fluxo & Lógica** | Bifurcação IF / Else com *Smart Skipping*, Switch Node (4 ramais) e pausas não-bloqueantes (`Delay`). | [ADR 0009](.specs/project/ADRs/0009-conditional-branching-skip-in-dag-runner.md) / [0017](.specs/project/ADRs/0017-delay-node-component.md) / [0018](.specs/project/ADRs/0018-switch-node-component-and-branch-skipping.md) |
| **Confiabilidade & Resiliência** | Processador de lotes (`Loop Iterator`) e limites de erro com fallback (`Try / Catch`) sem interrupção do workflow. | [ADR 0030](.specs/project/ADRs/0030-loop-iterator-component.md) / [0031](.specs/project/ADRs/0031-try-catch-component.md) |
| **Mensageria Omnichannel** | Notificações ricas no Slack, Discord (Embeds), Telegram Bot API e envio de e-mails corporativos via SMTP. | [ADR 0020](.specs/project/ADRs/0020-slack-notification-component.md) / [0022](.specs/project/ADRs/0022-discord-notification-component.md) / [0023](.specs/project/ADRs/0023-telegram-notification-component.md) / [0024](.specs/project/ADRs/0024-email-notification-component.md) |
| **Transformação de Dados** | Mapeamento com dot-notation (`Data Mapper`), agregações matemáticas (`Data Aggregator`) e parser CSV RFC 4180. | [ADR 0025](.specs/project/ADRs/0025-data-mapper-component.md) / [0026](.specs/project/ADRs/0026-data-aggregator-component.md) / [0027](.specs/project/ADRs/0027-csv-parser-component.md) |
| **Banco & Armazenamento** | Consultas SQL parametrizadas (`Database Query`) e armazenamento atômico entre execuções (`Key-Value Store`). | [ADR 0028](.specs/project/ADRs/0028-database-query-component.md) / [0029](.specs/project/ADRs/0029-key-value-store-component.md) |
| **HTTP Paginado com Break** | Paginação assíncrona (`page_number`, `offset_limit`, `cursor`) com limite de segurança e condição de parada. | [ADR 0010](.specs/project/ADRs/0010-paginated-http-loop-with-break.md) |
| **Webhooks Multimétodo Seguros** | Suporte a `POST`, `GET`, `PUT`, `DELETE`, `PATCH` e `ANY`, autenticação via API Key, Bearer ou Query, e gerador de cURL. | [ADR 0007](.specs/project/ADRs/0007-multi-method-webhook-support.md) / [0011](.specs/project/ADRs/0011-secure-webhook-authentication-modes.md) |
| **Variáveis Tridimensionais** | Nó unificado `Variable` com modos `get`/`set`, escopos `flow`/`global`, seleção de ambiente e persistência DB. | [ADR 0014](.specs/project/ADRs/0014-variable-get-set-mode-and-persistence.md) / [0015](.specs/project/ADRs/0015-variable-environment-scoping.md) |
| **Worktree de Pastas** | Organização hierárquica `/`, busca em tempo real, painel colapsável e visualização em Lista ou Grid 2-colunas. | [ADR 0012](.specs/project/ADRs/0012-worktree-folder-hierarchy-flows-manager.md) / [0013](.specs/project/ADRs/0013-responsive-flows-manager-viewport-and-grid.md) |
| **Pipeline de Promoção** | Promoção direta com versionamento semântico (`v1.0.0` → `v1.1.0`), linhagem (`source_flow_id`) e ciclo de rascunhos. | [ADR 0004](.specs/project/ADRs/0004-folders-and-multi-environment-promotion-pipeline.md) / [0005](.specs/project/ADRs/0005-reactivity-draft-lifecycle-and-environment-lineage.md) |
| **Biblioteca de Modelos** | 12 templates prontos para uso categorizados em 4 seções temáticas no TopNav do canvas. | [ADR 0021](.specs/project/ADRs/0021-showcase-workflow-templates.md) / [0032](.specs/project/ADRs/0032-showcase-workflow-templates.md) |

---

## 🏗️ Arquitetura

O sistema adota separação estrita entre o cliente de montagem e o motor de execução assíncrono:

```mermaid
flowchart TD
    subgraph Frontend ["Frontend (Vue 3 + TypeScript)"]
        UI["Canvas Vue Flow (@vue-flow/core)"]
        Palette["Component Palette & 18 Nós"]
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
        Runner["FlowRunner (Smart Skipping & Error Boundary)"]
        Scheduler["CronSchedulerService (croniter)"]
        Registry["ComponentRegistry (Schemas Dinâmicos)"]
    end

    subgraph Storage ["Camada de Persistência (SQLAlchemy 2.0)"]
        DB[(SQLite / PostgreSQL)]
        Vars[Tabela de Variáveis]
        KVStore[Tabela Key-Value Store]
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

O FlowBuild possui **18 componentes nativos** divididos em 6 categorias funcionais:

| Nó | Categoria | Ícone & Estilo | Descrição | Entradas Principais | Saídas Principais |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Manual Trigger** | `Triggers` | `Zap` / Amber | Disparo manual imediato via UI ou API. | `initial_payload` (dict) | `data` |
| **Webhook Trigger** | `Triggers` | `Radio` / Cyan | Endpoint HTTP com autenticação segura e múltiplos métodos. | `path`, `method`, `auth_mode`, `auth_header_name`, `secret_token` | `payload`, `headers`, `query_params` |
| **Schedule / Cron** | `Triggers` | `Zap` / Amber | Disparo temporal agendado baseado em expressão cron. | `cron_expression`, `timezone` | `timestamp`, `trigger_info` |
| **HTTP Request** | `Actions` | `Globe` / Blue | Requisição HTTP assíncrona com headers e timeout. | `url`, `method`, `headers`, `body` | `data`, `status_code` |
| **Paginated HTTP Client** | `Actions` | `Repeat` / Emerald | Consumo de APIs paginadas com break condition e agregação. | `url`, `pagination_mode`, `break_condition`, `max_pages` | `all_items`, `total_items`, `pages_fetched` |
| **Python Script** | `Actions` | `Terminal` / Purple | Execução isolada de scripts Python com retorno estruturado. | `code`, `input_data` | `result` |
| **Slack Webhook** | `Actions` | `MessageSquare` / Rose | Alertas formatados com avatar e canal customizados no Slack. | `webhook_url`, `text`, `channel`, `username`, `icon_emoji` | `success`, `status_code` |
| **Discord Webhook** | `Actions` | `MessageCircle` / Blurple | Alertas no Discord com suporte completo a Rich Embeds e cores. | `webhook_url`, `content`, `embed_title`, `embed_color`, `username` | `success`, `status_code` |
| **Telegram Webhook** | `Actions` | `Send` / Sky Blue | Envio de mensagens via Telegram Bot API com HTML/Markdown. | `bot_token`, `chat_id`, `text`, `parse_mode`, `silent` | `success`, `message_id` |
| **Email Notification** | `Actions` | `Mail` / Violet | Envio de e-mails via SMTP assíncrono com STARTTLS/SSL. | `smtp_host`, `smtp_port`, `sender_email`, `recipient_email`, `subject`, `body` | `success`, `recipient` |
| **JSON Transform** | `Transform` | `FileCode` / Emerald | Avaliação de expressões contra payloads JSON estruturados. | `input_data`, `expression` | `output_data` |
| **Data Filter** | `Transform` | `Filter` / Emerald | Filtragem declarativa de coleções com operadores e contadores. | `items`, `field`, `operator`, `value`, `expression` | `filtered_items`, `discarded_items`, `total_filtered` |
| **Data Mapper** | `Transform` | `ArrowRightLeft` / Emerald | Reestruturação declarativa de registros com dot-notation. | `data`, `field_mappings`, `items_path`, `include_unmapped` | `mapped_data`, `total_mapped` |
| **Data Aggregator** | `Transform` | `Calculator` / Emerald | Agregações matemáticas e agrupamento `group_by`. | `items`, `field`, `operation`, `group_by` | `result`, `aggregated_value`, `count` |
| **CSV Parser** | `Transform` | `FileSpreadsheet` / Emerald | Parsing de texto CSV para JSON e geração de CSV RFC 4180. | `input_data`, `mode`, `delimiter`, `has_headers`, `columns` | `parsed_rows`, `csv_text`, `row_count` |
| **Database Query** | `Storage` | `Database` / Teal | Execução de SQL parametrizado via SQLAlchemy (`text`). | `query`, `fetch_mode`, `params`, `database_url` | `rows`, `row_count`, `affected_rows` |
| **Key-Value Store** | `Storage` | `HardDrive` / Teal | Armazenamento de estado persistente e contadores atômicos. | `operation`, `key`, `value`, `amount`, `namespace` | `result`, `value`, `success` |
| **IF Condition** | `Logic` | `Sliders` / Amber | Bifurcação booleana com anulação de ramos inativos. | `input_data`, `expression` | `true_branch`, `false_branch`, `result` |
| **Delay / Sleep** | `Logic` | `Clock` / Amber | Pausa assíncrona não-bloqueante (`asyncio.sleep`) com repasse. | `delay`, `unit`, `input_data` | `data`, `waited_seconds` |
| **Switch / Router** | `Logic` | `GitFork` / Indigo | Roteamento multi-ramal (3 casos + default) com skip seletivo. | `input_data`, `expression`, `case_1_value`, `case_2_value`, `case_3_value` | `case_1`, `case_2`, `case_3`, `default_branch` |
| **Loop Iterator** | `Logic` | `Repeat` / Indigo | Fatiamento de coleções em lotes e métricas de paginação. | `items`, `items_path`, `batch_size`, `batch_index`, `max_batches` | `current_batch`, `batches`, `total_items`, `has_more` |
| **Try / Catch** | `Logic` | `ShieldAlert` / Rose | Encapsulamento de erros a montante com valor de fallback. | `input_data`, `fallback_value`, `catch_upstream_errors`, `error_message` | `success_branch`, `error_branch`, `result`, `has_error` |
| **Variable** | `Variables` | `Sliders` / Indigo | Leitura (`get`) ou escrita (`set`) com escopo 3D e persistência. | `mode`, `variable_name`, `value`, `scope`, `environment`, `persist` | `value`, `variable_name`, `success` |

---

## 📋 Modelos de Fluxos (Showcase)

O FlowBuild traz **12 templates canônicos pré-configurados** acessíveis diretamente pelo menu **Modelos** no cabeçalho do canvas:

### 🔌 1. Fluxos Básicos & APIs
- **HTTP Request & Enriquecimento**: Disparo Manual $\to$ API GitHub $\to$ JSON Transform.
- **Pipeline Python Script**: Disparo Manual $\to$ Execução de script Python isolado com dicionário de retorno.
- **Recepção Webhook Lead**: Webhook Trigger $\to$ Extração e normalização de payload.

### 🔀 2. Lógica & Controle de Fluxo
- **Decisão Condicional (IF / Else)**: Disparo Manual $\to$ IF Condition $\to$ Ramificação em `true_branch` vs `false_branch`.
- **Roteamento Inteligente & Multi-Branch**: Switch Node (4 ramais) roteando pedidos para canais específicos do Slack e filas.
- **Automação com Delay & Polling**: Disparo Manual $\to$ HTTP POST $\to$ Delay 3s $\to$ Alerta Slack.
- **Pipeline Resiliente: Try/Catch & Telegram**: Webhook $\to$ Data Mapper $\to$ Try/Catch com fallback seguro $\to$ Alerta crítico imediato no Telegram Bot se houver falhas.

### 📊 3. Dados & Alertas
- **Filtragem de Dados & Alerta Slack**: Data Filter isolando pedidos VIP (> R$ 1.000) $\to$ Alerta formatado para o time de vendas.
- **API Paginada com Loop & Break**: Ingestão paginada automática com parada por condição dinâmica.
- **ETL Completo (Paginação $\to$ Filtro $\to$ Slack)**: Ingestão de repositórios do GitHub $\to$ Filtro por estrelas $\to$ Transformação em resumo $\to$ Relatório executivo.

### 💾 4. Banco de Dados, Lotes & Mensageria
- **Exportação SQL para CSV & Email**: Agendamento semanal (Cron) $\to$ Query analítica SQL $\to$ Conversão para RFC 4180 CSV tabular $\to$ Disparo transacional por e-mail corporativo.
- **Processamento em Lote com KV & Discord**: Disparo Manual $\to$ Loop Iterator fatiando coleção de transações $\to$ Incremento atômico de contador no Key-Value Store $\to$ Notificação com Embed rico no Discord.

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

O projeto adota o ciclo **Spec Driven Development (SDD)** rigoroso, contando com **293 testes automatizados** passando com 100% de integridade:

```bash
# Executar suíte completa de testes do Backend (157 testes Pytest)
uv run --project backend pytest

# Executar suíte completa de testes do Frontend (136 testes Vitest)
cd frontend && npm test -- --run

# Build de produção do Frontend (TypeScript + Vite)
cd frontend && npm run build

# Sensor de integridade estrutural e de especificações SDD
node .agents/scripts/verify-sdd-integrity.js

# Sensor de drift de especificações (pre-commit)
node .agents/scripts/check-spec-drift.js
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
- [ADR 0017: Delay and Sleep Node Component for Flow Execution](.specs/project/ADRs/0017-delay-node-component.md)
- [ADR 0018: Multi-Branch Switch Routing Component & Generalized Branch Skipping](.specs/project/ADRs/0018-switch-node-component-and-branch-skipping.md)
- [ADR 0019: Declarative Data Filter Component for Collections and Records](.specs/project/ADRs/0019-data-filter-component.md)
- [ADR 0020: Slack Notification & Webhook Messaging Component](.specs/project/ADRs/0020-slack-notification-component.md)
- [ADR 0021: Showcase Workflow Templates for Logic, Data Filtering & Messaging](.specs/project/ADRs/0021-showcase-workflow-templates.md)
- [ADR 0022: Discord Notification & Webhook Messaging Component](.specs/project/ADRs/0022-discord-notification-component.md)
- [ADR 0023: Telegram Notification & Webhook Messaging Component](.specs/project/ADRs/0023-telegram-notification-component.md)
- [ADR 0024: Email Notification Component - SMTP Delivery](.specs/project/ADRs/0024-email-notification-component.md)
- [ADR 0025: Declarative Data Mapper Component for Record Transformation](.specs/project/ADRs/0025-data-mapper-component.md)
- [ADR 0026: Data Aggregator Component for Collection Metrics & Grouping](.specs/project/ADRs/0026-data-aggregator-component.md)
- [ADR 0027: CSV Parser Component for Delimited Data Serialization & Parsing](.specs/project/ADRs/0027-csv-parser-component.md)
- [ADR 0028: Database Query Component for SQL Execution & Storage](.specs/project/ADRs/0028-database-query-component.md)
- [ADR 0029: Key-Value Store Component for Cross-Execution State & Counters](.specs/project/ADRs/0029-key-value-store-component.md)
- [ADR 0030: Loop Iterator Component for Collection Chunking & Batch Processing](.specs/project/ADRs/0030-loop-iterator-component.md)
- [ADR 0031: Try / Catch Component for Error Handling & Resilient Routing](.specs/project/ADRs/0031-try-catch-component.md)
- [ADR 0032: Showcase Workflow Templates for Modern Data, Storage & Messaging](.specs/project/ADRs/0032-showcase-workflow-templates.md)

---

## 📄 Licença

Distribuído sob a licença **MIT**. Consulte `LICENSE` para mais informações.
