# Specification: Multi-Method Webhook Support (GET, POST, PUT, DELETE, ANY)

## Acceptance Criteria (BDD)

### Scenario 1: Trigger webhook via GET request with query parameters
- **Given** an active workflow with a `WebhookTriggerComponent` configured with `path: "/webhook/verify"` and `method: "GET"`
- **When** an external client sends `GET /api/v1/webhooks/verify?hub.challenge=xyz123&token=abc`
- **Then** the endpoint responds with HTTP 200 OK
- **And** the workflow executes with `payload` containing `{"hub.challenge": "xyz123", "token": "abc"}`
- **And** execution status is `completed`

### Scenario 2: Trigger webhook via POST request with JSON body
- **Given** an active workflow with a `WebhookTriggerComponent` configured with `path: "/webhook/order"` and `method: "POST"`
- **When** an external client sends `POST /api/v1/webhooks/order` with JSON `{"order_id": 999}`
- **Then** the endpoint responds with HTTP 200 OK
- **And** the workflow executes with `payload` containing `{"order_id": 999}`

### Scenario 3: Trigger webhook configured with method "ANY"
- **Given** an active workflow with a `WebhookTriggerComponent` configured with `method: "ANY"`
- **When** requests arrive via `GET`, `POST`, `PUT`, or `DELETE`
- **Then** all four HTTP methods execute the workflow successfully with HTTP 200 OK

### Scenario 4: Method mismatch yields descriptive HTTP 405
- **Given** an active workflow with a `WebhookTriggerComponent` configured with `method: "POST"`
- **When** an external client sends a `GET /api/v1/webhooks/...` request
- **Then** the endpoint returns HTTP 405 Method Not Allowed
- **And** the response body detail explains that the webhook expects `POST`, but received `GET`

### Scenario 5: Frontend FlowsModal displays the configured HTTP method badge
- **Given** a flow containing a `WebhookTriggerComponent`
- **When** the user opens the "Fluxos Salvos" modal
- **Then** the webhook banner displays the method badge (e.g. `GET`, `POST`, `ANY`) next to the route path
