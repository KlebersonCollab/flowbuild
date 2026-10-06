import { describe, it, expect, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useFlowStore } from '../src/stores/flowStore'

describe('Draft Lifecycle, Version Bumping & Lineage Synchronization', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('marks flow as draft and inactive upon node change without altering version', () => {
    const store = useFlowStore()
    store.version = 'v1.0.0'
    store.isDraft = false
    store.isActive = true

    // Adding node flags draft and deactivates background execution
    store.addNode('ManualTriggerComponent', { x: 100, y: 100 })

    expect(store.isDraft).toBe(true)
    expect(store.isActive).toBe(false)
    expect(store.version).toBe('v1.0.0') // MUST NOT bump version on draft edit!
  })

  it('bumps semantic subversion and clears draft flag on explicit save', async () => {
    const store = useFlowStore()
    store.version = 'v1.0.0'
    store.isDraft = true
    store.isActive = false

    // Explicit save / publish
    await store.publishOrSaveFlow()

    expect(store.version).toBe('v1.0.1')
    expect(store.isDraft).toBe(false)

    // Another explicit save increments subversion again
    await store.publishOrSaveFlow()
    expect(store.version).toBe('v1.0.2')
  })

  it('synchronizes linked flows bidirectionally when switching environments', () => {
    const store = useFlowStore()

    const devFlow = {
      id: 'flow-orders-dev',
      name: 'Orders Flow',
      environment: 'dev' as const,
      version: 'v1.0.0',
      nodes: [],
      edges: [],
    }

    const qaFlow = {
      id: 'flow-orders-dev-qa',
      name: 'Orders Flow',
      environment: 'qa' as const,
      version: 'v1.1.0',
      source_flow_id: 'flow-orders-dev',
      nodes: [],
      edges: [],
    }

    store.savedFlows = [
      { id: devFlow.id, name: devFlow.name, environment: 'dev', version: 'v1.0.0', flow_data: devFlow },
      { id: qaFlow.id, name: qaFlow.name, environment: 'qa', version: 'v1.1.0', source_flow_id: 'flow-orders-dev', flow_data: qaFlow },
    ]

    // 1. Currently in QA with QA flow loaded
    store.loadFlow(qaFlow)
    store.currentEnvironment = 'qa'
    expect(store.flowId).toBe('flow-orders-dev-qa')

    // 2. Switch environment back to DEV
    store.setEnvironment('dev')

    // Canvas must automatically resolve and load the DEV parent flow!
    expect(store.currentEnvironment).toBe('dev')
    expect(store.flowId).toBe('flow-orders-dev')
    expect(store.version).toBe('v1.0.0')

    // 3. Switch environment forward to QA
    store.setEnvironment('qa')
    expect(store.currentEnvironment).toBe('qa')
    expect(store.flowId).toBe('flow-orders-dev-qa')
    expect(store.version).toBe('v1.1.0')
  })

  it('manages flow description and includes it in toFlowPayload and loadFlow', () => {
    const store = useFlowStore()
    store.flowDescription = 'Fluxo de conciliação financeira automática'

    const payload = store.toFlowPayload()
    expect(payload.description).toBe('Fluxo de conciliação financeira automática')

    store.loadFlow({
      id: 'f-1',
      name: 'Flow 1',
      description: 'Descrição carregada do backend',
      nodes: [],
      edges: [],
    })
    expect(store.flowDescription).toBe('Descrição carregada do backend')
  })
})
