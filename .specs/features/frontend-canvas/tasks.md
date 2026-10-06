# Task List: Frontend Canvas & Dynamic Visual Builder

## Sequence Guidelines (MetaGPT SOP)
- **Strict Sequential Order**: Tasks must be executed top-to-bottom without reordering or cherry-picking.
- **Atomic File Boundaries**: Each task must modify at most 1–3 specific target files.
- **Decoupled Test Setup**: Test definition / scaffolding tasks (`Type: test`) MUST precede implementation tasks (`Type: feat`).
- **Sensor Evidence Gate**: Mark complete `[x]` ONLY after passing build, lint, and test sensors with recorded evidence.

## Implementation Tasks

| Status | ID | Type | Description | Target Files | Dependencies | Evidence |
|---|---|---|---|---|---|---|
| [ ] | TASK-01 | test | Scaffold frontend Vite Vue 3 TypeScript project and configure Vitest test runner | `frontend/package.json`, `frontend/vite.config.ts` | None | |
| [ ] | TASK-02 | test | Define test suite for domain types, flow serialization, and Pinia stores | `frontend/tests/stores.test.ts` | TASK-01 | |
| [ ] | TASK-03 | feat | Implement TypeScript interfaces and Pinia stores (flowStore, registryStore, executionStore) | `frontend/src/types/flow.ts`, `frontend/src/stores/flowStore.ts`, `frontend/src/stores/executionStore.ts` | TASK-02 | |
| [ ] | TASK-04 | feat | Configure Tailwind CSS with Linear Design System tokens from DESIGN.md | `frontend/tailwind.config.js`, `frontend/src/assets/main.css` | TASK-03 | |
| [ ] | TASK-05 | test | Define test suite for dynamic node component and schema-driven inspector rendering | `frontend/tests/components.test.ts` | TASK-04 | |
| [ ] | TASK-06 | feat | Implement Universal CustomNode component with dynamic handles and status indicators | `frontend/src/components/CustomNode.vue` | `TASK-05` | |
| [ ] | TASK-07 | feat | Implement schema-driven NodeInspector panel for dynamic form controls | `frontend/src/components/NodeInspector.vue` | TASK-06 | |
| [ ] | TASK-08 | feat | Implement ComponentPalette sidebar and TopNav bar with Run and Export buttons | `frontend/src/components/ComponentPalette.vue`, `frontend/src/components/TopNav.vue` | TASK-07 | |
| [ ] | TASK-09 | feat | Implement FlowCanvas with @vue-flow/core, drag-and-drop, and SSE execution streamer | `frontend/src/components/FlowCanvas.vue`, `frontend/src/App.vue` | TASK-08 | |
| [ ] | TASK-10 | review | Audit acceptance criteria, run TypeScript typecheck, Vitest suite, and SDD integrity sensor | `frontend/`, `.specs/` | TASK-09 | |

## Schema Dictionary
- **Status**: `[ ]` (Pending) | `[x]` (Verified Complete).
- **ID**: `TASK-01`, `TASK-02`, etc.
- **Type**: `test` | `feat` | `fix` | `refactor` | `docs` | `rules` | `skill` | `review`.
- **Target Files**: Concrete comma-separated file paths (relative to workspace root).
- **Dependencies**: Comma-separated list of preceding task IDs or `None`.
- **Evidence**: Commit hash (`git rev-parse --short HEAD`) + sensor output snippet.
