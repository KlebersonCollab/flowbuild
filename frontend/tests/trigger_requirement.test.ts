import { describe, it, expect, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useFlowStore } from '../src/stores/flowStore'

describe('Mandatory Trigger Node Requirement', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('detects absence of trigger when flow has no nodes or only action nodes', () => {
    const store = useFlowStore()
    expect(store.hasTriggerNode()).toBe(false)

    store.addNode('HttpRequestComponent', { x: 100, y: 100 })
    store.addNode('JsonTransformComponent', { x: 300, y: 100 })
    expect(store.hasTriggerNode()).toBe(false)

    const validation = store.validateExecutionPreconditions()
    expect(validation.valid).toBe(false)
    expect(validation.error).toContain('Trigger')
  })

  it('detects presence of trigger when ManualTrigger, WebhookTrigger, or CronTrigger exists', () => {
    const store = useFlowStore()
    store.addNode('HttpRequestComponent', { x: 100, y: 100 })
    expect(store.hasTriggerNode()).toBe(false)

    store.addNode('ManualTriggerComponent', { x: 50, y: 100 })
    expect(store.hasTriggerNode()).toBe(true)

    const validation = store.validateExecutionPreconditions()
    expect(validation.valid).toBe(true)
    expect(validation.error).toBeUndefined()
  })

  it('validates pre-configured templates all have triggers', () => {
    const store = useFlowStore()

    store.loadTemplate('http_enrich')
    expect(store.hasTriggerNode()).toBe(true)
    expect(store.validateExecutionPreconditions().valid).toBe(true)

    store.loadTemplate('webhook_flow')
    expect(store.hasTriggerNode()).toBe(true)
    expect(store.validateExecutionPreconditions().valid).toBe(true)

    store.loadTemplate('python_pipeline')
    expect(store.hasTriggerNode()).toBe(true)
    expect(store.validateExecutionPreconditions().valid).toBe(true)
  })
})
