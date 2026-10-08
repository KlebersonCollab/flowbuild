import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { setActivePinia, createPinia } from 'pinia'
import CustomNode from '../src/components/CustomNode.vue'
import ComponentPalette from '../src/components/ComponentPalette.vue'
import { useFlowStore } from '../src/stores/flowStore'
import { useRegistryStore } from '../src/stores/registryStore'
import type { ComponentDefinition } from '../src/types/flow'

const mockSwitchDef: ComponentDefinition = {
  name: 'SwitchNodeComponent',
  displayName: 'Switch / Router',
  category: 'Logic',
  description: 'Routes incoming data to one of multiple branches (case_1, case_2, case_3, or default) based on value or expression evaluation.',
  icon: 'git-fork',
  inputs: [
    { name: 'input_data', type: 'dict', label: 'Incoming Data', default: {}, required: false, is_handle: true },
    { name: 'expression', type: 'str', label: 'Switch Expression', default: "data.get('status')", required: true, is_handle: true },
    { name: 'case_1_value', type: 'str', label: 'Case 1 Match Value', default: 'paid', required: false, is_handle: true },
    { name: 'case_2_value', type: 'str', label: 'Case 2 Match Value', default: 'pending', required: false, is_handle: true },
    { name: 'case_3_value', type: 'str', label: 'Case 3 Match Value', default: 'cancelled', required: false, is_handle: true },
  ],
  outputs: [
    { name: 'case_1', label: 'Case 1 Branch', type: 'dict', method: 'get_case_1' },
    { name: 'case_2', label: 'Case 2 Branch', type: 'dict', method: 'get_case_2' },
    { name: 'case_3', label: 'Case 3 Branch', type: 'dict', method: 'get_case_3' },
    { name: 'default_branch', label: 'Default Branch', type: 'dict', method: 'get_default_branch' },
    { name: 'matched_case', label: 'Matched Case', type: 'str', method: 'get_matched_case' },
    { name: 'evaluated_value', label: 'Evaluated Value', type: 'any', method: 'get_evaluated_value' },
  ],
}

describe('SwitchNodeComponent Frontend Suite', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.restoreAllMocks()
    const registryStore = useRegistryStore()
    registryStore.setComponents([mockSwitchDef])
  })

  it('exposes SwitchNodeComponent schema with 4 branch outputs in registryStore', () => {
    const registryStore = useRegistryStore()
    const comp = registryStore.getComponent('SwitchNodeComponent')

    expect(comp).toBeDefined()
    expect(comp?.displayName).toBe('Switch / Router')
    expect(comp?.category).toBe('Logic')

    const outNames = comp?.outputs.map((o) => o.name)
    expect(outNames).toContain('case_1')
    expect(outNames).toContain('case_2')
    expect(outNames).toContain('case_3')
    expect(outNames).toContain('default_branch')
  })

  it('updates SwitchNodeComponent inputs and persists in flow payload', () => {
    const flowStore = useFlowStore()
    const nodeId = flowStore.addNode('SwitchNodeComponent', { x: 100, y: 150 }, {
      expression: "data.get('event')",
      case_1_value: 'order.created',
      case_2_value: 'order.paid',
      case_3_value: 'order.cancelled',
    })

    const node = flowStore.nodes.find((n) => n.id === nodeId)
    expect(node?.data.inputs.expression).toBe("data.get('event')")
    expect(node?.data.inputs.case_1_value).toBe('order.created')

    const payload = flowStore.toFlowPayload()
    const serialized = payload.nodes.find((n) => n.id === nodeId)
    expect(serialized?.data.inputs.case_2_value).toBe('order.paid')
  })

  it('renders CustomNode with Switch / Router handles and title', () => {
    const wrapper = mount(CustomNode, {
      props: {
        id: 'node-switch-1',
        type: 'SwitchNodeComponent',
        data: {
          inputs: { expression: "data.get('status')" },
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

    expect(wrapper.text()).toContain('Switch / Router')
    expect(wrapper.text()).toContain('Case 1 Branch')
    expect(wrapper.text()).toContain('Case 2 Branch')
    expect(wrapper.text()).toContain('Case 3 Branch')
    expect(wrapper.text()).toContain('Default Branch')
  })

  it('lists Switch / Router in ComponentPalette under Logic category', () => {
    const wrapper = mount(ComponentPalette)
    expect(wrapper.text()).toContain('Logic')
    expect(wrapper.text()).toContain('Switch / Router')
  })
})
