# Task List: Frontend Canvas & Dynamic Visual Builder

## Sequence Guidelines (MetaGPT SOP)
- **Strict Sequential Order**: Tasks must be executed top-to-bottom without reordering or cherry-picking.
- **Atomic File Boundaries**: Each task must modify at most 1–3 specific target files.
- **Decoupled Test Setup**: Test definition / scaffolding tasks (`Type: test`) MUST precede implementation tasks (`Type: feat`).
- **Sensor Evidence Gate**: Mark complete `[x]` ONLY after passing build, lint, and test sensors with recorded evidence.

## Implementation Tasks

| Status | ID | Type | Description | Target Files | Dependencies | Evidence |
|---|---|---|---|---|---|---|
| [x] | TASK-01 | test | Scaffold frontend Vite Vue 3 TypeScript project and configure Vitest test runner | `frontend/package.json`, `frontend/vite.config.ts` | None | `df33e83` Vite scaffold + vitest config pass |
| [x] | TASK-02 | test | Define test suite for domain types, flow serialization, and Pinia stores | `frontend/tests/stores.test.ts` | TASK-01 | `9341ff0` stores.test.ts scaffolded |
| [x] | TASK-03 | feat | Implement TypeScript interfaces and Pinia stores (flowStore, registryStore, executionStore) | `frontend/src/types/flow.ts`, `frontend/src/stores/flowStore.ts`, `frontend/src/stores/executionStore.ts` | TASK-02 | `7a44ae9` Pinia stores and types pass |
| [x] | TASK-04 | feat | Configure Tailwind CSS with Linear Design System tokens from DESIGN.md | `frontend/tailwind.config.js`, `frontend/src/assets/main.css` | TASK-03 | `7c327db` Linear tokens and Tailwind configured |
| [x] | TASK-05 | test | Define test suite for dynamic node component and schema-driven inspector rendering | `frontend/tests/components.test.ts` | TASK-04 | `a265137` components.test.ts scaffolded |
| [x] | TASK-06 | feat | Implement Universal CustomNode component with dynamic handles and status indicators | `frontend/src/components/CustomNode.vue` | `TASK-05` | `5e48ed5` CustomNode handles and status pass |
| [x] | TASK-07 | feat | Implement schema-driven NodeInspector panel for dynamic form controls | `frontend/src/components/NodeInspector.vue` | TASK-06 | `5e48ed5` NodeInspector schema forms pass |
| [x] | TASK-08 | feat | Implement ComponentPalette sidebar and TopNav bar with Run and Export buttons | `frontend/src/components/ComponentPalette.vue`, `frontend/src/components/TopNav.vue` | TASK-07 | `85351d3` Palette and TopNav controls pass |
| [x] | TASK-09 | feat | Implement FlowCanvas with @vue-flow/core, drag-and-drop, and SSE execution streamer | `frontend/src/components/FlowCanvas.vue`, `frontend/src/App.vue` | TASK-08 | `84f3062` FlowCanvas and App workspace pass |
| [x] | TASK-10 | review | Audit acceptance criteria, run TypeScript typecheck, Vitest suite, and SDD integrity sensor | `frontend/`, `.specs/` | TASK-09 | `84f3062` typecheck pass, 5/5 vitest pass, build pass, SDD integrity ok |

## Schema Dictionary
- **Status**: `[ ]` (Pending) | `[x]` (Verified Complete).
- **ID**: `TASK-01`, `TASK-02`, etc.
- **Type**: `test` | `feat` | `fix` | `refactor` | `docs` | `rules` | `skill` | `review`.
- **Target Files**: Concrete comma-separated file paths (relative to workspace root).
- **Dependencies**: Comma-separated list of preceding task IDs or `None`.
- **Evidence**: Commit hash (`git rev-parse --short HEAD`) + sensor output snippet.
