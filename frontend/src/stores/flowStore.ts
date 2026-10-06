import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { FlowNode, FlowEdge, FlowPosition, FlowModel } from '../types/flow'

export const useFlowStore = defineStore('flow', () => {
  const flowId = ref<string>('flow-current')
  const flowName = ref<string>('My Automation Workflow')
  const nodes = ref<FlowNode[]>([])
  const edges = ref<FlowEdge[]>([])
  const selectedNodeId = ref<string | null>(null)

  const selectedNode = computed(() => {
    if (!selectedNodeId.value) return null
    return nodes.value.find((n) => n.id === selectedNodeId.value) || null
  })

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
    return id
  }

  function removeNode(id: string): void {
    nodes.value = nodes.value.filter((n) => n.id !== id)
    edges.value = edges.value.filter((e) => e.source !== id && e.target !== id)
    if (selectedNodeId.value === id) {
      selectedNodeId.value = null
    }
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
    return id
  }

  function removeEdge(id: string): void {
    edges.value = edges.value.filter((e) => e.id !== id)
  }

  function updateNodeInput(nodeId: string, key: string, value: any): void {
    const node = nodes.value.find((n) => n.id === nodeId)
    if (node) {
      if (!node.data.inputs) {
        node.data.inputs = {}
      }
      node.data.inputs[key] = value
    }
  }

  function selectNode(nodeId: string | null): void {
    selectedNodeId.value = nodeId
  }

  function toFlowPayload(name?: string, description?: string): FlowModel {
    return {
      id: flowId.value,
      name: name || flowName.value,
      description: description || '',
      nodes: JSON.parse(JSON.stringify(nodes.value)),
      edges: JSON.parse(JSON.stringify(edges.value)),
    }
  }

  function loadFlow(flow: FlowModel): void {
    flowId.value = flow.id
    flowName.value = flow.name
    nodes.value = flow.nodes || []
    edges.value = flow.edges || []
    selectedNodeId.value = null
  }

  function loadTemplate(templateType: 'http_enrich' | 'webhook_flow' | 'python_pipeline'): void {
    if (templateType === 'http_enrich') {
      flowId.value = 'flow-http-enrich'
      flowName.value = 'Enriquecimento de Dados HTTP'
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
      edges.value = [
        { id: 'e1', source: n1Id, sourceHandle: 'data', target: n2Id, targetHandle: 'context' }
      ]
    } else {
      flowId.value = 'flow-webhook-transform'
      flowName.value = 'Recepção Webhook & Filtro'
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
    }
    selectedNodeId.value = null
  }

  const isActive = ref<boolean>(true)
  const savedFlows = ref<any[]>([])

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

  async function saveFlowToBackend(active: boolean = true, baseUrl: string = 'http://localhost:8000'): Promise<boolean> {
    isActive.value = active
    const payload = toFlowPayload()
    try {
      const res = await fetch(`${baseUrl}/api/v1/flows`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ flow: payload, is_active: active })
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

  async function deleteSavedFlow(id: string, baseUrl: string = 'http://localhost:8000'): Promise<boolean> {
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

  return {
    flowId,
    flowName,
    nodes,
    edges,
    selectedNodeId,
    selectedNode,
    isActive,
    savedFlows,
    addNode,
    removeNode,
    addEdge,
    removeEdge,
    updateNodeInput,
    selectNode,
    toFlowPayload,
    loadFlow,
    loadTemplate,
    fetchSavedFlows,
    saveFlowToBackend,
    deleteSavedFlow,
  }
})
