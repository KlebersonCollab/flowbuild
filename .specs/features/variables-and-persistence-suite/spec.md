# Feature Spec: Variables System & Agnostic Persistence

## 1. Domain Glossary Alignment
- **Global Variable**: Key-value pair stored centrally and available across all flows in the system.
- **Flow Variable**: Key-value pair scoped to a specific flow (`flow_id`), taking precedence over any global variable with the same key.
- **Template Interpolation**: Automatic replacement of `{{VAR_NAME}}` or `{{scope.VAR_NAME}}` patterns within string inputs of any component before execution.
- **Agnostic Database Engine**: A unified SQLAlchemy engine layer capable of connecting to SQLite or PostgreSQL transparently based on `DATABASE_URL`.
- **Canvas Position Auto-Persistence**: Real-time or debounced synchronization of node `{x, y}` coordinates to the database on drag release.

## 2. Business Rules & Invariants
- `BR-1`: Flow variables MUST override Global variables sharing the identical key name when executing within that flow.
- `BR-2`: Secret variables (`is_secret = True`) MUST be masked in non-admin read representations if configured.
- `BR-3`: The database abstraction MUST support SQLite (`sqlite:///...`) and PostgreSQL (`postgresql://...`) using standard SQLAlchemy column types and JSON serialization.
- `BR-4`: Any dragging movement of a canvas node MUST update the flow's node coordinate state and trigger persistent synchronization to the database.

## 3. Acceptance Criteria (BDD)

### AC-1: Scoped Variables Hierarchy & Interpolation
- **Given** a global variable `API_HOST = "api.global.com"` and a flow variable for flow F1 `API_HOST = "api.flow1.com"`.
- **When** flow F1 executes an `HttpRequestComponent` with URL `https://{{API_HOST}}/users`.
- **Then** the resolved request URL is `https://api.flow1.com/users`.

### AC-2: Dedicated Variable Component
- **Given** a `VariableComponent` configured with `variable_name = "BASE_URL"`.
- **When** the node executes within a flow where `BASE_URL` is configured.
- **Then** the output port `value` emits the string value of the variable.

### AC-3: Variables CRUD API
- **Given** a request to `POST /api/v1/variables` with `{"key": "TOKEN", "value": "xyz", "scope": "global"}`.
- **When** the endpoint processes the request.
- **Then** a 201 response returns the created variable, and `GET /api/v1/variables?scope=global` lists it.

### AC-4: Canvas Node Drag Auto-Persistence
- **Given** a node on the canvas dragged to new coordinates `{x: 350, y: 420}`.
- **When** the drag event finishes (`@node-drag-stop`).
- **Then** the flow model in the backend database updates node position to `{x: 350, y: 420}`.
