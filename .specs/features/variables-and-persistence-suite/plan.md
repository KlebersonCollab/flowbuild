# Feature Plan: Variables System & Agnostic Database Persistence (SQLite/PostgreSQL)

## 1. Executive Summary
Provide a production-grade variable management architecture (global and flow-scoped variables) and upgrade persistence to an agnostic SQLAlchemy engine supporting SQLite and PostgreSQL out-of-the-box. Ensure node positions on the canvas are auto-persisted on drag and variables can be called via dedicated nodes or `{{VARIABLE}}` inline interpolation.

## 2. Problem Statement
1. When nodes are dragged on the canvas, their updated positions are not automatically synchronized and persisted in the backend database.
2. The user wants PostgreSQL compatibility alongside SQLite for scalable persistence of flows, executions, and variables.
3. Repetitive configuration of URLs, API keys, and endpoints across nodes creates friction and errors; users need global and flow-scoped variables accessible via CRUD, dedicated variable nodes, and template strings.

## 3. High-Level Scope
- **Agnostic Database Engine**: SQLAlchemy 2.0 with dynamic dialect detection (`sqlite:///` default, `postgresql://` optional) in `db.py`.
- **Variables Table & CRUD API**:
  - Table `variables` with `scope` ('global' | 'flow'), `flow_id`, `key`, `value`, `is_secret`.
  - Endpoints `GET /api/v1/variables`, `POST /api/v1/variables`, `PUT /api/v1/variables/{id}`, `DELETE /api/v1/variables/{id}`.
- **Variables Engine & Interpolation**:
  - `VariableComponent`: canvas node fetching variable value.
  - Template substitution: `{{key}}` automatic resolution in `FlowRunner`.
- **Canvas Drag & Layout Auto-Save**:
  - `@node-drag-stop` in `FlowCanvas.vue` with debounced auto-sync to backend.
- **Variables Management UI**:
  - `VariablesModal.vue`: modal for managing global and flow-level variables with create, edit, delete, and copy helper.
