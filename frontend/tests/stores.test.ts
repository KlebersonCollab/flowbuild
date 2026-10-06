import { describe, it, expect, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useFlowStore } from '../src/stores/flowStore'
import { useRegistryStore } from '../src/stores/registryStore'
import { useExecutionStore } from '../src/stores/executionStore'
import type { ComponentDefinition } from '../src/types/flow'

describe('Pinia Stores Test Suite', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('useFlowStore adds node, updates input and serializes flow payload', () => {
    const flowStore = useFlowStore()
    expect(flowStore.nodes.length).toBe(0)

    const nodeId = flowStore.addNode('HttpRequestComponent', { x: 150, y: 200 }, { url: 'https://api.test' })
    expect(flowStore.nodes.length).toBe(1)
    expect(flowStore.nodes[0].id).toBe(nodeId)
    expect(flowStore.nodes[0].data.inputs.url).toBe('https://api.test')

    flowStore.updateNodeInput(nodeId, 'url', 'https://updated.test')
    expect(flowStore.nodes[0].data.inputs.url).toBe('https://updated.test')

    const node2Id = flowStore.addNode('JsonTransformComponent', { x: 400, y: 200 })
    flowStore.addEdge({
      source: nodeId,
      sourceHandle: 'data',
      target: node2Id,
      targetHandle: 'input_data',
    })
    expect(flowStore.edges.length).toBe(1)

    const payload = flowStore.toFlowPayload('Test Flow')
    expect(payload.name).toBe('Test Flow')
    expect(payload.nodes.length).toBe(2)
    expect(payload.edges.length).toBe(1)
    expect(payload.edges[0].source).toBe(nodeId)
  })

  it('useRegistryStore groups components by category', () => {
    const registryStore = useRegistryStore()
    const mockComponents: ComponentDefinition[] = [
      {
        name: 'ManualTriggerComponent',
        displayName: 'Manual Trigger',
        category: 'Triggers',
        description: 'Trigger flow',
        icon: 'play',
        inputs: [],
        outputs: [{ name: 'data', label: 'Data', type: 'dict', method: 'run' }]
      },
      {
        name: 'HttpRequestComponent',
        displayName: 'HTTP Request',
        category: 'Actions',
        description: 'Send HTTP request',
        icon: 'globe',
        inputs: [],
        outputs: []
      }
    ]

    registryStore.setComponents(mockComponents)
    expect(registryStore.components.length).toBe(2)

    const categories = registryStore.categorizedComponents
    expect(categories['Triggers'].length).toBe(1)
    expect(categories['Actions'].length).toBe(1)
    expect(registryStore.getComponent('ManualTriggerComponent')?.displayName).toBe('Manual Trigger')
  })

  it('useExecutionStore updates node states from execution events', () => {
    const executionStore = useExecutionStore()
    expect(executionStore.isRunning).toBe(false)

    executionStore.handleEvent({ event: 'flow_started', flow_id: 'flow-1' })
    expect(executionStore.isRunning).toBe(true)

    executionStore.handleEvent({ event: 'node_started', node_id: 'n1', type: 'HttpRequestComponent' })
    expect(executionStore.getNodeState('n1').status).toBe('running')

    executionStore.handleEvent({ event: 'node_completed', node_id: 'n1', output: { status: 200 } })
    expect(executionStore.getNodeState('n1').status).toBe('completed')
    expect(executionStore.getNodeState('n1').output).toEqual({ status: 200 })

    executionStore.handleEvent({ event: 'node_failed', node_id: 'n2', error: 'Connection refused' })
    expect(executionStore.getNodeState('n2').status).toBe('failed')
    expect(executionStore.getNodeState('n2').error).toBe('Connection refused')

    executionStore.handleEvent({ event: 'flow_completed', status: 'completed' })
    expect(executionStore.isRunning).toBe(false)
  })
})
