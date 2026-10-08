import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { setActivePinia, createPinia } from 'pinia'
import CustomNode from '../src/components/CustomNode.vue'
import ComponentPalette from '../src/components/ComponentPalette.vue'
import { useFlowStore } from '../src/stores/flowStore'
import { useRegistryStore } from '../src/stores/registryStore'
import type { ComponentDefinition } from '../src/types/flow'

const mockDatabaseQueryDef: ComponentDefinition = {
  name: 'DatabaseQueryComponent',
  displayName: 'Database Query',
  category: 'Storage',
  description: 'Executes parameterized SQL queries against SQLite, PostgreSQL, or external databases using SQLAlchemy.',
  icon: 'database',
  inputs: [
    { name: 'connection_string', type: 'str', label: 'Database Connection URL', default: '', required: false, is_handle: true },
    { name: 'query', type: 'code', label: 'SQL Query', default: 'SELECT 1 as result', required: true, is_handle: true },
    { name: 'params', type: 'dict', label: 'Query Parameters', default: {}, required: false, is_handle: true },
    { name: 'fetch_mode', type: 'select', label: 'Fetch Mode', default: 'all', options: ['all', 'one', 'none'], required: false, is_handle: false },
    { name: 'auto_commit', type: 'bool', label: 'Auto Commit', default: true, required: false, is_handle: false },
  ],
  outputs: [
    { name: 'data', label: 'Output Data', type: 'any', method: 'get_data' },
    { name: 'row_count', label: 'Row Count', type: 'int', method: 'get_row_count' },
    { name: 'columns', label: 'Columns', type: 'list', method: 'get_columns' },
  ],
}

describe('DatabaseQueryComponent Frontend Suite', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.restoreAllMocks()
    const registryStore = useRegistryStore()
    registryStore.setComponents([mockDatabaseQueryDef])
  })

  it('exposes DatabaseQueryComponent schema in registryStore', () => {
    const registryStore = useRegistryStore()
    const comp = registryStore.getComponent('DatabaseQueryComponent')

    expect(comp).toBeDefined()
    expect(comp?.displayName).toBe('Database Query')
    expect(comp?.category).toBe('Storage')

    const outNames = comp?.outputs.map((o) => o.name)
    expect(outNames).toContain('data')
    expect(outNames).toContain('row_count')
    expect(outNames).toContain('columns')

    const inpNames = comp?.inputs.map((i) => i.name)
    expect(inpNames).toContain('connection_string')
    expect(inpNames).toContain('query')
    expect(inpNames).toContain('params')
    expect(inpNames).toContain('fetch_mode')
    expect(inpNames).toContain('auto_commit')
  })

  it('updates DatabaseQueryComponent inputs and serializes in flow payload', () => {
    const flowStore = useFlowStore()
    const nodeId = flowStore.addNode('DatabaseQueryComponent', { x: 260, y: 150 }, {
      connection_string: 'sqlite:///test.db',
      query: 'SELECT * FROM users WHERE status = :status',
      params: { status: 'active' },
      fetch_mode: 'all',
      auto_commit: true,
    })

    const node = flowStore.nodes.find((n) => n.id === nodeId)
    expect(node?.data.inputs.query).toBe('SELECT * FROM users WHERE status = :status')
    expect(node?.data.inputs.fetch_mode).toBe('all')

    const payload = flowStore.toFlowPayload()
    const serialized = payload.nodes.find((n) => n.id === nodeId)
    expect(serialized?.data.inputs.query).toBe('SELECT * FROM users WHERE status = :status')
    expect(serialized?.data.inputs.params).toEqual({ status: 'active' })
  })

  it('renders CustomNode with Database Query title and ports', () => {
    const wrapper = mount(CustomNode, {
      props: {
        id: 'node-db-1',
        type: 'DatabaseQueryComponent',
        data: {
          inputs: {
            query: 'SELECT 1 as result',
            fetch_mode: 'one',
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

    expect(wrapper.text()).toContain('Database Query')
    expect(wrapper.text()).toContain('Output Data')
    expect(wrapper.text()).toContain('Row Count')
    expect(wrapper.text()).toContain('Columns')
  })

  it('lists Database Query in ComponentPalette under Storage category', () => {
    const wrapper = mount(ComponentPalette)
    expect(wrapper.text()).toContain('Storage')
    expect(wrapper.text()).toContain('Database Query')
  })
})
