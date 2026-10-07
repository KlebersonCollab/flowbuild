# Task List: GitHub Showcase README & Visual Documentation (ADR 0016)

## Sequence Guidelines (MetaGPT SOP)
- **Strict Sequential Order**: Tasks must be executed top-to-bottom without reordering.
- **Atomic File Boundaries**: Each task modifies at most 1–3 specific target files.
- **Decoupled Test Setup**: Test tasks (`Type: test`) precede implementation tasks (`Type: feat`).
- **Sensor Evidence Gate**: Mark complete `[x]` ONLY after passing build, lint, and test sensors with recorded evidence.

## Implementation Tasks

| Status | ID | Type | Description | Target Files | Dependencies | Evidence |
|---|---|---|---|---|---|---|
| [x] | TASK-01 | feat | Create automated capture script and take real 1080p screenshots of the live running application | `.agents/scripts/capture-screenshots.mjs`, `docs/screenshots/canvas-hero.png`, `docs/screenshots/flows-manager-worktree.png`, `docs/screenshots/variables-modal.png`, `docs/screenshots/execution-drawer-telemetry.png`, `frontend/package.json`, `frontend/package-lock.json` | None | 4 high-DPI screenshots captured successfully via Chrome Puppeteer |
| [x] | TASK-02 | docs | Author canonical showcase README.md with badges, diagrams, features, quickstart, and screenshots | `README.md`, `LICENSE` | TASK-01 | README.md and MIT LICENSE created with full feature showcase |
| [x] | TASK-03 | review | Run full sensor verification (Pytest, Vitest, Vue build, and SDD integrity sensor) | `README.md`, `docs/screenshots/`, `.specs/` | TASK-02 | Pytest 71 passed, Vitest 71 passed, Vue build clean, SDD integrity 100% |

## Schema Dictionary
- **Status**: `[ ]` (Pending) | `[x]` (Verified Complete).
- **ID**: `TASK-01`, `TASK-02`, etc.
- **Type**: `test` | `feat` | `fix` | `refactor` | `docs` | `rules` | `skill` | `review`.
- **Target Files**: Concrete comma-separated file paths (relative to workspace root).
- **Dependencies**: Comma-separated list of preceding task IDs or `None`.
- **Evidence**: Commit hash (`git rev-parse --short HEAD`) + sensor output snippet.
