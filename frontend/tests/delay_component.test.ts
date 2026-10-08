import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { setActivePinia, createPinia } from 'pinia'
import CustomNode from '../src/components/CustomNode.vue'
import ComponentPalette from '../src/components/ComponentPalette.vue'
import { useFlowStore } from '../src/stores/flowStore'
import { useRegistryStore } from '../src/stores/registryStore'
import type { ComponentDefinition } from '../src/types/flow'

const mockDelayDef: ComponentDefinition = {
  name: 'DelayComponent',
  displayName: 'Delay / Sleep',
  category: 'Logic',
  description: 'Suspends workflow execution for a specified duration before proceeding to downstream nodes.',
  icon: 'clock',
  inputs: [
    { name: 'input_data', type: 'dict', label: 'Incoming Data', default: {}, required: false, is_handle: true },
    { name: 'delay', type: 'float', label: 'Duration', default: 1.0, required: true, is_handle: true },
    { name: 'unit', type: 'select', label: 'Time Unit', options: ['seconds', 'milliseconds', 'minutes'], default: 'seconds', required: false, is_handle: true },
  ],
  outputs: [
    { name: 'data', label: 'Output Data', type: 'dict', method: 'get_data' },
    { name: 'waited_seconds', label: 'Waited Seconds', type: 'float', method: 'get_waited_seconds' },
  ],
}

describe('DelayComponent Frontend Suite', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.restoreAllMocks()
    const registryStore = useRegistryStore()
    registryStore.setComponents([mockDelayDef])
  })

  it('exposes DelayComponent schema with duration and unit options in registryStore', () => {
    const registryStore = useRegistryStore()
    const comp = registryStore.getComponent('DelayComponent')

    expect(comp).toBeDefined()
    expect(comp?.displayName).toBe('Delay / Sleep')
    expect(comp?.category).toBe('Logic')
    expect(comp?.icon).toBe('clock')

    const delayInput = comp?.inputs.find((i) => i.name === 'delay')
    expect(delayInput).toBeDefined()
    expect(delayInput?.type).toBe('float')
    expect(delayInput?.default).toBe(1.0)

    const unitInput = comp?.inputs.find((i) => i.name === 'unit')
    expect(unitInput).toBeDefined()
    expect(unitInput?.options).toEqual(['seconds', 'milliseconds', 'minutes'])
    expect(unitInput?.default).toBe('seconds')
  })

  it('updates DelayComponent node inputs and persists to flow payload', () => {
    const flowStore = useFlowStore()
    const nodeId = flowStore.addNode('DelayComponent', { x: 150, y: 200 }, {
      delay: 5,
      unit: 'seconds',
      input_data: {},
    })

    const node = flowStore.nodes.find((n) => n.id === nodeId)
    expect(node).toBeDefined()
    expect(node?.data.inputs.delay).toBe(5)
    expect(node?.data.inputs.unit).toBe('seconds')

    flowStore.updateNodeInput(nodeId, 'delay', 2.5)
    flowStore.updateNodeInput(nodeId, 'unit', 'minutes')

    expect(node?.data.inputs.delay).toBe(2.5)
    expect(node?.data.inputs.unit).toBe('minutes')

    const payload = flowStore.toFlowPayload()
    const serializedNode = payload.nodes.find((n) => n.id === nodeId)
    expect(serializedNode?.data.inputs.delay).toBe(2.5)
    expect(serializedNode?.data.inputs.unit).toBe('minutes')
  })

  it('renders CustomNode with Delay / Sleep title and ports', () => {
    const wrapper = mount(CustomNode, {
      props: {
        id: 'node-delay-1',
        type: 'DelayComponent',
        data: {
          inputs: { delay: 10, unit: 'seconds' },
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

    expect(wrapper.text()).toContain('Delay / Sleep')
    expect(wrapper.text()).toContain('Duration')
    expect(wrapper.text()).toContain('Time Unit')
    expect(wrapper.text()).toContain('Output Data')
    expect(wrapper.text()).toContain('Waited Seconds')
  })

  it('lists Delay / Sleep in ComponentPalette under Logic category', () => {
    const wrapper = mount(ComponentPalette)
    expect(wrapper.text()).toContain('Logic')
    expect(wrapper.text()).toContain('Delay / Sleep')
  })
})
