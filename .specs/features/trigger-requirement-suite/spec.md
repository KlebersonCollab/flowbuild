# Specification: Mandatory Trigger Node Requirement for Workflow Execution

## Acceptance Criteria (BDD)

### Scenario 1: Frontend execution blocked when canvas has no triggers
- **Given** a canvas with one or more action nodes (e.g. `HttpRequestComponent`) and no trigger node
- **When** the user clicks "Executar Fluxo"
- **Then** execution is prevented before sending any HTTP request
- **And** a warning notification is displayed to the user
- **And** the execution console drawer opens with a `warn` log entry explaining that an initial Trigger is required

### Scenario 2: Frontend execution proceeds when trigger is present
- **Given** a canvas containing at least one trigger node (e.g. `ManualTriggerComponent`)
- **When** the user clicks "Executar Fluxo"
- **Then** execution starts normally, streaming events via SSE to the console

### Scenario 3: Backend runtime stream blocks execution if trigger missing
- **Given** a flow payload with nodes but zero triggers submitted to `/api/v1/flows/execute/stream` with runtime validation
- **When** the stream execution starts
- **Then** the stream yields `flow_failed` with a clear explanation: `"O workflow precisa de pelo menos um nó Trigger inicial para ser executado."`
- **And** execution context terminates without executing isolated action components

### Scenario 4: Preservation of existing test suites and templates
- **Given** the pre-configured templates (`http_enrich`, `webhook_flow`, `python_pipeline`)
- **When** loaded and executed
- **Then** all templates pass trigger validation and execute successfully
- **And** all 40 backend pytest tests and 21 frontend vitest tests remain green
