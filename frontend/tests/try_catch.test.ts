import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { setActivePinia, createPinia } from 'pinia'
import CustomNode from '../src/components/CustomNode.vue'
import ComponentPalette from '../src/components/ComponentPalette.vue'
import { useFlowStore } from '../src/stores/flowStore'
import { useRegistryStore } from '../src/stores/registryStore'
import type { ComponentDefinition } from '../src/types/flow'

const mockTryCatchDef: ComponentDefinition = {
  name: 'TryCatchComponent',
  displayName: 'Try / Catch',
  category: 'Logic',
  description: 'Catches upstream failures, provides fallback values, and routes execution between success and error branches.',
  icon: 'shield-alert',
  inputs: [
    { name: 'input_data', type: 'dict', label: 'Input Data', default: {}, required: false, is_handle: true },
    { name: 'fallback_value', type: 'dict', label: 'Fallback Value', default: {}, required: false, is_handle: false },
    { name: 'catch_upstream_errors', type: 'bool', label: 'Catch Upstream Errors', default: true, required: false, is_handle: false },
    { name: 'error_message', type: 'str', label: 'Error Message', default: '', required: false, is_handle: false },
  ],
  outputs: [
    { name: 'success_branch', label: 'Success Branch', type: 'any', method: 'get_success_branch' },
    { name: 'error_branch', label: 'Error Branch', type: 'dict', method: 'get_error_branch' },
    { name: 'result', label: 'Result (Success or Fallback)', type: 'any', method: 'get_result' },
    { name: 'has_error', label: 'Has Error', type: 'bool', method: 'get_has_error' },
    { name: 'error_details', label: 'Error Details', type: 'str', method: 'get_error_details' },
  ],
}

describe('TryCatchComponent Frontend Suite', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.restoreAllMocks()
    const registryStore = useRegistryStore()
    registryStore.setComponents([mockTryCatchDef])
  })

  it('exposes TryCatchComponent schema in registryStore', () => {
    const registryStore = useRegistryStore()
    const comp = registryStore.getComponent('TryCatchComponent')

    expect(comp).toBeDefined()
    expect(comp?.displayName).toBe('Try / Catch')
    expect(comp?.category).toBe('Logic')

    const outNames = comp?.outputs.map((o) => o.name)
    expect(outNames).toContain('success_branch')
    expect(outNames).toContain('error_branch')
    expect(outNames).toContain('result')
    expect(outNames).toContain('has_error')
    expect(outNames).toContain('error_details')

    const inpNames = comp?.inputs.map((i) => i.name)
    expect(inpNames).toContain('input_data')
    expect(inpNames).toContain('fallback_value')
    expect(inpNames).toContain('catch_upstream_errors')
    expect(inpNames).toContain('error_message')
  })

  it('updates TryCatchComponent inputs and serializes in flow payload', () => {
    const flowStore = useFlowStore()
    const nodeId = flowStore.addNode('TryCatchComponent', { x: 300, y: 200 }, {
      fallback_value: { status: 'fallback', code: 500 },
      catch_upstream_errors: true,
      error_message: 'Simulated failure',
    })

    const node = flowStore.nodes.find((n) => n.id === nodeId)
    expect(node?.data.inputs.fallback_value).toEqual({ status: 'fallback', code: 500 })
    expect(node?.data.inputs.catch_upstream_errors).toBe(true)

    const payload = flowStore.toFlowPayload()
    const serialized = payload.nodes.find((n) => n.id === nodeId)
    expect(serialized?.data.inputs.fallback_value).toEqual({ status: 'fallback', code: 500 })
    expect(serialized?.data.inputs.error_message).toBe('Simulated failure')
  })

  it('renders CustomNode with Try / Catch title and branches', () => {
    const wrapper = mount(CustomNode, {
      props: {
        id: 'node-tc-1',
        type: 'TryCatchComponent',
        data: {
          inputs: {
            catch_upstream_errors: true,
          },
          expanded: true,
        },
      },
      global: {
        stubs: {
          Handle: {
            template: '<div class="vue-flow-handle" :data-id="id" />',
            props: ['id', 'type', 'position'],
          },
        },
      },
    })

    expect(wrapper.text()).toContain('Try / Catch')
    expect(wrapper.text()).toContain('Success Branch')
    expect(wrapper.text()).toContain('Error Branch')
  })

  it('lists Try / Catch in ComponentPalette under Logic category', () => {
    const wrapper = mount(ComponentPalette)
    expect(wrapper.text()).toContain('Logic')
    expect(wrapper.text()).toContain('Try / Catch')
  })
})
