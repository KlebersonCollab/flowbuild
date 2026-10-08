import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { setActivePinia, createPinia } from 'pinia'
import CustomNode from '../src/components/CustomNode.vue'
import ComponentPalette from '../src/components/ComponentPalette.vue'
import { useFlowStore } from '../src/stores/flowStore'
import { useRegistryStore } from '../src/stores/registryStore'
import type { ComponentDefinition } from '../src/types/flow'

const mockMapperDef: ComponentDefinition = {
  name: 'DataMapperComponent',
  displayName: 'Data Mapper',
  category: 'Transform',
  description: 'Transforms, renames, and restructures objects or collections using declarative field mappings.',
  icon: 'arrow-right-left',
  inputs: [
    { name: 'input_data', type: 'dict', label: 'Input Data', default: {}, required: true, is_handle: true },
    { name: 'mapping', type: 'dict', label: 'Field Mapping Schema', default: {}, required: true, is_handle: true },
    { name: 'items_path', type: 'str', label: 'Items Array Path', default: '', required: false, is_handle: true },
    { name: 'pass_unmapped', type: 'bool', label: 'Pass Unmapped Fields', default: false, required: false, is_handle: false },
    { name: 'mode', type: 'str', label: 'Processing Mode', default: 'auto', required: false, is_handle: false },
  ],
  outputs: [
    { name: 'output_data', label: 'Mapped Output', type: 'any', method: 'get_output_data' },
    { name: 'mapped_count', label: 'Mapped Count', type: 'int', method: 'get_mapped_count' },
  ],
}

describe('DataMapperComponent Frontend Suite', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.restoreAllMocks()
    const registryStore = useRegistryStore()
    registryStore.setComponents([mockMapperDef])
  })

  it('exposes DataMapperComponent schema in registryStore', () => {
    const registryStore = useRegistryStore()
    const comp = registryStore.getComponent('DataMapperComponent')

    expect(comp).toBeDefined()
    expect(comp?.displayName).toBe('Data Mapper')
    expect(comp?.category).toBe('Transform')

    const outNames = comp?.outputs.map((o) => o.name)
    expect(outNames).toContain('output_data')
    expect(outNames).toContain('mapped_count')

    const inpNames = comp?.inputs.map((i) => i.name)
    expect(inpNames).toContain('input_data')
    expect(inpNames).toContain('mapping')
    expect(inpNames).toContain('items_path')
  })

  it('updates DataMapperComponent inputs and serializes in flow payload', () => {
    const flowStore = useFlowStore()
    const nodeId = flowStore.addNode('DataMapperComponent', { x: 200, y: 150 }, {
      input_data: { user: { name: 'Bob' } },
      mapping: { userName: 'user.name' },
      pass_unmapped: true,
    })

    const node = flowStore.nodes.find((n) => n.id === nodeId)
    expect(node?.data.inputs.mapping).toEqual({ userName: 'user.name' })
    expect(node?.data.inputs.pass_unmapped).toBe(true)

    const payload = flowStore.toFlowPayload()
    const serialized = payload.nodes.find((n) => n.id === nodeId)
    expect(serialized?.data.inputs.mapping).toEqual({ userName: 'user.name' })
  })

  it('renders CustomNode with Data Mapper title and ports', () => {
    const wrapper = mount(CustomNode, {
      props: {
        id: 'node-mapper-1',
        type: 'DataMapperComponent',
        data: {
          inputs: {
            mapping: { id: 'user_id' },
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

    expect(wrapper.text()).toContain('Data Mapper')
    expect(wrapper.text()).toContain('Mapped Output')
    expect(wrapper.text()).toContain('Mapped Count')
  })

  it('lists Data Mapper in ComponentPalette under Transform category', () => {
    const wrapper = mount(ComponentPalette)
    expect(wrapper.text()).toContain('Transform')
    expect(wrapper.text()).toContain('Data Mapper')
  })
})
