import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { FlowNode, FlowEdge, FlowPosition, FlowModel, Environment, FlowRecordItem } from '../types/flow'

export const useFlowStore = defineStore('flow', () => {
  const flowId = ref<string>('flow-current')
  const flowName = ref<string>('My Automation Workflow')
  const flowDescription = ref<string>('')
  const currentEnvironment = ref<Environment>('dev')
  const currentFolder = ref<string>('Geral')
  const version = ref<string>('v1.0.0')
  const sourceFlowId = ref<string | null>(null)
  const isDraft = ref<boolean>(false)
  const nodes = ref<FlowNode[]>([])
  const edges = ref<FlowEdge[]>([])
  const selectedNodeId = ref<string | null>(null)
  const isActive = ref<boolean>(true)
  const savedFlows = ref<FlowRecordItem[]>([])
  let autoSaveTimeout: ReturnType<typeof setTimeout> | null = null

  function bumpPatchVersion(v: string): string {
    try {
      const clean = (v || 'v1.0.0').replace(/^v/, '')
      const parts = clean.split('.')
      const major = parseInt(parts[0] || '1', 10)
      const minor = parseInt(parts[1] || '0', 10)
      const patch = parseInt(parts[2] || '0', 10) + 1
      return `v${major}.${minor}.${patch}`
    } catch {
      return 'v1.0.1'
    }
  }

  const selectedNode = computed(() => {
    if (!selectedNodeId.value) return null
    return nodes.value.find((n) => n.id === selectedNodeId.value) || null
  })

  const flowsInCurrentEnvironment = computed(() =>
    savedFlows.value.filter((f) => (f.environment || 'dev') === currentEnvironment.value)
  )

  const flowsByFolder = computed(() => {
    const map: Record<string, FlowRecordItem[]> = {}
    for (const flow of flowsInCurrentEnvironment.value) {
      const folderName = flow.folder || 'Geral'
      if (!map[folderName]) {
        map[folderName] = []
      }
      map[folderName].push(flow)
    }
    return map
  })

  function setEnvironment(env: Environment): void {
    if (currentEnvironment.value === env) return
    currentEnvironment.value = env

    // Lineage resolution: find corresponding linked flow in target environment
    let targetFlow: FlowRecordItem | undefined

    if (env === 'dev') {
      if (sourceFlowId.value) {
        targetFlow = savedFlows.value.find((f) => f.id === sourceFlowId.value && (f.environment || 'dev') === 'dev')
      }
      if (!targetFlow) {
        const cleanId = flowId.value.replace(/-qa$|-prd$/, '')
        targetFlow = savedFlows.value.find((f) => f.id === cleanId && (f.environment || 'dev') === 'dev')
      }
    } else {
      // Switching to QA or PRD: look for child flow promoted from flowId
      targetFlow = savedFlows.value.find(
        (f) =>
          f.environment === env &&
          (f.source_flow_id === flowId.value || f.id === `${flowId.value}-${env}`)
      )
    }

    if (!targetFlow) {
      targetFlow = savedFlows.value.find((f) => (f.environment || 'dev') === env)
    }

    if (targetFlow && targetFlow.flow_data) {
      loadFlow(targetFlow.flow_data)
      isActive.value = targetFlow.is_active ?? true
      isDraft.value = targetFlow.is_draft ?? false
    }
  }

  function setFolder(folder: string): void {
    currentFolder.value = folder
  }

  function addNode(
    type: string,
    position: FlowPosition = { x: 200, y: 150 },
    initialInputs: Record<string, any> = {}
  ): string {
    const id = `node-${Date.now()}-${Math.random().toString(36).substring(2, 6)}`
    const newNode: FlowNode = {
      id,
      type,
      position,
      data: {
        inputs: { ...initialInputs },
      },
    }
    nodes.value.push(newNode)
    selectedNodeId.value = id
    isDraft.value = true
    isActive.value = false
    triggerAutoSave()
    return id
  }

  function removeNode(id: string): void {
    nodes.value = nodes.value.filter((n) => n.id !== id)
    edges.value = edges.value.filter((e) => e.source !== id && e.target !== id)
    if (selectedNodeId.value === id) {
      selectedNodeId.value = null
    }
    isDraft.value = true
    isActive.value = false
    triggerAutoSave()
  }

  function addEdge(edgeData: {
    source: string
    sourceHandle?: string
    target: string
    targetHandle?: string
  }): string {
    const id = `edge-${Date.now()}-${Math.random().toString(36).substring(2, 6)}`
    const newEdge: FlowEdge = {
      id,
      source: edgeData.source,
      sourceHandle: edgeData.sourceHandle,
      target: edgeData.target,
      targetHandle: edgeData.targetHandle,
    }
    edges.value.push(newEdge)
    isDraft.value = true
    isActive.value = false
    triggerAutoSave()
    return id
  }

  function removeEdge(id: string): void {
    edges.value = edges.value.filter((e) => e.id !== id)
    isDraft.value = true
    isActive.value = false
    triggerAutoSave()
  }

  function updateNodeInput(nodeId: string, key: string, value: any): void {
    const node = nodes.value.find((n) => n.id === nodeId)
    if (node) {
      if (!node.data.inputs) {
        node.data.inputs = {}
      }
      node.data.inputs[key] = value
      isDraft.value = true
      isActive.value = false
      triggerAutoSave()
    }
  }

  function updateNodePosition(nodeId: string, position: FlowPosition): void {
    const node = nodes.value.find((n) => n.id === nodeId)
    if (node) {
      node.position = { ...position }
      isDraft.value = true
      isActive.value = false
      triggerAutoSave()
    }
  }

  function updateNodeExpanded(nodeId: string, expanded: boolean): void {
    const node = nodes.value.find((n) => n.id === nodeId)
    if (node) {
      node.data.expanded = expanded
      triggerAutoSave()
    }
  }

  function selectNode(nodeId: string | null): void {
    selectedNodeId.value = nodeId
  }

  function toFlowPayload(name?: string, description?: string): FlowModel {
    return {
      id: flowId.value,
      name: name || flowName.value,
      description: description !== undefined ? description : (flowDescription.value || ''),
      folder: currentFolder.value,
      environment: currentEnvironment.value,
      version: version.value,
      source_flow_id: sourceFlowId.value,
      is_draft: isDraft.value,
      nodes: JSON.parse(JSON.stringify(nodes.value)),
      edges: JSON.parse(JSON.stringify(edges.value)),
    }
  }

  function loadFlow(flow: FlowModel): void {
    flowId.value = flow.id
    flowName.value = flow.name
    flowDescription.value = flow.description || ''
    currentFolder.value = flow.folder || 'Geral'
    if (flow.environment) {
      currentEnvironment.value = flow.environment
    }
    version.value = flow.version || 'v1.0.0'
    sourceFlowId.value = flow.source_flow_id || null
    isDraft.value = flow.is_draft ?? false
    nodes.value = flow.nodes || []
    edges.value = flow.edges || []
    selectedNodeId.value = null
  }

  function loadTemplate(
    templateType:
      | 'http_enrich'
      | 'webhook_flow'
      | 'python_pipeline'
      | 'if_condition_flow'
      | 'paginated_api_flow'
      | 'switch_router_flow'
      | 'data_filter_alert_flow'
      | 'delay_polling_flow'
      | 'etl_pagination_filter_flow'
      | 'database_csv_export_flow'
      | 'batch_kv_discord_flow'
      | 'resilient_try_catch_telegram_flow'
  ): void {
    if (templateType === 'http_enrich') {
      flowId.value = 'flow-http-enrich'
      flowName.value = 'Enriquecimento de Dados HTTP'
      flowDescription.value = 'Disparo manual que consome a API do GitHub e formata os dados em JSON estruturado.'
      const n1Id = 'trigger-1'
      const n2Id = 'http-1'
      const n3Id = 'transform-1'
      nodes.value = [
        {
          id: n1Id,
          type: 'ManualTriggerComponent',
          position: { x: 80, y: 180 },
          data: {
            inputs: {
              initial_payload: { user: "octocat", action: "fetch_quote" }
            }
          }
        },
        {
          id: n2Id,
          type: 'HttpRequestComponent',
          position: { x: 420, y: 180 },
          data: {
            inputs: {
              url: 'https://api.github.com/zen',
              method: 'GET',
              timeout: 15
            }
          }
        },
        {
          id: n3Id,
          type: 'JsonTransformComponent',
          position: { x: 760, y: 180 },
          data: {
            inputs: {
              expression: "{'quote': payload.get('response', 'ok'), 'processed_by': 'flowbuild'}"
            }
          }
        }
      ]
      edges.value = [
        { id: 'e1', source: n1Id, sourceHandle: 'data', target: n2Id, targetHandle: 'body' },
        { id: 'e2', source: n2Id, sourceHandle: 'data', target: n3Id, targetHandle: 'input_data' }
      ]
    } else if (templateType === 'python_pipeline') {
      flowId.value = 'flow-python-pipeline'
      flowName.value = 'Pipeline de Automação Python'
      flowDescription.value = 'Pipeline com script Python customizado para processamento e agregações matemáticas.'
      const n1Id = 'trigger-1'
      const n2Id = 'py-1'
      nodes.value = [
        {
          id: n1Id,
          type: 'ManualTriggerComponent',
          position: { x: 100, y: 180 },
          data: {
            inputs: {
              initial_payload: { values: [10, 25, 45, 90] }
            }
          }
        },
        {
          id: n2Id,
          type: 'PythonScriptComponent',
          position: { x: 480, y: 180 },
          data: {
            inputs: {
              script: "def run(context):\n    vals = context.get('values', [])\n    return {'total': sum(vals), 'count': len(vals), 'average': sum(vals)/max(len(vals), 1)}"
            }
          }
        }
      ]
    } else if (templateType === 'if_condition_flow') {
      flowId.value = 'flow-if-condition'
      flowName.value = 'Decisão Condicional (IF / Else)'
      flowDescription.value = 'Fluxo de decisão lógica onde apenas o ramo correspondente à condição é executado.'
      const n1Id = 'trigger-1'
      const n2Id = 'if-1'
      const n3Id = 'tf-true'
      const n4Id = 'tf-false'
      nodes.value = [
        {
          id: n1Id,
          type: 'ManualTriggerComponent',
          position: { x: 80, y: 200 },
          data: {
            inputs: {
              initial_payload: { score: 85, user: 'Alice', status: 'pending' }
            }
          }
        },
        {
          id: n2Id,
          type: 'IfConditionComponent',
          position: { x: 420, y: 200 },
          data: {
            inputs: {
              expression: "data.get('score', 0) >= 70"
            }
          }
        },
        {
          id: n3Id,
          type: 'JsonTransformComponent',
          position: { x: 780, y: 100 },
          data: {
            inputs: {
              expression: "dict(status='aprovado', score=payload.get('score'), user=payload.get('user'))"
            }
          }
        },
        {
          id: n4Id,
          type: 'JsonTransformComponent',
          position: { x: 780, y: 320 },
          data: {
            inputs: {
              expression: "dict(status='rejeitado', score=payload.get('score'), user=payload.get('user'))"
            }
          }
        }
      ]
      edges.value = [
        { id: 'e1', source: n1Id, sourceHandle: 'data', target: n2Id, targetHandle: 'input_data' },
        { id: 'e2', source: n2Id, sourceHandle: 'true_branch', target: n3Id, targetHandle: 'input_data' },
        { id: 'e3', source: n2Id, sourceHandle: 'false_branch', target: n4Id, targetHandle: 'input_data' },
      ]
    } else if (templateType === 'paginated_api_flow') {
      flowId.value = 'flow-paginated-api'
      flowName.value = 'API Paginada com Loop & Break'
      flowDescription.value = 'Consome APIs REST paginadas iterando páginas até a última ou condição de parada (break), consolidando o JSON completo.'
      const n1Id = 'trigger-1'
      const n2Id = 'page-http-1'
      const n3Id = 'summary-1'
      nodes.value = [
        {
          id: n1Id,
          type: 'ManualTriggerComponent',
          position: { x: 80, y: 180 },
          data: {
            inputs: {
              initial_payload: { sort: 'updated', direction: 'desc' }
            }
          }
        },
        {
          id: n2Id,
          type: 'PaginatedHttpComponent',
          position: { x: 440, y: 180 },
          data: {
            inputs: {
              url: 'https://api.github.com/orgs/vuejs/repos',
              method: 'GET',
              pagination_mode: 'page_number',
              page_param: 'page',
              limit_param: 'per_page',
              page_size: 10,
              start_page: 1,
              items_path: '',
              break_condition: 'total_items >= 25',
              max_pages: 5,
              headers: { 'User-Agent': 'FlowBuild/1.0' },
              params: {}
            }
          }
        },
        {
          id: n3Id,
          type: 'JsonTransformComponent',
          position: { x: 820, y: 180 },
          data: {
            inputs: {
              expression: "dict(total_registros=len(payload), repositorios=[r.get('name') for r in payload if isinstance(r, dict)])"
            }
          }
        }
      ]
      edges.value = [
        { id: 'e1', source: n1Id, sourceHandle: 'data', target: n2Id, targetHandle: 'params' },
        { id: 'e2', source: n2Id, sourceHandle: 'all_items', target: n3Id, targetHandle: 'input_data' },
      ]
    } else if (templateType === 'webhook_flow') {
      flowId.value = 'flow-webhook-transform'
      flowName.value = 'Recepção Webhook & Filtro'
      flowDescription.value = 'Endpoint de webhook HTTP para recepção e filtragem contínua de leads em tempo real.'
      const n1Id = 'wh-1'
      const n2Id = 'tf-1'
      nodes.value = [
        {
          id: n1Id,
          type: 'WebhookTriggerComponent',
          position: { x: 100, y: 180 },
          data: {
            inputs: {
              path: '/webhook/lead',
              method: 'POST'
            }
          }
        },
        {
          id: n2Id,
          type: 'JsonTransformComponent',
          position: { x: 460, y: 180 },
          data: {
            inputs: {
              expression: "dict(status='received', payload=payload)"
            }
          }
        }
      ]
      edges.value = [
        { id: 'e1', source: n1Id, sourceHandle: 'payload', target: n2Id, targetHandle: 'input_data' }
      ]
    } else if (templateType === 'switch_router_flow') {
      flowId.value = 'flow-switch-router'
      flowName.value = 'Roteamento Inteligente & Multi-Branch'
      flowDescription.value = 'Triagem multi-ramais baseada em regras de negócio com Switch Node e escalação automática de chamados críticos via Slack.'
      const n1Id = 'trig-1'
      const n2Id = 'switch-1'
      const n3Id = 'slack-urgent'
      const n4Id = 'tf-high'
      const n5Id = 'tf-med'
      const n6Id = 'tf-default'
      nodes.value = [
        {
          id: n1Id,
          type: 'ManualTriggerComponent',
          position: { x: 60, y: 220 },
          data: {
            inputs: {
              initial_payload: {
                ticket_id: 'TCK-9402',
                customer: 'Acme Corp',
                priority: 'critical',
                subject: 'Instabilidade no cluster de produção'
              }
            }
          }
        },
        {
          id: n2Id,
          type: 'SwitchNodeComponent',
          position: { x: 420, y: 200 },
          data: {
            inputs: {
              expression: "data.get('priority')",
              case_1_expr: "'critical'",
              case_2_expr: "'high'",
              case_3_expr: "'medium'"
            }
          }
        },
        {
          id: n3Id,
          type: 'SlackWebhookComponent',
          position: { x: 800, y: 40 },
          data: {
            inputs: {
              webhook_url: 'https://hooks.slack.com/services/T00/B00/X00',
              text: '🚨 ALERTA CRÍTICO: Chamado {{ticket_id}} de {{customer}} - {{subject}}',
              channel: '#incidents',
              username: 'IncidentBot',
              icon_emoji: ':fire:'
            }
          }
        },
        {
          id: n4Id,
          type: 'JsonTransformComponent',
          position: { x: 800, y: 190 },
          data: {
            inputs: {
              expression: "dict(queue='prioritaria', ticket=payload.get('ticket_id'), sla_horas=2)"
            }
          }
        },
        {
          id: n5Id,
          type: 'JsonTransformComponent',
          position: { x: 800, y: 340 },
          data: {
            inputs: {
              expression: "dict(queue='padrao', ticket=payload.get('ticket_id'), sla_horas=8)"
            }
          }
        },
        {
          id: n6Id,
          type: 'JsonTransformComponent',
          position: { x: 800, y: 480 },
          data: {
            inputs: {
              expression: "dict(queue='backlog_geral', ticket=payload.get('ticket_id'), status='triagem')"
            }
          }
        }
      ]
      edges.value = [
        { id: 'e1', source: n1Id, sourceHandle: 'data', target: n2Id, targetHandle: 'input_data' },
        { id: 'e2', source: n2Id, sourceHandle: 'case_1', target: n3Id, targetHandle: 'text' },
        { id: 'e3', source: n2Id, sourceHandle: 'case_2', target: n4Id, targetHandle: 'input_data' },
        { id: 'e4', source: n2Id, sourceHandle: 'case_3', target: n5Id, targetHandle: 'input_data' },
        { id: 'e5', source: n2Id, sourceHandle: 'default_branch', target: n6Id, targetHandle: 'input_data' }
      ]
    } else if (templateType === 'data_filter_alert_flow') {
      flowId.value = 'flow-data-filter-alert'
      flowName.value = 'Filtro de Dados & Alerta Slack'
      flowDescription.value = 'Extração e filtragem declarativa de lista de pedidos, separando pedidos VIP de compras padrão e notificando a equipe.'
      const n1Id = 'trig-1'
      const n2Id = 'filter-1'
      const n3Id = 'tf-vip'
      const n4Id = 'slack-vip'
      const n5Id = 'tf-standard'
      nodes.value = [
        {
          id: n1Id,
          type: 'ManualTriggerComponent',
          position: { x: 60, y: 200 },
          data: {
            inputs: {
              initial_payload: {
                batch_id: 'batch-2026-10',
                orders: [
                  { id: 101, customer: 'Empresa Alpha', total: 4500, tier: 'gold' },
                  { id: 102, customer: 'Beta Ltd', total: 320, tier: 'standard' },
                  { id: 103, customer: 'Mega Corp', total: 12800, tier: 'platinum' },
                  { id: 104, customer: 'Micro Dev', total: 150, tier: 'standard' }
                ]
              }
            }
          }
        },
        {
          id: n2Id,
          type: 'DataFilterComponent',
          position: { x: 420, y: 180 },
          data: {
            inputs: {
              items_path: 'orders',
              field: 'total',
              operator: 'greater_than',
              value: '1000'
            }
          }
        },
        {
          id: n3Id,
          type: 'JsonTransformComponent',
          position: { x: 780, y: 100 },
          data: {
            inputs: {
              expression: "dict(total_vips=len(payload), clientes=[p.get('customer') for p in payload], valor_total=sum(p.get('total', 0) for p in payload))"
            }
          }
        },
        {
          id: n4Id,
          type: 'SlackWebhookComponent',
          position: { x: 1140, y: 100 },
          data: {
            inputs: {
              webhook_url: 'https://hooks.slack.com/services/T00/B00/X00',
              text: '🎉 Relatório VIP: Identificados novos pedidos de alto valor no lote!',
              username: 'SalesBot',
              icon_emoji: ':moneybag:'
            }
          }
        },
        {
          id: n5Id,
          type: 'JsonTransformComponent',
          position: { x: 780, y: 300 },
          data: {
            inputs: {
              expression: "dict(total_pedidos_comuns=len(payload), status='fila_padrao_expedicao')"
            }
          }
        }
      ]
      edges.value = [
        { id: 'e1', source: n1Id, sourceHandle: 'data', target: n2Id, targetHandle: 'input_data' },
        { id: 'e2', source: n2Id, sourceHandle: 'filtered_items', target: n3Id, targetHandle: 'input_data' },
        { id: 'e3', source: n3Id, sourceHandle: 'data', target: n4Id, targetHandle: 'text' },
        { id: 'e4', source: n2Id, sourceHandle: 'discarded_items', target: n5Id, targetHandle: 'input_data' }
      ]
    } else if (templateType === 'delay_polling_flow') {
      flowId.value = 'flow-delay-polling'
      flowName.value = 'Automação com Delay & Polling Assíncrono'
      flowDescription.value = 'Dispara um processamento assíncrono, aguarda uma pausa não-bloqueante (Delay node) e notifica o término da rotina.'
      const n1Id = 'trig-1'
      const n2Id = 'http-start'
      const n3Id = 'delay-1'
      const n4Id = 'slack-finish'
      nodes.value = [
        {
          id: n1Id,
          type: 'ManualTriggerComponent',
          position: { x: 80, y: 200 },
          data: {
            inputs: {
              initial_payload: { job_id: 'export-data-902', environment: 'prd' }
            }
          }
        },
        {
          id: n2Id,
          type: 'HttpRequestComponent',
          position: { x: 400, y: 200 },
          data: {
            inputs: {
              url: 'https://httpbin.org/post',
              method: 'POST',
              body: { action: 'start_heavy_task' },
              timeout: 15
            }
          }
        },
        {
          id: n3Id,
          type: 'DelayComponent',
          position: { x: 740, y: 200 },
          data: {
            inputs: {
              delay: 3,
              unit: 'seconds'
            }
          }
        },
        {
          id: n4Id,
          type: 'SlackWebhookComponent',
          position: { x: 1060, y: 200 },
          data: {
            inputs: {
              webhook_url: 'https://hooks.slack.com/services/T00/B00/X00',
              text: '⏱️ Tarefa {{job_id}} finalizada com sucesso após intervalo de delay!',
              username: 'WorkflowNotifier',
              icon_emoji: ':white_check_mark:'
            }
          }
        }
      ]
      edges.value = [
        { id: 'e1', source: n1Id, sourceHandle: 'data', target: n2Id, targetHandle: 'body' },
        { id: 'e2', source: n2Id, sourceHandle: 'data', target: n3Id, targetHandle: 'input_data' },
        { id: 'e3', source: n3Id, sourceHandle: 'data', target: n4Id, targetHandle: 'text' }
      ]
    } else if (templateType === 'etl_pagination_filter_flow') {
      flowId.value = 'flow-etl-pagination-filter'
      flowName.value = 'ETL Completo: Paginação → Filtro → Slack'
      flowDescription.value = 'Pipeline analítico empresarial completo: consome API paginada, filtra itens por regras declarativas, consolida métricas e posta no Slack.'
      const n1Id = 'trig-1'
      const n2Id = 'page-http'
      const n3Id = 'filter-stars'
      const n4Id = 'tf-digest'
      const n5Id = 'slack-report'
      nodes.value = [
        {
          id: n1Id,
          type: 'ManualTriggerComponent',
          position: { x: 60, y: 200 },
          data: {
            inputs: {
              initial_payload: { organization: 'vuejs', min_stars: 100 }
            }
          }
        },
        {
          id: n2Id,
          type: 'PaginatedHttpComponent',
          position: { x: 380, y: 200 },
          data: {
            inputs: {
              url: 'https://api.github.com/orgs/vuejs/repos',
              method: 'GET',
              pagination_mode: 'page_number',
              page_param: 'page',
              limit_param: 'per_page',
              page_size: 10,
              start_page: 1,
              items_path: '',
              break_condition: 'total_items >= 20',
              max_pages: 3,
              headers: { 'User-Agent': 'FlowBuild/1.0' }
            }
          }
        },
        {
          id: n3Id,
          type: 'DataFilterComponent',
          position: { x: 740, y: 200 },
          data: {
            inputs: {
              field: 'stargazers_count',
              operator: 'greater_than',
              value: '500'
            }
          }
        },
        {
          id: n4Id,
          type: 'JsonTransformComponent',
          position: { x: 1080, y: 120 },
          data: {
            inputs: {
              expression: "dict(total_destaque=len(payload), top_repos=[r.get('name') for r in payload if isinstance(r, dict)])"
            }
          }
        },
        {
          id: n5Id,
          type: 'SlackWebhookComponent',
          position: { x: 1420, y: 120 },
          data: {
            inputs: {
              webhook_url: 'https://hooks.slack.com/services/T00/B00/X00',
              text: '📊 Relatório ETL: Ingestão paginada e filtragem concluídas com sucesso!',
              username: 'ETLBot',
              icon_emoji: ':bar_chart:'
            }
          }
        }
      ]
      edges.value = [
        { id: 'e1', source: n1Id, sourceHandle: 'data', target: n2Id, targetHandle: 'params' },
        { id: 'e2', source: n2Id, sourceHandle: 'all_items', target: n3Id, targetHandle: 'input_data' },
        { id: 'e3', source: n3Id, sourceHandle: 'filtered_items', target: n4Id, targetHandle: 'input_data' },
        { id: 'e4', source: n4Id, sourceHandle: 'data', target: n5Id, targetHandle: 'text' }
      ]
    } else if (templateType === 'database_csv_export_flow') {
      flowId.value = 'flow-db-csv-export'
      flowName.value = 'Exportação SQL para CSV & Email'
      flowDescription.value = 'Executa query SQL analítica periódica, converte os registros em formato tabular CSV (RFC 4180) e envia relatório transacional por e-mail.'
      const n1Id = 'cron-1'
      const n2Id = 'db-query-1'
      const n3Id = 'csv-parser-1'
      const n4Id = 'email-notify-1'
      nodes.value = [
        {
          id: n1Id,
          type: 'CronTriggerComponent',
          position: { x: 60, y: 200 },
          data: {
            inputs: {
              cron_expression: '0 8 * * 1'
            }
          }
        },
        {
          id: n2Id,
          type: 'DatabaseQueryComponent',
          position: { x: 380, y: 200 },
          data: {
            inputs: {
              query: "SELECT id, customer, amount, status FROM orders WHERE status = 'completed' ORDER BY amount DESC LIMIT 50;",
              fetch_mode: 'all',
              params: {}
            }
          }
        },
        {
          id: n3Id,
          type: 'CsvParserComponent',
          position: { x: 740, y: 200 },
          data: {
            inputs: {
              mode: 'generate',
              delimiter: ',',
              has_headers: true
            }
          }
        },
        {
          id: n4Id,
          type: 'EmailNotificationComponent',
          position: { x: 1080, y: 200 },
          data: {
            inputs: {
              smtp_host: 'smtp.mailgun.org',
              smtp_port: 587,
              use_tls: true,
              sender_email: 'relatorios@flowbuild.io',
              recipient_email: 'financeiro@empresa.com',
              subject: 'Relatório Semanal de Pedidos (CSV Export)',
              is_html: false
            }
          }
        }
      ]
      edges.value = [
        { id: 'e1', source: n1Id, sourceHandle: 'trigger_info', target: n2Id, targetHandle: 'params' },
        { id: 'e2', source: n2Id, sourceHandle: 'rows', target: n3Id, targetHandle: 'records' },
        { id: 'e3', source: n3Id, sourceHandle: 'csv_text', target: n4Id, targetHandle: 'body' }
      ]
    } else if (templateType === 'batch_kv_discord_flow') {
      flowId.value = 'flow-batch-kv-discord'
      flowName.value = 'Processamento em Lote com KV & Discord'
      flowDescription.value = 'Fatia uma coleção de transações em lotes via Loop Iterator, incrementa atomicamente o contador persistente no Key-Value Store e emite card Embed no Discord.'
      const n1Id = 'trig-1'
      const n2Id = 'loop-1'
      const n3Id = 'kv-1'
      const n4Id = 'discord-1'
      nodes.value = [
        {
          id: n1Id,
          type: 'ManualTriggerComponent',
          position: { x: 60, y: 200 },
          data: {
            inputs: {
              initial_payload: {
                transactions: [
                  { id: 'tx_101', amount: 250, status: 'approved' },
                  { id: 'tx_102', amount: 180, status: 'approved' },
                  { id: 'tx_103', amount: 420, status: 'approved' },
                  { id: 'tx_104', amount: 90, status: 'approved' }
                ],
                batch_size: 2
              }
            }
          }
        },
        {
          id: n2Id,
          type: 'LoopIteratorComponent',
          position: { x: 380, y: 200 },
          data: {
            inputs: {
              items_path: 'transactions',
              batch_size: 2,
              batch_index: 0
            }
          }
        },
        {
          id: n3Id,
          type: 'KeyValueStoreComponent',
          position: { x: 740, y: 200 },
          data: {
            inputs: {
              operation: 'increment',
              key: 'processed_batches_total',
              amount: 1,
              namespace: 'billing'
            }
          }
        },
        {
          id: n4Id,
          type: 'DiscordWebhookComponent',
          position: { x: 1080, y: 200 },
          data: {
            inputs: {
              webhook_url: 'https://discord.com/api/webhooks/00/xx',
              username: 'BatchProcessorBot',
              content: '📦 Lote de transações processado com sucesso!',
              embed_title: 'Métricas de Processamento em Lote',
              embed_description: 'Lote fatiado via Loop Iterator e contador atualizado no Key-Value Store.',
              embed_color: '#5865F2'
            }
          }
        }
      ]
      edges.value = [
        { id: 'e1', source: n1Id, sourceHandle: 'data', target: n2Id, targetHandle: 'items' },
        { id: 'e2', source: n2Id, sourceHandle: 'batch_info', target: n3Id, targetHandle: 'value' },
        { id: 'e3', source: n3Id, sourceHandle: 'result', target: n4Id, targetHandle: 'content' }
      ]
    } else if (templateType === 'resilient_try_catch_telegram_flow') {
      flowId.value = 'flow-resilient-try-catch-telegram'
      flowName.value = 'Pipeline Resiliente: Try/Catch & Telegram'
      flowDescription.value = 'Ingere webhook externo, mapeia e normaliza campos declarativamente, isola execução em Try/Catch e ramifica em sucesso vs. alerta imediato no Telegram.'
      const n1Id = 'wh-1'
      const n2Id = 'map-1'
      const n3Id = 'try-1'
      const n4Id = 'tf-ok'
      const n5Id = 'tg-err'
      nodes.value = [
        {
          id: n1Id,
          type: 'WebhookTriggerComponent',
          position: { x: 60, y: 200 },
          data: {
            inputs: {
              method: 'POST',
              auth_mode: 'none'
            }
          }
        },
        {
          id: n2Id,
          type: 'DataMapperComponent',
          position: { x: 380, y: 200 },
          data: {
            inputs: {
              field_mappings: {
                user_id: 'customer.id',
                email: 'customer.contact.email',
                plan: 'subscription.tier'
              },
              include_unmapped: false
            }
          }
        },
        {
          id: n3Id,
          type: 'TryCatchComponent',
          position: { x: 740, y: 200 },
          data: {
            inputs: {
              fallback_value: { recovered: true, mode: 'safe_mode' },
              catch_upstream_errors: true
            }
          }
        },
        {
          id: n4Id,
          type: 'JsonTransformComponent',
          position: { x: 1080, y: 100 },
          data: {
            inputs: {
              expression: "dict(status='processed', user=payload.get('user_id'), active=True)"
            }
          }
        },
        {
          id: n5Id,
          type: 'TelegramWebhookComponent',
          position: { x: 1080, y: 320 },
          data: {
            inputs: {
              bot_token: '123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11',
              chat_id: '-100123456789',
              text: '🚨 <b>ALERTA FLOWBUILD</b>: Falha interceptada no pipeline!\nDetalhes: Recuperado em modo fallback seguro.',
              parse_mode: 'HTML'
            }
          }
        }
      ]
      edges.value = [
        { id: 'e1', source: n1Id, sourceHandle: 'payload', target: n2Id, targetHandle: 'data' },
        { id: 'e2', source: n2Id, sourceHandle: 'mapped_data', target: n3Id, targetHandle: 'input_data' },
        { id: 'e3', source: n3Id, sourceHandle: 'success_branch', target: n4Id, targetHandle: 'input_data' },
        { id: 'e4', source: n3Id, sourceHandle: 'error_branch', target: n5Id, targetHandle: 'text' }
      ]
    } else {
      // Fallback: Default http_enrich
      loadTemplate('http_enrich')
      return
    }
    selectedNodeId.value = null
  }

  async function fetchSavedFlows(baseUrl: string = 'http://localhost:8000'): Promise<void> {
    try {
      const res = await fetch(`${baseUrl}/api/v1/flows`)
      if (res.ok) {
        savedFlows.value = await res.json()
      }
    } catch {
      // Ignore network errors in test mode
    }
  }

  async function promoteFlow(
    sourceId: string,
    targetEnvironment: Environment,
    targetVersion?: string,
    baseUrl: string = 'http://localhost:8000'
  ): Promise<boolean> {
    try {
      const res = await fetch(`${baseUrl}/api/v1/flows/${sourceId}/promote`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          target_environment: targetEnvironment,
          target_version: targetVersion,
        }),
      })
      if (res.ok) {
        await fetchSavedFlows(baseUrl)
        return true
      }
      return false
    } catch {
      return false
    }
  }

  async function saveFlowToBackend(
    active: boolean = true,
    baseUrl: string = 'http://localhost:8000'
  ): Promise<boolean> {
    isActive.value = active
    // Fail-safe: if in dev but ID has foreign env suffix, resolve to sourceFlowId
    if (currentEnvironment.value === 'dev' && sourceFlowId.value && (flowId.value.endsWith('-qa') || flowId.value.endsWith('-prd'))) {
      flowId.value = sourceFlowId.value
      sourceFlowId.value = null
    }
    const payload = toFlowPayload()
    try {
      const res = await fetch(`${baseUrl}/api/v1/flows`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ flow: payload, is_active: active, is_draft: isDraft.value }),
      })
      if (res.ok) {
        await fetchSavedFlows(baseUrl)
        return true
      }
      return false
    } catch {
      return false
    }
  }

  async function publishOrSaveFlow(
    active: boolean = true,
    baseUrl: string = 'http://localhost:8000'
  ): Promise<boolean> {
    version.value = bumpPatchVersion(version.value)
    isDraft.value = false
    isActive.value = active
    return await saveFlowToBackend(active, baseUrl)
  }

  async function deleteSavedFlow(
    id: string,
    baseUrl: string = 'http://localhost:8000'
  ): Promise<boolean> {
    try {
      const res = await fetch(`${baseUrl}/api/v1/flows/${id}`, { method: 'DELETE' })
      if (res.ok) {
        await fetchSavedFlows(baseUrl)
        return true
      }
      return false
    } catch {
      return false
    }
  }

  function saveToLocalStorage(): void {
    try {
      const payload = toFlowPayload()
      localStorage.setItem(
        'flowbuild_active_flow',
        JSON.stringify({
          flow: payload,
          is_active: isActive.value,
          timestamp: Date.now(),
        })
      )
    } catch {
      // Ignore storage errors in test or private mode
    }
  }

  function triggerAutoSave(debounceMs: number = 600): void {
    saveToLocalStorage()
    if (autoSaveTimeout) {
      clearTimeout(autoSaveTimeout)
    }
    autoSaveTimeout = setTimeout(() => {
      saveFlowToBackend(isActive.value)
    }, debounceMs)
  }

  async function loadPersistedFlow(baseUrl: string = 'http://localhost:8000'): Promise<boolean> {
    // 1. Try to fetch saved flows from backend database
    try {
      await fetchSavedFlows(baseUrl)
      if (savedFlows.value && savedFlows.value.length > 0) {
        const activeRec =
          savedFlows.value.find((f: any) => f.id === flowId.value) ||
          savedFlows.value.find((f: any) => f.is_active) ||
          savedFlows.value[0]

        if (activeRec && activeRec.flow_data && activeRec.flow_data.nodes?.length > 0) {
          loadFlow(activeRec.flow_data)
          isActive.value = activeRec.is_active ?? true
          isDraft.value = activeRec.is_draft ?? false
          saveToLocalStorage()
          return true
        }
      }
    } catch {
      // Backend not yet ready or offline
    }

    // 2. Fallback to localStorage cache
    try {
      const localStr = localStorage.getItem('flowbuild_active_flow')
      if (localStr) {
        const parsed = JSON.parse(localStr)
        if (parsed?.flow?.nodes?.length > 0) {
          loadFlow(parsed.flow)
          isActive.value = parsed.is_active ?? true
          isDraft.value = parsed.flow?.is_draft ?? false
          return true
        }
      }
    } catch {
      // Ignore parse error
    }

    // 3. Fallback: Initialize with rich default template
    loadTemplate('http_enrich')
    await saveFlowToBackend(true, baseUrl)
    return false
  }

  function hasTriggerNode(): boolean {
    if (!nodes.value || nodes.value.length === 0) return false
    return nodes.value.some((node) => {
      const typeLower = (node.type || '').toLowerCase()
      return typeLower.includes('trigger')
    })
  }

  function validateExecutionPreconditions(): { valid: boolean; error?: string } {
    if (!nodes.value || nodes.value.length === 0) {
      return {
        valid: false,
        error: 'O canvas está vazio. Adicione componentes ao fluxo antes de executar.',
      }
    }
    if (!hasTriggerNode()) {
      return {
        valid: false,
        error: 'O workflow precisa de pelo menos um nó Trigger inicial (ex: Disparo Manual, Webhook ou Agendamento/Cron) para ser executado.',
      }
    }
    return { valid: true }
  }

  return {
    flowId,
    flowName,
    flowDescription,
    currentEnvironment,
    currentFolder,
    version,
    sourceFlowId,
    isDraft,
    nodes,
    edges,
    selectedNodeId,
    selectedNode,
    isActive,
    savedFlows,
    flowsInCurrentEnvironment,
    flowsByFolder,
    setEnvironment,
    setFolder,
    promoteFlow,
    addNode,
    removeNode,
    addEdge,
    removeEdge,
    updateNodeInput,
    updateNodePosition,
    updateNodeExpanded,
    selectNode,
    toFlowPayload,
    loadFlow,
    loadTemplate,
    fetchSavedFlows,
    saveFlowToBackend,
    publishOrSaveFlow,
    deleteSavedFlow,
    triggerAutoSave,
    saveToLocalStorage,
    loadPersistedFlow,
    hasTriggerNode,
    validateExecutionPreconditions,
  }
})
