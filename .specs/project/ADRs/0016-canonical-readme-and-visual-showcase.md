# ADR 0016: Canonical GitHub Showcase README and Visual Documentation

## Status
Accepted

## Date
2026-10-07

## Context
FlowBuild has reached a comprehensive level of maturity with 15 accepted ADRs, including:
- Decoupled FastAPI + Vue 3 architecture
- DAG execution engine with conditional branching (skip inactive branches), paginated HTTP loops with break conditions, multi-method secure webhook triggers, and mandatory initial triggers
- 3-dimensional variables system (Mode: get/set, Scope: flow/global, Environment: current/all/dev/qa/prd) with SQLite/PostgreSQL persistence
- Modern frontend UX conforming to Linear dark tokens (`DESIGN.md`), with Worktree folder hierarchy, responsive modal viewports, list/grid view switchers, and real-time execution drawer streaming SSE telemetry

To publish the repository to GitHub with maximum impact, the project requires a production-grade, aesthetically stunning `README.md` containing clear badges, live architecture flowcharts, comprehensive feature showcases, quickstart instructions, and real 1080p screenshots captured directly from the live running application.

## Decision
1. **Visual Documentation Directory**:
   - Store all high-resolution screenshots in `docs/screenshots/`:
     - `canvas-hero.png`: The main FlowBuild canvas with nodes and connections.
     - `flows-manager-worktree.png`: The Flows Manager modal showing the Worktree folder hierarchy, multi-method webhooks, and cURL generation.
     - `execution-drawer-telemetry.png`: Live execution drawer displaying real-time SSE streaming logs, duration metrics, and node outputs.
     - `variables-modal.png`: The 3-dimensional variables management modal.
2. **Canonical README Structure**:
   - Linear dark styling aesthetics, tech badges, and concise tagline.
   - Live Architecture diagram using Mermaid.
   - Key Features breakdown with direct links to corresponding ADRs.
   - Component Ecosystem catalog.
   - Quickstart Guide (uv for Python backend, npm for Vue frontend).
   - Environment Promotion Pipeline & Variables System explanation.
   - Automated Test Suite & Quality Sensors summary.

## Consequences
- **Positive**: Provides a professional, open-source-ready presentation for GitHub stars, contributors, and enterprise adopters.
- **Maintenance**: Screenshots can be regenerated programmatically whenever UI changes occur.
