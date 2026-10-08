import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { setActivePinia, createPinia } from 'pinia'
import CustomNode from '../src/components/CustomNode.vue'
import ComponentPalette from '../src/components/ComponentPalette.vue'
import { useFlowStore } from '../src/stores/flowStore'
import { useRegistryStore } from '../src/stores/registryStore'
import type { ComponentDefinition } from '../src/types/flow'

const mockFilterDef: ComponentDefinition = {
  name: 'DataFilterComponent',
  displayName: 'Data Filter',
  category: 'Transform',
  description: 'Filters arrays of objects or data payloads declaratively based on field comparisons or expressions.',
  icon: 'filter',
  inputs: [
    { name: 'input_data', type: 'any', label: 'Incoming Collection', default: [], required: false, is_handle: true },
    { name: 'items_path', type: 'str', label: 'Items Key / Path', default: '', required: false, is_handle: true },
    { name: 'field', type: 'str', label: 'Field Name', default: 'status', required: false, is_handle: true },
    {
      name: 'operator',
      type: 'select',
      label: 'Comparison Operator',
      options: ['equals', 'not_equals', 'greater_than', 'less_than', 'greater_or_equal', 'less_or_equal', 'contains', 'not_contains', 'is_empty', 'is_not_empty', 'expression'],
      default: 'equals',
      required: false,
      is_handle: true,
    },
    { name: 'value', type: 'str', label: 'Comparison Value', default: 'active', required: false, is_handle: true },
    { name: 'custom_expression', type: 'str', label: 'Custom Expression', default: "item.get('status') == 'active'", required: false, is_handle: true },
  ],
  outputs: [
    { name: 'filtered_items', label: 'Filtered Items', type: 'list', method: 'get_filtered_items' },
    { name: 'discarded_items', label: 'Discarded Items', type: 'list', method: 'get_discarded_items' },
    { name: 'count', label: 'Count', type: 'int', method: 'get_count' },
    { name: 'total_count', label: 'Total Count', type: 'int', method: 'get_total_count' },
  ],
}

describe('DataFilterComponent Frontend Suite', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.restoreAllMocks()
    const registryStore = useRegistryStore()
    registryStore.setComponents([mockFilterDef])
  })

  it('exposes DataFilterComponent schema in registryStore', () => {
    const registryStore = useRegistryStore()
    const comp = registryStore.getComponent('DataFilterComponent')

    expect(comp).toBeDefined()
    expect(comp?.displayName).toBe('Data Filter')
    expect(comp?.category).toBe('Transform')

    const outNames = comp?.outputs.map((o) => o.name)
    expect(outNames).toContain('filtered_items')
    expect(outNames).toContain('discarded_items')
    expect(outNames).toContain('count')
    expect(outNames).toContain('total_count')

    const opInput = comp?.inputs.find((i) => i.name === 'operator')
    expect(opInput?.options).toContain('greater_than')
    expect(opInput?.options).toContain('contains')
  })

  it('updates DataFilterComponent inputs and serializes in flow payload', () => {
    const flowStore = useFlowStore()
    const nodeId = flowStore.addNode('DataFilterComponent', { x: 100, y: 150 }, {
      field: 'total',
      operator: 'greater_than',
      value: '100',
      items_path: 'records',
    })

    const node = flowStore.nodes.find((n) => n.id === nodeId)
    expect(node?.data.inputs.field).toBe('total')
    expect(node?.data.inputs.operator).toBe('greater_than')
    expect(node?.data.inputs.value).toBe('100')

    const payload = flowStore.toFlowPayload()
    const serialized = payload.nodes.find((n) => n.id === nodeId)
    expect(serialized?.data.inputs.field).toBe('total')
    expect(serialized?.data.inputs.items_path).toBe('records')
  })

  it('renders CustomNode with Data Filter ports and title', () => {
    const wrapper = mount(CustomNode, {
      props: {
        id: 'node-filter-1',
        type: 'DataFilterComponent',
        data: {
          inputs: { field: 'status', operator: 'equals', value: 'approved' },
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

    expect(wrapper.text()).toContain('Data Filter')
    expect(wrapper.text()).toContain('Filtered Items')
    expect(wrapper.text()).toContain('Discarded Items')
    expect(wrapper.text()).toContain('Count')
    expect(wrapper.text()).toContain('Total Count')
  })

  it('lists Data Filter in ComponentPalette under Transform category', () => {
    const wrapper = mount(ComponentPalette)
    expect(wrapper.text()).toContain('Transform')
    expect(wrapper.text()).toContain('Data Filter')
  })
})
