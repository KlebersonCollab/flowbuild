# Specification: Modern Toast Notification System

## Acceptance Criteria (BDD)

### Scenario 1: Trigger validation warning toast on execution attempt
- **Given** a canvas without a Trigger node
- **When** the user clicks "Executar Fluxo"
- **Then** a warning toast (`type: 'warn'`) appears with title `"Atenção"` and message `"O workflow precisa de pelo menos um nó Trigger inicial..."`
- **And** no native browser `alert()` modal is invoked
- **And** the execution drawer logs the warning in real-time

### Scenario 2: Error toast on invalid JSON import
- **Given** the user uploads a malformed JSON file via "Importar JSON"
- **When** parsing fails
- **Then** an error toast (`type: 'error'`) appears with message `"Arquivo JSON inválido. Verifique o formato do fluxo."`
- **And** no native browser `alert()` modal is invoked

### Scenario 3: Success toast on valid actions
- **Given** an action completes (e.g. successful flow import or publish)
- **When** `toast.success(...)` is called
- **Then** a success toast (`type: 'success'`) appears with green semantic styling

### Scenario 4: Auto-dismissal and manual close
- **Given** an active toast on screen
- **When** the user clicks the close `X` button OR after the timeout expires (4.5s)
- **Then** the toast is removed smoothly from the viewport
