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

  return {
    flowId,
    flowName,
    nodes,
    edges,
    selectedNodeId,
    selectedNode,
    addNode,
    removeNode,
    addEdge,
    removeEdge,
    updateNodeInput,
    selectNode,
    toFlowPayload,
    loadFlow,
  }
})
