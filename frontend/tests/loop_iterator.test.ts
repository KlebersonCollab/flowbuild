import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { setActivePinia, createPinia } from 'pinia'
import CustomNode from '../src/components/CustomNode.vue'
import ComponentPalette from '../src/components/ComponentPalette.vue'
import { useFlowStore } from '../src/stores/flowStore'
import { useRegistryStore } from '../src/stores/registryStore'
import type { ComponentDefinition } from '../src/types/flow'

const mockLoopIteratorDef: ComponentDefinition = {
  name: 'LoopIteratorComponent',
  displayName: 'Loop Iterator',
  category: 'Logic',
  description: 'Partitions collections into manageable batches, slices subsets, and emits iteration metrics without violating DAG acyclicity.',
  icon: 'repeat',
  inputs: [
    { name: 'items', type: 'dict', label: 'Collection Items', default: [], required: true, is_handle: true },
    { name: 'items_path', type: 'str', label: 'Items Array Path', default: '', required: false, is_handle: true },
    { name: 'batch_size', type: 'int', label: 'Batch Size', default: 10, required: false, is_handle: false },
    { name: 'batch_index', type: 'int', label: 'Batch Index (0-based)', default: 0, required: false, is_handle: false },
    { name: 'max_batches', type: 'int', label: 'Max Batches (0 = unlimited)', default: 0, required: false, is_handle: false },
  ],
  outputs: [
    { name: 'current_batch', label: 'Current Batch', type: 'list', method: 'get_current_batch' },
    { name: 'batches', label: 'All Batches', type: 'list', method: 'get_batches' },
    { name: 'total_items', label: 'Total Items', type: 'int', method: 'get_total_items' },
    { name: 'total_batches', label: 'Total Batches', type: 'int', method: 'get_total_batches' },
    { name: 'has_more', label: 'Has More Batches', type: 'bool', method: 'get_has_more' },
    { name: 'batch_info', label: 'Batch Info', type: 'dict', method: 'get_batch_info' },
  ],
}

describe('LoopIteratorComponent Frontend Suite', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.restoreAllMocks()
    const registryStore = useRegistryStore()
    registryStore.setComponents([mockLoopIteratorDef])
  })

  it('exposes LoopIteratorComponent schema in registryStore', () => {
    const registryStore = useRegistryStore()
    const comp = registryStore.getComponent('LoopIteratorComponent')

    expect(comp).toBeDefined()
    expect(comp?.displayName).toBe('Loop Iterator')
    expect(comp?.category).toBe('Logic')

    const outNames = comp?.outputs.map((o) => o.name)
    expect(outNames).toContain('current_batch')
    expect(outNames).toContain('batches')
    expect(outNames).toContain('total_items')
    expect(outNames).toContain('total_batches')
    expect(outNames).toContain('has_more')
    expect(outNames).toContain('batch_info')

    const inpNames = comp?.inputs.map((i) => i.name)
    expect(inpNames).toContain('items')
    expect(inpNames).toContain('items_path')
    expect(inpNames).toContain('batch_size')
    expect(inpNames).toContain('batch_index')
    expect(inpNames).toContain('max_batches')
  })

  it('updates LoopIteratorComponent inputs and serializes in flow payload', () => {
    const flowStore = useFlowStore()
    const nodeId = flowStore.addNode('LoopIteratorComponent', { x: 280, y: 190 }, {
      items: [1, 2, 3],
      batch_size: 5,
      batch_index: 0,
      max_batches: 2,
    })

    const node = flowStore.nodes.find((n) => n.id === nodeId)
    expect(node?.data.inputs.batch_size).toBe(5)
    expect(node?.data.inputs.max_batches).toBe(2)

    const payload = flowStore.toFlowPayload()
    const serialized = payload.nodes.find((n) => n.id === nodeId)
    expect(serialized?.data.inputs.batch_size).toBe(5)
    expect(serialized?.data.inputs.items).toEqual([1, 2, 3])
  })

  it('renders CustomNode with Loop Iterator title and ports', () => {
    const wrapper = mount(CustomNode, {
      props: {
        id: 'node-loop-1',
        type: 'LoopIteratorComponent',
        data: {
          inputs: {
            batch_size: 10,
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

    expect(wrapper.text()).toContain('Loop Iterator')
    expect(wrapper.text()).toContain('Current Batch')
    expect(wrapper.text()).toContain('Total Batches')
    expect(wrapper.text()).toContain('Has More Batches')
  })

  it('lists Loop Iterator in ComponentPalette under Logic category', () => {
    const wrapper = mount(ComponentPalette)
    expect(wrapper.text()).toContain('Logic')
    expect(wrapper.text()).toContain('Loop Iterator')
  })
})
