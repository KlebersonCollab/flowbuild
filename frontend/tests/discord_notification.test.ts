import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { setActivePinia, createPinia } from 'pinia'
import CustomNode from '../src/components/CustomNode.vue'
import ComponentPalette from '../src/components/ComponentPalette.vue'
import { useFlowStore } from '../src/stores/flowStore'
import { useRegistryStore } from '../src/stores/registryStore'
import type { ComponentDefinition } from '../src/types/flow'

const mockDiscordDef: ComponentDefinition = {
  name: 'DiscordWebhookComponent',
  displayName: 'Discord Notification',
  category: 'Actions',
  description: 'Sends formatted messages, embeds, and alerts to Discord channels via Webhooks.',
  icon: 'message-circle',
  inputs: [
    { name: 'webhook_url', type: 'str', label: 'Webhook URL', placeholder: 'https://discord.com/api/webhooks/...', required: true, is_handle: true },
    { name: 'content', type: 'str', label: 'Message Content', placeholder: 'Message text', default: '', required: false, is_handle: true },
    { name: 'username', type: 'str', label: 'Bot Username', default: 'FlowBuild Bot', required: false, is_handle: true },
    { name: 'avatar_url', type: 'str', label: 'Avatar Image URL', default: '', required: false, is_handle: true },
    { name: 'embed_title', type: 'str', label: 'Embed Card Title', default: '', required: false, is_handle: true },
    { name: 'embed_description', type: 'str', label: 'Embed Card Description', default: '', required: false, is_handle: true },
    { name: 'embed_color', type: 'str', label: 'Embed Accent Color', default: '5814783', required: false, is_handle: true },
    { name: 'embeds', type: 'dict', label: 'Custom Embeds', default: null, required: false, is_handle: true },
    { name: 'timeout', type: 'int', label: 'Timeout', default: 15, required: false, is_handle: false },
  ],
  outputs: [
    { name: 'success', label: 'Success', type: 'bool', method: 'get_success' },
    { name: 'status_code', label: 'Status Code', type: 'int', method: 'get_status_code' },
    { name: 'response', label: 'Response', type: 'str', method: 'get_response' },
  ],
}

describe('DiscordWebhookComponent Frontend Suite', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.restoreAllMocks()
    const registryStore = useRegistryStore()
    registryStore.setComponents([mockDiscordDef])
  })

  it('exposes DiscordWebhookComponent schema in registryStore', () => {
    const registryStore = useRegistryStore()
    const comp = registryStore.getComponent('DiscordWebhookComponent')

    expect(comp).toBeDefined()
    expect(comp?.displayName).toBe('Discord Notification')
    expect(comp?.category).toBe('Actions')

    const outNames = comp?.outputs.map((o) => o.name)
    expect(outNames).toContain('success')
    expect(outNames).toContain('status_code')
    expect(outNames).toContain('response')

    const inpNames = comp?.inputs.map((i) => i.name)
    expect(inpNames).toContain('webhook_url')
    expect(inpNames).toContain('content')
    expect(inpNames).toContain('embed_title')
    expect(inpNames).toContain('embed_color')
  })

  it('updates DiscordWebhookComponent inputs and serializes in flow payload', () => {
    const flowStore = useFlowStore()
    const nodeId = flowStore.addNode('DiscordWebhookComponent', { x: 250, y: 350 }, {
      webhook_url: 'https://discord.com/api/webhooks/123/abc',
      content: 'Server status: operational',
      embed_title: 'Health Check',
      embed_color: '#00FF00',
    })

    const node = flowStore.nodes.find((n) => n.id === nodeId)
    expect(node?.data.inputs.webhook_url).toBe('https://discord.com/api/webhooks/123/abc')
    expect(node?.data.inputs.content).toBe('Server status: operational')
    expect(node?.data.inputs.embed_title).toBe('Health Check')

    const payload = flowStore.toFlowPayload()
    const serialized = payload.nodes.find((n) => n.id === nodeId)
    expect(serialized?.data.inputs.content).toBe('Server status: operational')
    expect(serialized?.data.inputs.embed_color).toBe('#00FF00')
  })

  it('renders CustomNode with Discord Notification title and ports', () => {
    const wrapper = mount(CustomNode, {
      props: {
        id: 'node-discord-1',
        type: 'DiscordWebhookComponent',
        data: {
          inputs: {
            webhook_url: 'https://discord.com/api/webhooks/...',
            content: 'Deployment completed in PRD',
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

    expect(wrapper.text()).toContain('Discord Notification')
    expect(wrapper.text()).toContain('Success')
    expect(wrapper.text()).toContain('Status Code')
    expect(wrapper.text()).toContain('Response')
  })

  it('lists Discord Notification in ComponentPalette under Actions category', () => {
    const wrapper = mount(ComponentPalette)
    expect(wrapper.text()).toContain('Actions')
    expect(wrapper.text()).toContain('Discord Notification')
  })
})
