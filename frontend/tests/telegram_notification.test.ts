import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { setActivePinia, createPinia } from 'pinia'
import CustomNode from '../src/components/CustomNode.vue'
import ComponentPalette from '../src/components/ComponentPalette.vue'
import { useFlowStore } from '../src/stores/flowStore'
import { useRegistryStore } from '../src/stores/registryStore'
import type { ComponentDefinition } from '../src/types/flow'

const mockTelegramDef: ComponentDefinition = {
  name: 'TelegramWebhookComponent',
  displayName: 'Telegram Notification',
  category: 'Actions',
  description: 'Sends messages, alerts, or formatted notifications to Telegram chats or channels via Telegram Bot API.',
  icon: 'send',
  inputs: [
    { name: 'bot_token', type: 'str', label: 'Bot Token', placeholder: '123456789:ABC...', required: true, is_handle: true },
    { name: 'chat_id', type: 'str', label: 'Chat ID', placeholder: '@channel_username or -1001234567890', required: true, is_handle: true },
    { name: 'message', type: 'str', label: 'Message Text', placeholder: 'Message text', default: '', required: true, is_handle: true },
    { name: 'parse_mode', type: 'str', label: 'Parse Mode', default: 'HTML', required: false, is_handle: true },
    { name: 'disable_web_page_preview', type: 'bool', label: 'Disable Link Previews', default: false, required: false, is_handle: false },
    { name: 'disable_notification', type: 'bool', label: 'Silent Notification', default: false, required: false, is_handle: false },
    { name: 'timeout', type: 'int', label: 'Timeout', default: 15, required: false, is_handle: false },
  ],
  outputs: [
    { name: 'success', label: 'Success', type: 'bool', method: 'get_success' },
    { name: 'status_code', label: 'Status Code', type: 'int', method: 'get_status_code' },
    { name: 'response', label: 'Response', type: 'str', method: 'get_response' },
    { name: 'message_id', label: 'Message ID', type: 'int', method: 'get_message_id' },
  ],
}

describe('TelegramWebhookComponent Frontend Suite', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.restoreAllMocks()
    const registryStore = useRegistryStore()
    registryStore.setComponents([mockTelegramDef])
  })

  it('exposes TelegramWebhookComponent schema in registryStore', () => {
    const registryStore = useRegistryStore()
    const comp = registryStore.getComponent('TelegramWebhookComponent')

    expect(comp).toBeDefined()
    expect(comp?.displayName).toBe('Telegram Notification')
    expect(comp?.category).toBe('Actions')

    const outNames = comp?.outputs.map((o) => o.name)
    expect(outNames).toContain('success')
    expect(outNames).toContain('status_code')
    expect(outNames).toContain('response')
    expect(outNames).toContain('message_id')

    const inpNames = comp?.inputs.map((i) => i.name)
    expect(inpNames).toContain('bot_token')
    expect(inpNames).toContain('chat_id')
    expect(inpNames).toContain('message')
    expect(inpNames).toContain('parse_mode')
  })

  it('updates TelegramWebhookComponent inputs and serializes in flow payload', () => {
    const flowStore = useFlowStore()
    const nodeId = flowStore.addNode('TelegramWebhookComponent', { x: 300, y: 200 }, {
      bot_token: '123456:ABC-DEF',
      chat_id: '-100998877',
      message: 'System alert: database healthy',
      parse_mode: 'HTML',
    })

    const node = flowStore.nodes.find((n) => n.id === nodeId)
    expect(node?.data.inputs.bot_token).toBe('123456:ABC-DEF')
    expect(node?.data.inputs.chat_id).toBe('-100998877')
    expect(node?.data.inputs.message).toBe('System alert: database healthy')

    const payload = flowStore.toFlowPayload()
    const serialized = payload.nodes.find((n) => n.id === nodeId)
    expect(serialized?.data.inputs.bot_token).toBe('123456:ABC-DEF')
    expect(serialized?.data.inputs.chat_id).toBe('-100998877')
    expect(serialized?.data.inputs.message).toBe('System alert: database healthy')
  })

  it('renders CustomNode with Telegram Notification title and ports', () => {
    const wrapper = mount(CustomNode, {
      props: {
        id: 'node-telegram-1',
        type: 'TelegramWebhookComponent',
        data: {
          inputs: {
            bot_token: '123456:ABC',
            chat_id: '-100123',
            message: 'Hello Telegram!',
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

    expect(wrapper.text()).toContain('Telegram Notification')
    expect(wrapper.text()).toContain('Success')
    expect(wrapper.text()).toContain('Status Code')
    expect(wrapper.text()).toContain('Response')
    expect(wrapper.text()).toContain('Message ID')
  })

  it('lists Telegram Notification in ComponentPalette under Actions category', () => {
    const wrapper = mount(ComponentPalette)
    expect(wrapper.text()).toContain('Actions')
    expect(wrapper.text()).toContain('Telegram Notification')
  })
})
