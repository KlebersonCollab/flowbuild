import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useExecutionStore } from '../src/stores/executionStore'
import { useFlowStore } from '../src/stores/flowStore'

describe('Automation Suite Store & Retry Tests', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.restoreAllMocks()
  })

  it('executionStore handles retry in freeze and unfreeze modes', async () => {
    const store = useExecutionStore()

    const mockRetryResponse = {
      flowId: 'test-flow',
      status: 'completed',
      results: { n1: 100, n2: 200 },
      errors: {},
      duration: 12.5
    }

    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => mockRetryResponse
    } as any)

    // Test Freeze Retry
    const freezeResult = await store.retryExecution('exec-failed-1', 'freeze')
    expect(freezeResult.status).toBe('completed')
    expect(global.fetch).toHaveBeenCalledWith(
      'http://localhost:8000/api/v1/executions/exec-failed-1/retry?mode=freeze',
      expect.objectContaining({ method: 'POST' })
    )

    // Test Unfreeze Retry
    const unfreezeResult = await store.retryExecution('exec-failed-1', 'unfreeze')
    expect(unfreezeResult.status).toBe('completed')
    expect(global.fetch).toHaveBeenCalledWith(
      'http://localhost:8000/api/v1/executions/exec-failed-1/retry?mode=unfreeze',
      expect.objectContaining({ method: 'POST' })
    )
  })

  it('flowStore manages active state and saves flow to backend', async () => {
    const store = useFlowStore()
    store.flowId = 'flow-persisted-1'
    store.flowName = 'My Saved Flow'

    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({
        id: 'flow-persisted-1',
        name: 'My Saved Flow',
        is_active: true
      })
    } as any)

    const saved = await store.saveFlowToBackend(true)
    expect(saved).toBe(true)
    expect(global.fetch).toHaveBeenCalledWith(
      'http://localhost:8000/api/v1/flows',
      expect.objectContaining({
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      })
    )
  })

  it('executionStore.loadExecution populates nodeStates from history record and activates outputs tab', () => {
    const store = useExecutionStore()
    const historyRecord = {
      id: 'exec-hist-1',
      node_states: {
        'wh-1': { status: 'completed', output: { email: 'user@test.com' } },
        'tf-1': { status: 'completed', output: { received: true } }
      }
    }

    store.loadExecution(historyRecord)
    expect(store.activeDrawerTab).toBe('outputs')
    expect(store.nodeStates['wh-1'].status).toBe('completed')
    expect(store.nodeStates['wh-1'].output).toEqual({ email: 'user@test.com' })
    expect(store.nodeStates['tf-1'].output).toEqual({ received: true })
  })
})
