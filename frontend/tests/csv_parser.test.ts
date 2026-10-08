import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { setActivePinia, createPinia } from 'pinia'
import CustomNode from '../src/components/CustomNode.vue'
import ComponentPalette from '../src/components/ComponentPalette.vue'
import { useFlowStore } from '../src/stores/flowStore'
import { useRegistryStore } from '../src/stores/registryStore'
import type { ComponentDefinition } from '../src/types/flow'

const mockCsvParserDef: ComponentDefinition = {
  name: 'CsvParserComponent',
  displayName: 'CSV Parser',
  category: 'Transform',
  description: 'Parses CSV text into JSON collections, or converts JSON collections into formatted CSV strings.',
  icon: 'file-spreadsheet',
  inputs: [
    { name: 'mode', type: 'select', label: 'Operation Mode', default: 'parse', options: ['parse', 'generate'], required: true, is_handle: false },
    { name: 'csv_data', type: 'str', label: 'CSV Data', default: '', required: false, is_handle: true },
    { name: 'json_data', type: 'dict', label: 'JSON Data', default: [], required: false, is_handle: true },
    { name: 'delimiter', type: 'str', label: 'Delimiter', default: ',', required: false, is_handle: false },
    { name: 'has_headers', type: 'bool', label: 'Has Header Row', default: true, required: false, is_handle: false },
    { name: 'skip_empty_lines', type: 'bool', label: 'Skip Empty Lines', default: true, required: false, is_handle: false },
    { name: 'custom_headers', type: 'str', label: 'Custom Headers (Generate Mode)', default: '', required: false, is_handle: false },
  ],
  outputs: [
    { name: 'data', label: 'Output Data', type: 'any', method: 'get_data' },
    { name: 'row_count', label: 'Row Count', type: 'int', method: 'get_row_count' },
    { name: 'headers', label: 'Headers', type: 'list', method: 'get_headers' },
  ],
}

describe('CsvParserComponent Frontend Suite', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.restoreAllMocks()
    const registryStore = useRegistryStore()
    registryStore.setComponents([mockCsvParserDef])
  })

  it('exposes CsvParserComponent schema in registryStore', () => {
    const registryStore = useRegistryStore()
    const comp = registryStore.getComponent('CsvParserComponent')

    expect(comp).toBeDefined()
    expect(comp?.displayName).toBe('CSV Parser')
    expect(comp?.category).toBe('Transform')

    const outNames = comp?.outputs.map((o) => o.name)
    expect(outNames).toContain('data')
    expect(outNames).toContain('row_count')
    expect(outNames).toContain('headers')

    const inpNames = comp?.inputs.map((i) => i.name)
    expect(inpNames).toContain('mode')
    expect(inpNames).toContain('csv_data')
    expect(inpNames).toContain('json_data')
    expect(inpNames).toContain('delimiter')
    expect(inpNames).toContain('has_headers')
    expect(inpNames).toContain('skip_empty_lines')
    expect(inpNames).toContain('custom_headers')
  })

  it('updates CsvParserComponent inputs and serializes in flow payload', () => {
    const flowStore = useFlowStore()
    const nodeId = flowStore.addNode('CsvParserComponent', { x: 300, y: 200 }, {
      mode: 'parse',
      csv_data: 'name,email\nAna,ana@test.com',
      delimiter: ',',
      has_headers: true,
    })

    const node = flowStore.nodes.find((n) => n.id === nodeId)
    expect(node?.data.inputs.mode).toBe('parse')
    expect(node?.data.inputs.delimiter).toBe(',')
    expect(node?.data.inputs.has_headers).toBe(true)

    const payload = flowStore.toFlowPayload()
    const serialized = payload.nodes.find((n) => n.id === nodeId)
    expect(serialized?.data.inputs.mode).toBe('parse')
    expect(serialized?.data.inputs.csv_data).toBe('name,email\nAna,ana@test.com')
  })

  it('renders CustomNode with CSV Parser title and ports', () => {
    const wrapper = mount(CustomNode, {
      props: {
        id: 'node-csv-1',
        type: 'CsvParserComponent',
        data: {
          inputs: {
            mode: 'parse',
            delimiter: ';',
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

    expect(wrapper.text()).toContain('CSV Parser')
    expect(wrapper.text()).toContain('Output Data')
    expect(wrapper.text()).toContain('Row Count')
    expect(wrapper.text()).toContain('Headers')
  })

  it('lists CSV Parser in ComponentPalette under Transform category', () => {
    const wrapper = mount(ComponentPalette)
    expect(wrapper.text()).toContain('Transform')
    expect(wrapper.text()).toContain('CSV Parser')
  })
})
