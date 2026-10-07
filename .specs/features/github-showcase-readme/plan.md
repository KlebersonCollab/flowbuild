# Feature Plan: GitHub Showcase README & Visual Documentation (ADR 0016)

## 1. Executive Summary
Produce a showcase-grade `README.md` for GitHub publication with comprehensive technical diagrams, features overview, quickstart instructions, and real screenshots captured directly from the running FlowBuild application in `docs/screenshots/`.

## 2. Architecture & Design Alignment
- **Screenshot Automation**: Node.js script using `puppeteer-core` connected to system Chrome (`C:\Program Files\Google\Chrome\Application\chrome.exe`), taking 1080p high-DPI screenshots of:
  - `docs/screenshots/canvas-hero.png`: The visual builder canvas with connected DAG workflow.
  - `docs/screenshots/flows-manager-worktree.png`: The Flows Manager modal with Worktree folder hierarchy and webhook auth.
  - `docs/screenshots/execution-drawer-telemetry.png`: Execution Drawer with live telemetry and SSE event streaming.
  - `docs/screenshots/variables-modal.png`: Environment-aware 3D variables manager modal.
- **Canonical README.md**:
  - Hero header with project description and badges.
  - Visual showcase carousel / screenshots.
  - Key Features & Capabilities mapped to ADRs.
  - System Architecture with Mermaid diagram.
  - Builtin Component Library catalog.
  - Getting Started (Backend via `uv`, Frontend via `npm`).
  - Testing & Quality Sensor Suite (71 Pytest + 71 Vitest).
  - License and Author.

## 3. Risks & Non-Regression
- Ephemeral servers started for screenshot generation must be cleanly shut down.
- Image assets must be crisp, high-resolution, and lightweight (< 600KB each).
