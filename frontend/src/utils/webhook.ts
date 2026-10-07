export type WebhookAuthType = 'none' | 'api_key_header' | 'bearer' | 'api_key_query'

export interface WebhookInfo {
  path: string
  method: string
  authType: WebhookAuthType
  authHeaderName: string
  authQueryParam: string
  authToken: string
}

export function getWebhookInfo(flowData: any): WebhookInfo | null {
  const node = flowData?.nodes?.find((n: any) => n.type === 'WebhookTriggerComponent')
  if (!node) return null
  const inputs = node.data?.inputs || {}
  const rawPath = inputs.path || 'webhook/default'
  const path = rawPath.startsWith('/') ? rawPath.slice(1) : rawPath
  const method = (inputs.method || 'POST').toUpperCase()

  const legacySecret = inputs.secret_token || ''
  let authType: WebhookAuthType = inputs.auth_type
  if (!authType) {
    authType = legacySecret ? 'api_key_header' : 'none'
  }

  const authHeaderName = inputs.auth_header_name || 'X-API-Key'
  const authQueryParam = inputs.auth_query_param || 'api_key'
  const authToken = inputs.auth_token || legacySecret || ''

  return {
    path,
    method,
    authType,
    authHeaderName,
    authQueryParam,
    authToken,
  }
}

export function getWebhookPath(flowData: any): string | null {
  const info = getWebhookInfo(flowData)
  return info ? info.path : null
}

export function getWebhookAuthBadge(info: WebhookInfo): { label: string; class: string } {
  switch (info.authType) {
    case 'api_key_header':
      return {
        label: `Header: ${info.authHeaderName}`,
        class: 'bg-amber-500/15 text-amber-400 border-amber-500/30',
      }
    case 'bearer':
      return {
        label: 'Bearer Token',
        class: 'bg-purple-500/15 text-purple-400 border-purple-500/30',
      }
    case 'api_key_query':
      return {
        label: `Query: ?${info.authQueryParam}=`,
        class: 'bg-blue-500/15 text-blue-400 border-blue-500/30',
      }
    case 'none':
    default:
      return {
        label: 'Aberto (Sem Auth)',
        class: 'bg-zinc-500/15 text-zinc-400 border-zinc-500/30',
      }
  }
}

export function getWebhookCurlCommand(fullUrl: string, info: WebhookInfo): string {
  const method = info.method === 'ANY' ? 'POST' : info.method
  const token = info.authToken || '<SEU_TOKEN>'

  let targetUrl = fullUrl
  if (info.authType === 'api_key_query') {
    const sep = targetUrl.includes('?') ? '&' : '?'
    targetUrl = `${targetUrl}${sep}${info.authQueryParam}=${token}`
  }

  const parts = [`curl -X ${method} "${targetUrl}"`]

  if (info.authType === 'api_key_header') {
    parts.push(`-H "${info.authHeaderName}: ${token}"`)
  } else if (info.authType === 'bearer') {
    parts.push(`-H "Authorization: Bearer ${token}"`)
  }

  if (['POST', 'PUT', 'PATCH'].includes(method)) {
    parts.push(`-H "Content-Type: application/json"`)
    parts.push(`-d '{"event": "test"}'`)
  }

  return parts.join(' ')
}
