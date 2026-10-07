import { describe, it, expect } from 'vitest'
import {
  getWebhookInfo,
  getWebhookAuthBadge,
  getWebhookCurlCommand,
  type WebhookInfo,
} from '../src/utils/webhook'

describe('FlowsModal Multi-Method Webhook Info Extraction', () => {
  it('returns null if flow has no WebhookTriggerComponent', () => {
    const flowData = {
      nodes: [
        { id: '1', type: 'ManualTriggerComponent', data: {} },
        { id: '2', type: 'HttpRequestComponent', data: {} },
      ],
    }
    expect(getWebhookInfo(flowData)).toBeNull()
  })

  it('extracts default path, POST method and none auth when inputs are omitted', () => {
    const flowData = {
      nodes: [
        { id: 'wh', type: 'WebhookTriggerComponent', data: { inputs: {} } },
      ],
    }
    const info = getWebhookInfo(flowData)
    expect(info).not.toBeNull()
    expect(info?.path).toBe('webhook/default')
    expect(info?.method).toBe('POST')
    expect(info?.authType).toBe('none')
    expect(info?.authHeaderName).toBe('X-API-Key')
    expect(info?.authQueryParam).toBe('api_key')
  })

  it('extracts custom path and GET method correctly', () => {
    const flowData = {
      nodes: [
        {
          id: 'wh',
          type: 'WebhookTriggerComponent',
          data: {
            inputs: {
              path: '/webhook/verify-challenge',
              method: 'GET',
            },
          },
        },
      ],
    }
    const info = getWebhookInfo(flowData)
    expect(info).not.toBeNull()
    expect(info?.path).toBe('webhook/verify-challenge')
    expect(info?.method).toBe('GET')
  })

  it('extracts ANY method and strips leading slash from path', () => {
    const flowData = {
      nodes: [
        {
          id: 'wh',
          type: 'WebhookTriggerComponent',
          data: {
            inputs: {
              path: '/api/incoming/event',
              method: 'ANY',
            },
          },
        },
      ],
    }
    const info = getWebhookInfo(flowData)
    expect(info).not.toBeNull()
    expect(info?.path).toBe('api/incoming/event')
    expect(info?.method).toBe('ANY')
  })

  it('extracts api_key_header with custom header and token', () => {
    const flowData = {
      nodes: [
        {
          id: 'wh',
          type: 'WebhookTriggerComponent',
          data: {
            inputs: {
              path: 'custom/auth',
              auth_type: 'api_key_header',
              auth_header_name: 'Stripe-Signature',
              auth_token: 'whsec_98765',
            },
          },
        },
      ],
    }
    const info = getWebhookInfo(flowData)
    expect(info?.authType).toBe('api_key_header')
    expect(info?.authHeaderName).toBe('Stripe-Signature')
    expect(info?.authToken).toBe('whsec_98765')
  })

  it('falls back to api_key_header when legacy secret_token is provided without auth_type', () => {
    const flowData = {
      nodes: [
        {
          id: 'wh',
          type: 'WebhookTriggerComponent',
          data: {
            inputs: {
              path: 'legacy/token',
              secret_token: 'legacy-secret-123',
            },
          },
        },
      ],
    }
    const info = getWebhookInfo(flowData)
    expect(info?.authType).toBe('api_key_header')
    expect(info?.authHeaderName).toBe('X-API-Key')
    expect(info?.authToken).toBe('legacy-secret-123')
  })

  it('extracts bearer auth and api_key_query auth properly', () => {
    const bearerFlow = {
      nodes: [
        {
          id: 'wh',
          type: 'WebhookTriggerComponent',
          data: {
            inputs: {
              auth_type: 'bearer',
              auth_token: 'jwt.token.abc',
            },
          },
        },
      ],
    }
    const queryFlow = {
      nodes: [
        {
          id: 'wh',
          type: 'WebhookTriggerComponent',
          data: {
            inputs: {
              auth_type: 'api_key_query',
              auth_query_param: 'access_key',
              auth_token: 'query-secret-456',
            },
          },
        },
      ],
    }

    const bearerInfo = getWebhookInfo(bearerFlow)
    expect(bearerInfo?.authType).toBe('bearer')
    expect(bearerInfo?.authToken).toBe('jwt.token.abc')

    const queryInfo = getWebhookInfo(queryFlow)
    expect(queryInfo?.authType).toBe('api_key_query')
    expect(queryInfo?.authQueryParam).toBe('access_key')
    expect(queryInfo?.authToken).toBe('query-secret-456')
  })
})

