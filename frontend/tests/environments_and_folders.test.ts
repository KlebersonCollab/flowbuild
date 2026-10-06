import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useFlowStore } from '../src/stores/flowStore'
import { useVariablesStore } from '../src/stores/variablesStore'

describe('Folders and Multi-Environment Promotion Suite', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.restoreAllMocks()
    localStorage.clear()
  })

  it('flowStore manages currentEnvironment and filters saved flows by environment', () => {
    const store = useFlowStore()
    expect(store.currentEnvironment).toBe('dev')

    store.savedFlows = [
      {
        id: 'flow-dev-1',
        name: 'Order Dev',
        folder: 'Financeiro',
        environment: 'dev',
        version: 'v1.0.0',
        is_active: true,
        flow_data: { id: 'flow-dev-1', name: 'Order Dev', nodes: [], edges: [] },
      },
      {
        id: 'flow-qa-1',
        name: 'Order QA',
        folder: 'Financeiro',
        environment: 'qa',
        version: 'v1.1.0',
        is_active: true,
        flow_data: { id: 'flow-qa-1', name: 'Order QA', nodes: [], edges: [] },
      },
    ]

    // In dev:
    expect(store.flowsInCurrentEnvironment.length).toBe(1)
    expect(store.flowsInCurrentEnvironment[0].id).toBe('flow-dev-1')

    // Switch environment to QA
    store.setEnvironment('qa')
    expect(store.currentEnvironment).toBe('qa')
    expect(store.flowsInCurrentEnvironment.length).toBe(1)
    expect(store.flowsInCurrentEnvironment[0].id).toBe('flow-qa-1')
  })

  it('flowStore groups flows by folder correctly', () => {
    const store = useFlowStore()
    store.savedFlows = [
      {
        id: 'f1',
        name: 'Flow 1',
        folder: 'Financeiro',
        environment: 'dev',
        is_active: true,
        flow_data: { id: 'f1', name: 'Flow 1', nodes: [], edges: [] },
      },
      {
        id: 'f2',
        name: 'Flow 2',
        folder: 'Vendas',
        environment: 'dev',
        is_active: true,
        flow_data: { id: 'f2', name: 'Flow 2', nodes: [], edges: [] },
      },
      {
        id: 'f3',
        name: 'Flow 3',
        folder: 'Financeiro',
        environment: 'dev',
        is_active: true,
        flow_data: { id: 'f3', name: 'Flow 3', nodes: [], edges: [] },
      },
      {
        id: 'f4',
        name: 'Flow 4',
        // No folder provided -> defaults to Geral
        environment: 'dev',
        is_active: true,
        flow_data: { id: 'f4', name: 'Flow 4', nodes: [], edges: [] },
      },
    ]

    const grouped = store.flowsByFolder
    expect(grouped['Financeiro'].length).toBe(2)
    expect(grouped['Vendas'].length).toBe(1)
    expect(grouped['Geral'].length).toBe(1)
  })

  it('flowStore promoteFlow calls API and refreshes savedFlows', async () => {
    const store = useFlowStore()
    const mockPromoted = {
      id: 'f1-qa',
      name: 'Flow 1',
      folder: 'Financeiro',
      environment: 'qa',
      version: 'v1.1.0',
      source_flow_id: 'f1',
      is_active: true,
      flow_data: { id: 'f1-qa', name: 'Flow 1', nodes: [], edges: [] },
    }

    global.fetch = vi.fn().mockImplementation((url: string) => {
      if (url.includes('/promote')) {
        return Promise.resolve({
          ok: true,
          json: async () => mockPromoted,
        })
      }
      return Promise.resolve({
        ok: true,
        json: async () => [mockPromoted],
      })
    })

    const ok = await store.promoteFlow('f1', 'qa', 'v1.1.0')
    expect(ok).toBe(true)
    expect(global.fetch).toHaveBeenCalledWith(
      expect.stringContaining('/api/v1/flows/f1/promote'),
      expect.objectContaining({
        method: 'POST',
        body: JSON.stringify({ target_environment: 'qa', target_version: 'v1.1.0' }),
      })
    )
  })

  it('variablesStore supports environment-scoped variable management', async () => {
    const varStore = useVariablesStore()
    varStore.currentFlowId = 'flow-123'

    varStore.variables = [
      { id: 'v1', key: 'API_URL', value: 'https://dev.api', scope: 'global', environment: 'dev' },
      { id: 'v2', key: 'API_URL', value: 'https://qa.api', scope: 'global', environment: 'qa' },
      { id: 'v3', key: 'SHARED', value: 'all-env-val', scope: 'global', environment: 'all' },
    ]

    // Variables for DEV: contains DEV + all
    const devVars = varStore.getVariablesForEnvironment('dev')
    expect(devVars.length).toBe(2)
    expect(devVars.map((v) => v.value)).toContain('https://dev.api')
    expect(devVars.map((v) => v.value)).toContain('all-env-val')

    // Variables for QA: contains QA + all
    const qaVars = varStore.getVariablesForEnvironment('qa')
    expect(qaVars.length).toBe(2)
    expect(qaVars.map((v) => v.value)).toContain('https://qa.api')
    expect(qaVars.map((v) => v.value)).toContain('all-env-val')
  })
})
