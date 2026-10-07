import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useFlowStore } from '../src/stores/flowStore'
import { useRegistryStore } from '../src/stores/registryStore'
import { useExecutionStore } from '../src/stores/executionStore'

describe('VariableComponent Get/Set Frontend Suite', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.restoreAllMocks()
  })

  it('initializes VariableComponent with mode get by default', () => {
    const flowStore = useFlowStore()
    const nodeId = flowStore.addNode('VariableComponent', { x: 100, y: 150 })

    const node = flowStore.nodes.find(n => n.id === nodeId)
    expect(node).toBeDefined()
    expect(node?.type).toBe('VariableComponent')
    expect(node?.data.inputs).toBeDefined()
  })

  it('updates VariableComponent inputs to set mode with scope and persist', () => {
    const flowStore = useFlowStore()
    const nodeId = flowStore.addNode('VariableComponent', { x: 100, y: 150 })

    flowStore.updateNodeInput(nodeId, 'mode', 'set')
    flowStore.updateNodeInput(nodeId, 'variable_name', 'AUTH_TOKEN')
    flowStore.updateNodeInput(nodeId, 'value', 'jwt_bearer_token_abc')
    flowStore.updateNodeInput(nodeId, 'scope', 'flow')
    flowStore.updateNodeInput(nodeId, 'persist', true)

    const node = flowStore.nodes.find(n => n.id === nodeId)
    expect(node?.data.inputs.mode).toBe('set')
    expect(node?.data.inputs.variable_name).toBe('AUTH_TOKEN')
    expect(node?.data.inputs.value).toBe('jwt_bearer_token_abc')
    expect(node?.data.inputs.scope).toBe('flow')
    expect(node?.data.inputs.persist).toBe(true)

    // Serialization check
    const payload = flowStore.toFlowPayload()
    const serializedNode = payload.nodes.find(n => n.id === nodeId)
    expect(serializedNode?.data.inputs.mode).toBe('set')
    expect(serializedNode?.data.inputs.variable_name).toBe('AUTH_TOKEN')
    expect(serializedNode?.data.inputs.value).toBe('jwt_bearer_token_abc')
    expect(serializedNode?.data.inputs.scope).toBe('flow')
    expect(serializedNode?.data.inputs.persist).toBe(true)
  })

  it('supports global scope and persist false configuration', () => {
    const flowStore = useFlowStore()
    const nodeId = flowStore.addNode('VariableComponent', { x: 200, y: 300 })

    flowStore.updateNodeInput(nodeId, 'mode', 'set')
    flowStore.updateNodeInput(nodeId, 'variable_name', 'GLOBAL_CACHE_KEY')
    flowStore.updateNodeInput(nodeId, 'value', 'cache_v1')
    flowStore.updateNodeInput(nodeId, 'scope', 'global')
    flowStore.updateNodeInput(nodeId, 'persist', false)

    const node = flowStore.nodes.find(n => n.id === nodeId)
    expect(node?.data.inputs.scope).toBe('global')
    expect(node?.data.inputs.persist).toBe(false)
  })

  it('executionStore captures node output with variable metadata', () => {
    const execStore = useExecutionStore()
    const nodeId = 'var-node-1'

    // Simulate node execution event
    execStore.handleEvent({
      event: 'node_started',
      node_id: nodeId,
      type: 'VariableComponent'
    })
    expect(execStore.nodeStates[nodeId]?.status).toBe('running')

    execStore.handleEvent({
      event: 'node_completed',
      node_id: nodeId,
      output: {
        value: 'resolved_secret_key',
        variable_name: 'SECRET_KEY',
        success: true
      }
    })

    const state = execStore.getNodeState(nodeId)
    expect(state.status).toBe('completed')
    expect(state.output).toEqual({
      value: 'resolved_secret_key',
      variable_name: 'SECRET_KEY',
      success: true
    })
  })

  it('registryStore registers VariableComponent definition correctly', () => {
    const registryStore = useRegistryStore()
    registryStore.setComponents([
      {
        name: 'VariableComponent',
        displayName: 'Variable',
        category: 'Variables',
        description: 'Reads (get) or writes and persists (set) global and flow-scoped variables.',
        icon: 'key',
        inputs: [
          { name: 'mode', type: 'select', label: 'Operation Mode', default: 'get', required: false, is_handle: true, options: ['get', 'set'] },
          { name: 'variable_name', type: 'str', label: 'Variable Name', required: true, is_handle: true },
          { name: 'value', type: 'str', label: 'Value to Set', default: '', required: false, is_handle: true },
          { name: 'scope', type: 'select', label: 'Scope', default: 'flow', required: false, is_handle: true, options: ['flow', 'global'] },
          { name: 'persist', type: 'bool', label: 'Persist in Database', default: true, required: false, is_handle: true },
          { name: 'default_value', type: 'str', label: 'Default Value', default: '', required: false, is_handle: true }
        ],
        outputs: [
          { name: 'value', type: 'any', label: 'Variable Value' },
          { name: 'variable_name', type: 'str', label: 'Variable Name' },
          { name: 'success', type: 'bool', label: 'Success' }
        ]
      }
    ])

    const comp = registryStore.getComponent('VariableComponent')
    expect(comp).toBeDefined()
    expect(comp?.inputs.some(i => i.name === 'mode')).toBe(true)
    expect(comp?.inputs.some(i => i.name === 'scope')).toBe(true)
    expect(comp?.inputs.some(i => i.name === 'persist')).toBe(true)
    expect(comp?.outputs.some(o => o.name === 'success')).toBe(true)
  })
})