describe('Webhook Auth Badges', () => {
  it('returns correct label and css classes for all auth types', () => {
    const noneBadge = getWebhookAuthBadge({
      path: 'p',
      method: 'POST',
      authType: 'none',
      authHeaderName: 'X-API-Key',
      authQueryParam: 'api_key',
      authToken: '',
    })
    expect(noneBadge.label).toContain('Aberto')

    const headerBadge = getWebhookAuthBadge({
      path: 'p',
      method: 'POST',
      authType: 'api_key_header',
      authHeaderName: 'X-Custom-Auth',
      authQueryParam: 'api_key',
      authToken: 'secret',
    })
    expect(headerBadge.label).toBe('Header: X-Custom-Auth')

    const bearerBadge = getWebhookAuthBadge({
      path: 'p',
      method: 'POST',
      authType: 'bearer',
      authHeaderName: 'X-API-Key',
      authQueryParam: 'api_key',
      authToken: 'token',
    })
    expect(bearerBadge.label).toBe('Bearer Token')

    const queryBadge = getWebhookAuthBadge({
      path: 'p',
      method: 'POST',
      authType: 'api_key_query',
      authHeaderName: 'X-API-Key',
      authQueryParam: 'token_id',
      authToken: 'secret',
    })
    expect(queryBadge.label).toBe('Query: ?token_id=')
  })
})

describe('Webhook cURL Command Generation', () => {
  it('generates cURL for public POST webhook', () => {
    const info: WebhookInfo = {
      path: 'webhook/public',
      method: 'POST',
      authType: 'none',
      authHeaderName: 'X-API-Key',
      authQueryParam: 'api_key',
      authToken: '',
    }
    const curl = getWebhookCurlCommand('http://localhost:8000/api/v1/webhooks/webhook/public', info)
    expect(curl).toBe('curl -X POST "http://localhost:8000/api/v1/webhooks/webhook/public" -H "Content-Type: application/json" -d \'{"event": "test"}\'')
  })

  it('generates cURL for GET webhook without request body', () => {
    const info: WebhookInfo = {
      path: 'webhook/get-status',
      method: 'GET',
      authType: 'none',
      authHeaderName: 'X-API-Key',
      authQueryParam: 'api_key',
      authToken: '',
    }
    const curl = getWebhookCurlCommand('http://localhost:8000/api/v1/webhooks/webhook/get-status', info)
    expect(curl).toBe('curl -X GET "http://localhost:8000/api/v1/webhooks/webhook/get-status"')
  })

  it('generates cURL with custom header authentication', () => {
    const info: WebhookInfo = {
      path: 'webhook/secure',
      method: 'POST',
      authType: 'api_key_header',
      authHeaderName: 'X-Hook-Key',
      authQueryParam: 'api_key',
      authToken: 'my-secret-key',
    }
    const curl = getWebhookCurlCommand('http://localhost:8000/api/v1/webhooks/webhook/secure', info)
    expect(curl).toContain('-H "X-Hook-Key: my-secret-key"')
    expect(curl).toContain('-H "Content-Type: application/json"')
  })

  it('generates cURL with Bearer token authentication', () => {
    const info: WebhookInfo = {
      path: 'webhook/secure',
      method: 'POST',
      authType: 'bearer',
      authHeaderName: 'X-API-Key',
      authQueryParam: 'api_key',
      authToken: 'bearer-token-123',
    }
    const curl = getWebhookCurlCommand('http://localhost:8000/api/v1/webhooks/webhook/secure', info)
    expect(curl).toContain('-H "Authorization: Bearer bearer-token-123"')
  })

  it('generates cURL with query parameter authentication', () => {
    const info: WebhookInfo = {
      path: 'webhook/secure',
      method: 'POST',
      authType: 'api_key_query',
      authHeaderName: 'X-API-Key',
      authQueryParam: 'auth_token',
      authToken: 'secret99',
    }
    const curl = getWebhookCurlCommand('http://localhost:8000/api/v1/webhooks/webhook/secure', info)
    expect(curl).toContain('http://localhost:8000/api/v1/webhooks/webhook/secure?auth_token=secret99')
  })
})
