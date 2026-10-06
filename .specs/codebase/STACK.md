# Technology Stack (FlowBuild)

## 1. Backend Stack (Python)

- **Language & Runtime**: Python 3.11+
- **API Framework**: FastAPI (modern, high-performance async ASGI framework)
- **ASGI Server**: Uvicorn
- **Data Validation & Schemas**: Pydantic v2 (strict type enforcement, JSON schema serialization)
- **Graph & DAG Execution**: Custom asynchronous topological executor with `asyncio` and `collections.defaultdict` (with optional `networkx` graph algorithms)
- **HTTP Client for Actions**: `httpx` (async HTTP client)
- **Package & Environment Management**: `uv` (Astral's high-speed package installer and resolver with `pyproject.toml`)
- **Testing**: `pytest`, `pytest-asyncio`, `pytest-cov`
- **Linter & Code Formatter**: `ruff`

## 2. Frontend Stack (Vue 3 + TypeScript)

- **Framework**: Vue 3 (Composition API with `<script setup>`)
- **Language**: TypeScript 5+ (strict mode enabled)
- **Build Tool / Bundler**: Vite (instant HMR, fast builds)
- **Flow Canvas Engine**: `@vue-flow/core` with `@vue-flow/background` and `@vue-flow/controls`
- **State Management**: Pinia (modular stores: `flowStore`, `registryStore`, `executionStore`)
- **Styling & Design System**: Tailwind CSS v3 configured with tokens from [DESIGN.md](file:///F:/Projetos/flowbuild/DESIGN.md) (Linear dark palette, `#010102` canvas, `#5e6ad2` primary, `#0f1011` surface-1, hairline borders)
- **Icons**: `lucide-vue-next` (crisp, minimal line icons)
- **Testing**: Vitest + `@vue/test-utils`
- **Linter**: ESLint + Prettier

## 3. Communication Protocols

- **REST API**: CRUD for workflows, component registry retrieval, node validation, webhook ingestion.
- **Server-Sent Events (SSE)**: Real-time execution streaming (node progress, logs, outputs, errors).
