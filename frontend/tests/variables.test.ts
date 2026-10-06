import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useVariablesStore } from '../src/stores/variablesStore'
import { useFlowStore } from '../src/stores/flowStore'

describe('Variables Store & Persistence Test Suite', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.restoreAllMocks()
  })

  it('useVariablesStore classifies global and flow-scoped variables', () => {
    const varStore = useVariablesStore()
    varStore.currentFlowId = 'flow-123'

    varStore.variables = [
      { id: 'v1', key: 'GLOBAL_URL', value: 'https://global.com', scope: 'global' },
      { id: 'v2', key: 'LOCAL_TOKEN', value: 'secret-xyz', scope: 'flow', flow_id: 'flow-123' },
      { id: 'v3', key: 'OTHER_FLOW_VAR', value: 'other', scope: 'flow', flow_id: 'flow-999' }
    ]

    expect(varStore.globalVariables.length).toBe(1)
    expect(varStore.globalVariables[0].key).toBe('GLOBAL_URL')

    expect(varStore.flowVariables.length).toBe(1)
    expect(varStore.flowVariables[0].key).toBe('LOCAL_TOKEN')
  })

  it('useVariablesStore createVariable adds variable via mock API', async () => {
    const varStore = useVariablesStore()
    varStore.currentFlowId = 'flow-123'

    const mockCreated = {
      id: 'v-new',
      key: 'API_KEY',
      value: 'val-123',
      scope: 'global',
      is_secret: false
    }

    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => mockCreated
    } as any)

    const result = await varStore.createVariable({
      key: 'API_KEY',
      value: 'val-123',
      scope: 'global'
    })

    expect(result).toBe(true)
    expect(varStore.variables.some(v => v.id === 'v-new')).toBe(true)
  })

  it('useVariablesStore updateVariable and deleteVariable mutate local state', async () => {
    const varStore = useVariablesStore()
    varStore.variables = [
      { id: 'v-1', key: 'URL', value: 'old-url', scope: 'global' }
    ]

    // Update
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ id: 'v-1', key: 'URL', value: 'new-url', scope: 'global' })
    } as any)

    const updated = await varStore.updateVariable('v-1', 'new-url')
    expect(updated).toBe(true)
    expect(varStore.variables[0].value).toBe('new-url')

    // Delete
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({ deleted: true })
    } as any)

    const deleted = await varStore.deleteVariable('v-1')
    expect(deleted).toBe(true)
    expect(varStore.variables.length).toBe(0)
  })

  it('useFlowStore updates node position and reflects in payload serialization', () => {
    const flowStore = useFlowStore()
    const nodeId = flowStore.addNode('HttpRequestComponent', { x: 100, y: 100 })

    expect(flowStore.nodes[0].position).toEqual({ x: 100, y: 100 })

    // Update position via store method
    flowStore.updateNodePosition(nodeId, { x: 450, y: 600 })

    expect(flowStore.nodes[0].position).toEqual({ x: 450, y: 600 })

    const payload = flowStore.toFlowPayload()
    expect(payload.nodes[0].position).toEqual({ x: 450, y: 600 })
  })

  it('useFlowStore persists node expanded format and restores persisted flow', async () => {
    const flowStore = useFlowStore()
    const nodeId = flowStore.addNode('HttpRequestComponent', { x: 200, y: 250 })

    // Collapse node format
    flowStore.updateNodeExpanded(nodeId, false)
    expect(flowStore.nodes[0].data.expanded).toBe(false)

    const payload = flowStore.toFlowPayload()
    expect(payload.nodes[0].data.expanded).toBe(false)

    // Mock backend returning saved flow with custom node format and position
    const mockSavedFlows = [
      {
        id: 'flow-persisted-1',
        name: 'My Restored Flow',
        is_active: true,
        flow_data: {
          id: 'flow-persisted-1',
          name: 'My Restored Flow',
          nodes: [
            {
              id: 'restored-node-1',
              type: 'HttpRequestComponent',
              position: { x: 777, y: 888 },
              data: {
                expanded: false,
                inputs: { url: 'https://persisted-api.com' }
              }
            }
          ],
          edges: []
        }
      }
    ]

    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => mockSavedFlows
    } as any)

    const restored = await flowStore.loadPersistedFlow()
    expect(restored).toBe(true)
    expect(flowStore.flowId).toBe('flow-persisted-1')
    expect(flowStore.nodes.length).toBe(1)
    expect(flowStore.nodes[0].position).toEqual({ x: 777, y: 888 })
    expect(flowStore.nodes[0].data.expanded).toBe(false)
    expect(flowStore.nodes[0].data.inputs.url).toBe('https://persisted-api.com')
  })
})
