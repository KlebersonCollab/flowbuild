import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { setActivePinia, createPinia } from 'pinia'
import CustomNode from '../src/components/CustomNode.vue'
import ComponentPalette from '../src/components/ComponentPalette.vue'
import { useFlowStore } from '../src/stores/flowStore'
import { useRegistryStore } from '../src/stores/registryStore'
import type { ComponentDefinition } from '../src/types/flow'

const mockAggregatorDef: ComponentDefinition = {
  name: 'DataAggregatorComponent',
  displayName: 'Data Aggregator',
  category: 'Transform',
  description: 'Calculates mathematical and statistical aggregations (sum, avg, min, max, count, concat, group_by) on collections.',
  icon: 'calculator',
  inputs: [
    { name: 'items', type: 'dict', label: 'Items Collection', default: [], required: true, is_handle: true },
    { name: 'items_path', type: 'str', label: 'Items Array Path', default: '', required: false, is_handle: true },
    { name: 'field', type: 'str', label: 'Target Field Path', default: '', required: false, is_handle: true },
    { name: 'operation', type: 'str', label: 'Aggregation Operation', default: 'all', required: false, is_handle: false },
    { name: 'group_by', type: 'str', label: 'Group By Field', default: '', required: false, is_handle: true },
    { name: 'delimiter', type: 'str', label: 'Concat Delimiter', default: ', ', required: false, is_handle: false },
  ],
  outputs: [
    { name: 'result', label: 'Result', type: 'any', method: 'get_result' },
    { name: 'summary', label: 'Summary', type: 'dict', method: 'get_summary' },
    { name: 'count', label: 'Count', type: 'int', method: 'get_count' },
  ],
}

describe('DataAggregatorComponent Frontend Suite', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.restoreAllMocks()
    const registryStore = useRegistryStore()
    registryStore.setComponents([mockAggregatorDef])
  })

  it('exposes DataAggregatorComponent schema in registryStore', () => {
    const registryStore = useRegistryStore()
    const comp = registryStore.getComponent('DataAggregatorComponent')

    expect(comp).toBeDefined()
    expect(comp?.displayName).toBe('Data Aggregator')
    expect(comp?.category).toBe('Transform')

    const outNames = comp?.outputs.map((o) => o.name)
    expect(outNames).toContain('result')
    expect(outNames).toContain('summary')
    expect(outNames).toContain('count')

    const inpNames = comp?.inputs.map((i) => i.name)
    expect(inpNames).toContain('items')
    expect(inpNames).toContain('field')
    expect(inpNames).toContain('operation')
    expect(inpNames).toContain('group_by')
  })

  it('updates DataAggregatorComponent inputs and serializes in flow payload', () => {
    const flowStore = useFlowStore()
    const nodeId = flowStore.addNode('DataAggregatorComponent', { x: 250, y: 180 }, {
      items: [{ amount: 100 }, { amount: 200 }],
      field: 'amount',
      operation: 'sum',
      group_by: 'category',
    })

    const node = flowStore.nodes.find((n) => n.id === nodeId)
    expect(node?.data.inputs.field).toBe('amount')
    expect(node?.data.inputs.operation).toBe('sum')
    expect(node?.data.inputs.group_by).toBe('category')

    const payload = flowStore.toFlowPayload()
    const serialized = payload.nodes.find((n) => n.id === nodeId)
    expect(serialized?.data.inputs.field).toBe('amount')
    expect(serialized?.data.inputs.operation).toBe('sum')
  })

  it('renders CustomNode with Data Aggregator title and ports', () => {
    const wrapper = mount(CustomNode, {
      props: {
        id: 'node-agg-1',
        type: 'DataAggregatorComponent',
        data: {
          inputs: {
            field: 'price',
            operation: 'avg',
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

    expect(wrapper.text()).toContain('Data Aggregator')
    expect(wrapper.text()).toContain('Result')
    expect(wrapper.text()).toContain('Summary')
    expect(wrapper.text()).toContain('Count')
  })

  it('lists Data Aggregator in ComponentPalette under Transform category', () => {
    const wrapper = mount(ComponentPalette)
    expect(wrapper.text()).toContain('Transform')
    expect(wrapper.text()).toContain('Data Aggregator')
  })
})
