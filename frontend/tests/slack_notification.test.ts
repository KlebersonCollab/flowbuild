import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { setActivePinia, createPinia } from 'pinia'
import CustomNode from '../src/components/CustomNode.vue'
import ComponentPalette from '../src/components/ComponentPalette.vue'
import { useFlowStore } from '../src/stores/flowStore'
import { useRegistryStore } from '../src/stores/registryStore'
import type { ComponentDefinition } from '../src/types/flow'

const mockSlackDef: ComponentDefinition = {
  name: 'SlackWebhookComponent',
  displayName: 'Slack Notification',
  category: 'Actions',
  description: 'Sends formatted alert messages and notifications to Slack channels via Incoming Webhooks.',
  icon: 'message-square',
  inputs: [
    { name: 'webhook_url', type: 'str', label: 'Webhook URL', placeholder: 'https://hooks.slack.com/services/...', required: true, is_handle: true },
    { name: 'text', type: 'str', label: 'Message Text', placeholder: 'Alert text', required: true, is_handle: true },
    { name: 'channel', type: 'str', label: 'Channel Override', default: '', required: false, is_handle: true },
    { name: 'username', type: 'str', label: 'Bot Username', default: 'FlowBuild Bot', required: false, is_handle: true },
    { name: 'icon_emoji', type: 'str', label: 'Icon Emoji', default: ':robot_face:', required: false, is_handle: true },
    { name: 'blocks', type: 'dict', label: 'Block Kit Blocks', default: null, required: false, is_handle: true },
    { name: 'attachments', type: 'dict', label: 'Attachments', default: null, required: false, is_handle: true },
    { name: 'timeout', type: 'int', label: 'Timeout', default: 15, required: false, is_handle: false },
  ],
  outputs: [
    { name: 'success', label: 'Success', type: 'bool', method: 'get_success' },
    { name: 'status_code', label: 'Status Code', type: 'int', method: 'get_status_code' },
    { name: 'response', label: 'Response', type: 'str', method: 'get_response' },
  ],
}

describe('SlackWebhookComponent Frontend Suite', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.restoreAllMocks()
    const registryStore = useRegistryStore()
    registryStore.setComponents([mockSlackDef])
  })

  it('exposes SlackWebhookComponent schema in registryStore', () => {
    const registryStore = useRegistryStore()
    const comp = registryStore.getComponent('SlackWebhookComponent')

    expect(comp).toBeDefined()
    expect(comp?.displayName).toBe('Slack Notification')
    expect(comp?.category).toBe('Actions')

    const outNames = comp?.outputs.map((o) => o.name)
    expect(outNames).toContain('success')
    expect(outNames).toContain('status_code')
    expect(outNames).toContain('response')

    const inpNames = comp?.inputs.map((i) => i.name)
    expect(inpNames).toContain('webhook_url')
    expect(inpNames).toContain('text')
    expect(inpNames).toContain('channel')
    expect(inpNames).toContain('username')
  })

  it('updates SlackWebhookComponent inputs and serializes in flow payload', () => {
    const flowStore = useFlowStore()
    const nodeId = flowStore.addNode('SlackWebhookComponent', { x: 200, y: 300 }, {
      webhook_url: 'https://hooks.slack.com/services/T00/B00/X00',
      text: 'Build succeeded for {{COMMIT}}',
      channel: '#alerts',
    })

    const node = flowStore.nodes.find((n) => n.id === nodeId)
    expect(node?.data.inputs.webhook_url).toBe('https://hooks.slack.com/services/T00/B00/X00')
    expect(node?.data.inputs.text).toBe('Build succeeded for {{COMMIT}}')
    expect(node?.data.inputs.channel).toBe('#alerts')

    const payload = flowStore.toFlowPayload()
    const serialized = payload.nodes.find((n) => n.id === nodeId)
    expect(serialized?.data.inputs.text).toBe('Build succeeded for {{COMMIT}}')
    expect(serialized?.data.inputs.channel).toBe('#alerts')
  })

  it('renders CustomNode with Slack Notification title and ports', () => {
    const wrapper = mount(CustomNode, {
      props: {
        id: 'node-slack-1',
        type: 'SlackWebhookComponent',
        data: {
          inputs: {
            webhook_url: 'https://hooks.slack.com/...',
            text: 'System alert: database failover',
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

    expect(wrapper.text()).toContain('Slack Notification')
    expect(wrapper.text()).toContain('Success')
    expect(wrapper.text()).toContain('Status Code')
    expect(wrapper.text()).toContain('Response')
  })

  it('lists Slack Notification in ComponentPalette under Actions category', () => {
    const wrapper = mount(ComponentPalette)
    expect(wrapper.text()).toContain('Actions')
    expect(wrapper.text()).toContain('Slack Notification')
  })
})
