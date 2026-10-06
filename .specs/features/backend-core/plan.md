# Plan: Backend Core & Decoupled Execution Engine

## 1. Problem Statement & Motivation
To build an automation workflow builder as decoupled as Langflow, we need an independent Python runtime capable of:
1. Defining self-describing automation components with rich typed inputs and outputs.
2. Generating a standard JSON Schema catalog of all registered components so the frontend never hardcodes node shapes.
3. Constructing and validating Directed Acyclic Graphs (DAGs), ensuring cycle-free topological ordering.
4. Executing workflows asynchronously (`asyncio`) with data passing, error handling, and event streaming.
5. Operating headlessly via REST API and Webhooks.

## 2. Scope & Boundaries
- **In Scope**:
  - Python project initialization using `uv` with `pyproject.toml`.
  - Core component classes: `BaseComponent`, typed `Input` hierarchy, `Output` descriptor.
  - Component registry with dynamic discovery and JSON schema export.
  - Core DAG engine: graph model, topological sort, cycle detection, async execution runner.
  - Initial set of automation components: `ManualTrigger`, `HttpRequest`, `PythonScript`, `JsonTransform`.
  - FastAPI application with REST endpoints for health, components registry, flow validation, and flow execution.
  - Automated test suite with `pytest` and `pytest-asyncio`.
- **Out of Scope**:
  - Persistent relational database storage (flows will be validated and executed in-memory / via payload for this milestone).
  - Distributed Celery/Redis queue workers (in-process `asyncio` engine is sufficient for core).
  - Frontend visual UI implementation (handled in Milestone 2).

## 3. High-Level Approach
1. Initialize the `backend/` directory using `uv init --app backend` and install FastAPI, Uvicorn, Pydantic, Httpx, and Pytest.
2. Build the domain models (`Flow`, `Node`, `Edge`, `ExecutionContext`).
3. Build the component descriptor system and registry.
4. Implement Kahn's algorithm for topological sorting and cycle detection.
5. Implement the asynchronous execution runner that maps node dependencies, executes outputs, and handles telemetry.
6. Expose the FastAPI endpoints and test all components and execution engine with 100% test pass rate.

## 4. Dependencies & Prerequisites
- Python 3.12+ managed by `uv`.
- Libraries: `fastapi`, `uvicorn`, `pydantic>=2.0`, `httpx`, `pytest`, `pytest-asyncio`.

## 5. Architectural Decision Records (ADRs)
- [ADR 0001: Decoupled Architecture Inspired by Langflow](file:///F:/Projetos/flowbuild/.specs/project/ADRs/0001-decoupled-architecture-langflow-pattern.md)
