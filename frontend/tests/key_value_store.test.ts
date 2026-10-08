import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { setActivePinia, createPinia } from 'pinia'
import CustomNode from '../src/components/CustomNode.vue'
import ComponentPalette from '../src/components/ComponentPalette.vue'
import { useFlowStore } from '../src/stores/flowStore'
import { useRegistryStore } from '../src/stores/registryStore'
import type { ComponentDefinition } from '../src/types/flow'

const mockKeyValueStoreDef: ComponentDefinition = {
  name: 'KeyValueStoreComponent',
  displayName: 'Key-Value Store',
  category: 'Storage',
  description: 'Persists and manages cross-execution state, flags, and atomic counters across workflow runs.',
  icon: 'hard-drive',
  inputs: [
    { name: 'operation', type: 'select', label: 'Operation', default: 'get', options: ['get', 'set', 'delete', 'increment', 'list'], required: true, is_handle: false },
    { name: 'key', type: 'str', label: 'Key', default: 'my_key', required: true, is_handle: true },
    { name: 'value', type: 'dict', label: 'Value', default: '', required: false, is_handle: true },
    { name: 'namespace', type: 'str', label: 'Namespace', default: 'default', required: false, is_handle: true },
    { name: 'default_value', type: 'str', label: 'Default Fallback Value', default: '', required: false, is_handle: false },
    { name: 'amount', type: 'int', label: 'Increment Amount', default: 1, required: false, is_handle: false },
  ],
  outputs: [
    { name: 'result', label: 'Result', type: 'any', method: 'get_result' },
    { name: 'found', label: 'Found', type: 'bool', method: 'get_found' },
    { name: 'key', label: 'Key', type: 'str', method: 'get_key' },
    { name: 'previous_value', label: 'Previous Value', type: 'any', method: 'get_previous_value' },
  ],
}

describe('KeyValueStoreComponent Frontend Suite', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.restoreAllMocks()
    const registryStore = useRegistryStore()
    registryStore.setComponents([mockKeyValueStoreDef])
  })

  it('exposes KeyValueStoreComponent schema in registryStore', () => {
    const registryStore = useRegistryStore()
    const comp = registryStore.getComponent('KeyValueStoreComponent')

    expect(comp).toBeDefined()
    expect(comp?.displayName).toBe('Key-Value Store')
    expect(comp?.category).toBe('Storage')

    const outNames = comp?.outputs.map((o) => o.name)
    expect(outNames).toContain('result')
    expect(outNames).toContain('found')
    expect(outNames).toContain('key')
    expect(outNames).toContain('previous_value')

    const inpNames = comp?.inputs.map((i) => i.name)
    expect(inpNames).toContain('operation')
    expect(inpNames).toContain('key')
    expect(inpNames).toContain('value')
    expect(inpNames).toContain('namespace')
    expect(inpNames).toContain('amount')
  })

  it('updates KeyValueStoreComponent inputs and serializes in flow payload', () => {
    const flowStore = useFlowStore()
    const nodeId = flowStore.addNode('KeyValueStoreComponent', { x: 300, y: 180 }, {
      operation: 'increment',
      key: 'hits',
      amount: 5,
      namespace: 'ratelimit',
    })

    const node = flowStore.nodes.find((n) => n.id === nodeId)
    expect(node?.data.inputs.operation).toBe('increment')
    expect(node?.data.inputs.key).toBe('hits')
    expect(node?.data.inputs.amount).toBe(5)

    const payload = flowStore.toFlowPayload()
    const serialized = payload.nodes.find((n) => n.id === nodeId)
    expect(serialized?.data.inputs.operation).toBe('increment')
    expect(serialized?.data.inputs.namespace).toBe('ratelimit')
  })

  it('renders CustomNode with Key-Value Store title and ports', () => {
    const wrapper = mount(CustomNode, {
      props: {
        id: 'node-kv-1',
        type: 'KeyValueStoreComponent',
        data: {
          inputs: {
            operation: 'get',
            key: 'active_token',
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

    expect(wrapper.text()).toContain('Key-Value Store')
    expect(wrapper.text()).toContain('Result')
    expect(wrapper.text()).toContain('Found')
    expect(wrapper.text()).toContain('Key')
  })

  it('lists Key-Value Store in ComponentPalette under Storage category', () => {
    const wrapper = mount(ComponentPalette)
    expect(wrapper.text()).toContain('Storage')
    expect(wrapper.text()).toContain('Key-Value Store')
  })
})
