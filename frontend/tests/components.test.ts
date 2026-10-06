import { describe, it, expect, beforeEach } from 'vitest'
import { mount } from '@vue/test-utils'
import { setActivePinia, createPinia } from 'pinia'
import CustomNode from '../src/components/CustomNode.vue'
import NodeInspector from '../src/components/NodeInspector.vue'
import { useRegistryStore } from '../src/stores/registryStore'
import { useFlowStore } from '../src/stores/flowStore'
import type { ComponentDefinition } from '../src/types/flow'

const mockDefinition: ComponentDefinition = {
  name: 'HttpRequestComponent',
  displayName: 'HTTP Request',
  category: 'Actions',
  description: 'Sends HTTP requests',
  icon: 'globe',
  inputs: [
    { name: 'url', type: 'str', label: 'Endpoint URL', required: true, default: '' },
    { name: 'method', type: 'select', label: 'HTTP Method', options: ['GET', 'POST', 'PUT', 'DELETE'], default: 'GET' },
    { name: 'timeout', type: 'int', label: 'Timeout Seconds', default: 30 },
    { name: 'script', type: 'code', label: 'Transform Script', default: 'def run(): pass' },
  ],
  outputs: [
    { name: 'data', label: 'Response Body', type: 'dict', method: 'execute' },
    { name: 'status_code', label: 'Status Code', type: 'int', method: 'get_status' },
  ]
}

describe('Component Renderers Test Suite', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    const registry = useRegistryStore()
    registry.setComponents([mockDefinition])
  })

  it('CustomNode renders node display name, inputs and outputs', () => {
    const wrapper = mount(CustomNode, {
      props: {
        id: 'node-test-1',
        type: 'HttpRequestComponent',
        data: {
          inputs: { url: 'https://api.github.com' }
        }
      },
      global: {
        stubs: {
          Handle: {
            template: '<div class="vue-flow-handle" :data-id="id" />',
            props: ['id', 'type', 'position']
          }
        }
      }
    })

    expect(wrapper.text()).toContain('HTTP Request')
    expect(wrapper.text()).toContain('Endpoint URL')
    expect(wrapper.text()).toContain('Response Body')
    expect(wrapper.text()).toContain('Status Code')
  })

  it('NodeInspector dynamically generates controls for str, select, int, and code fields', async () => {
    const flowStore = useFlowStore()
    const nodeId = flowStore.addNode('HttpRequestComponent', { x: 100, y: 100 }, {
      url: 'https://api.github.com',
      method: 'GET',
      timeout: 30,
      script: 'def run(): pass'
    })

    const wrapper = mount(NodeInspector)

    expect(wrapper.text()).toContain('HTTP Request')
    expect(wrapper.text()).toContain('Endpoint URL')
    expect(wrapper.text()).toContain('HTTP Method')

    const urlInput = wrapper.find('input[type="text"]')
    expect(urlInput.exists()).toBe(true)
    expect((urlInput.element as HTMLInputElement).value).toBe('https://api.github.com')

    const select = wrapper.find('select')
    expect(select.exists()).toBe(true)
    expect((select.element as HTMLSelectElement).value).toBe('GET')

    const numberInput = wrapper.find('input[type="number"]')
    expect(numberInput.exists()).toBe(true)
    expect((numberInput.element as HTMLInputElement).value).toBe('30')

    const textarea = wrapper.find('textarea')
    expect(textarea.exists()).toBe(true)
    expect((textarea.element as HTMLTextAreaElement).value).toBe('def run(): pass')

    // Test updating value
    await urlInput.setValue('https://api.newdomain.com')
    expect(flowStore.nodes[0].data.inputs.url).toBe('https://api.newdomain.com')
  })
})
