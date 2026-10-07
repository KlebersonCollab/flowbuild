# Feature Spec: GitHub Showcase README & Visual Documentation (ADR 0016)

## 1. Acceptance Criteria

### US-01: Real Application Screenshots Generation
As a potential user or developer visiting GitHub, I want to see real screenshots of the interface in action.
- **AC-01.1**: Capture `docs/screenshots/canvas-hero.png` showing the node canvas with a multi-step workflow.
- **AC-01.2**: Capture `docs/screenshots/flows-manager-worktree.png` showcasing the split-view Worktree folder hierarchy and webhook cards.
- **AC-01.3**: Capture `docs/screenshots/execution-drawer-telemetry.png` displaying the real-time execution logs and output data.
- **AC-01.4**: Capture `docs/screenshots/variables-modal.png` displaying global and flow-scoped variables across DEV/QA/PRD.

### US-02: Comprehensive Showcase README.md
As an open-source explorer, I want a well-structured, beautiful `README.md` that explains what FlowBuild does, its tech stack, and how to run it.
- **AC-02.1**: Root `README.md` includes modern badges, clear value proposition, and embedded screenshots.
- **AC-02.2**: Includes a Mermaid architecture flowchart showing Frontend, FastAPI Engine, SQLite/PostgreSQL, SSE Stream, and Worker services.
- **AC-02.3**: Contains exact, copy-pasteable installation and run instructions for both backend (`uv`) and frontend (`npm`).
- **AC-02.4**: Details the component catalog, webhook authentication modes, environment promotion pipeline, and testing instructions.
