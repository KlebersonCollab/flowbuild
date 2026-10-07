import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useFlowStore } from '../src/stores/flowStore'
import { useRegistryStore } from '../src/stores/registryStore'

describe('VariableComponent Environment Scoping Frontend Suite', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.restoreAllMocks()
  })

  it('updates VariableComponent with target environment prd', () => {
    const flowStore = useFlowStore()
    const nodeId = flowStore.addNode('VariableComponent', { x: 100, y: 150 })

    flowStore.updateNodeInput(nodeId, 'mode', 'set')
    flowStore.updateNodeInput(nodeId, 'variable_name', 'PROD_DB_URL')
    flowStore.updateNodeInput(nodeId, 'value', 'postgres://prd:5432/db')
    flowStore.updateNodeInput(nodeId, 'scope', 'global')
    flowStore.updateNodeInput(nodeId, 'environment', 'prd')
    flowStore.updateNodeInput(nodeId, 'persist', true)

    const node = flowStore.nodes.find(n => n.id === nodeId)
    expect(node?.data.inputs.environment).toBe('prd')
    expect(node?.data.inputs.scope).toBe('global')

    // Serialization check
    const payload = flowStore.toFlowPayload()
    const serialized = payload.nodes.find(n => n.id === nodeId)
    expect(serialized?.data.inputs.environment).toBe('prd')
    expect(serialized?.data.inputs.scope).toBe('global')
  })

  it('supports environment all and current defaults', () => {
    const flowStore = useFlowStore()
    const nodeId = flowStore.addNode('VariableComponent', { x: 200, y: 250 })

    // Defaults
    flowStore.updateNodeInput(nodeId, 'mode', 'get')
    flowStore.updateNodeInput(nodeId, 'variable_name', 'API_KEY')
    flowStore.updateNodeInput(nodeId, 'environment', 'current')

    const node = flowStore.nodes.find(n => n.id === nodeId)
    expect(node?.data.inputs.environment).toBe('current')

    // Switch to all
    flowStore.updateNodeInput(nodeId, 'environment', 'all')
    expect(node?.data.inputs.environment).toBe('all')
  })

  it('registryStore exposes environment options for VariableComponent', () => {
    const registryStore = useRegistryStore()
    registryStore.setComponents([
      {
        name: 'VariableComponent',
        displayName: 'Variable',
        category: 'Variables',
        description: 'Reads (get) or writes and persists (set) global and flow-scoped variables across environments.',
        icon: 'key',
        inputs: [
          { name: 'mode', type: 'select', label: 'Operation Mode', default: 'get', required: false, is_handle: true, options: ['get', 'set'] },
          { name: 'variable_name', type: 'str', label: 'Variable Name', required: true, is_handle: true },
          { name: 'value', type: 'str', label: 'Value to Set', default: '', required: false, is_handle: true },
          { name: 'scope', type: 'select', label: 'Scope', default: 'flow', required: false, is_handle: true, options: ['flow', 'global'] },
          { name: 'environment', type: 'select', label: 'Environment', default: 'current', required: false, is_handle: true, options: ['current', 'all', 'dev', 'qa', 'prd'] },
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
    const envInput = comp?.inputs.find(i => i.name === 'environment')
    expect(envInput).toBeDefined()
    expect(envInput?.options).toEqual(['current', 'all', 'dev', 'qa', 'prd'])
    expect(envInput?.default).toBe('current')
  })
})
