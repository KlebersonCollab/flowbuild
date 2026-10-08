import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { setActivePinia, createPinia } from 'pinia'
import CustomNode from '../src/components/CustomNode.vue'
import ComponentPalette from '../src/components/ComponentPalette.vue'
import { useFlowStore } from '../src/stores/flowStore'
import { useRegistryStore } from '../src/stores/registryStore'
import type { ComponentDefinition } from '../src/types/flow'

const mockEmailDef: ComponentDefinition = {
  name: 'EmailNotificationComponent',
  displayName: 'Email Notification',
  category: 'Actions',
  description: 'Sends transactional emails and alerts via standard SMTP with HTML and plain text support.',
  icon: 'mail',
  inputs: [
    { name: 'smtp_host', type: 'str', label: 'SMTP Host', placeholder: 'smtp.gmail.com', required: true, is_handle: true },
    { name: 'smtp_port', type: 'int', label: 'SMTP Port', default: 587, required: false, is_handle: false },
    { name: 'smtp_user', type: 'str', label: 'SMTP Username', default: '', required: false, is_handle: true },
    { name: 'smtp_password', type: 'str', label: 'SMTP Password', default: '', required: false, is_handle: true },
    { name: 'use_tls', type: 'bool', label: 'Use STARTTLS', default: true, required: false, is_handle: false },
    { name: 'use_ssl', type: 'bool', label: 'Use SSL/TLS', default: false, required: false, is_handle: false },
    { name: 'from_email', type: 'str', label: 'From Email', placeholder: 'alerts@example.com', required: true, is_handle: true },
    { name: 'to_email', type: 'str', label: 'To Email(s)', placeholder: 'dev@example.com', required: true, is_handle: true },
    { name: 'subject', type: 'str', label: 'Subject', placeholder: 'Alert Subject', required: true, is_handle: true },
    { name: 'body_html', type: 'str', label: 'HTML Body', default: '', required: false, is_handle: true },
    { name: 'body_text', type: 'str', label: 'Plain Text Body', default: '', required: false, is_handle: true },
    { name: 'timeout', type: 'int', label: 'Timeout', default: 20, required: false, is_handle: false },
  ],
  outputs: [
    { name: 'success', label: 'Success', type: 'bool', method: 'get_success' },
    { name: 'status_code', label: 'Status Code', type: 'int', method: 'get_status_code' },
    { name: 'response', label: 'Response', type: 'str', method: 'get_response' },
    { name: 'recipients_count', label: 'Recipients Count', type: 'int', method: 'get_recipients_count' },
  ],
}

describe('EmailNotificationComponent Frontend Suite', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.restoreAllMocks()
    const registryStore = useRegistryStore()
    registryStore.setComponents([mockEmailDef])
  })

  it('exposes EmailNotificationComponent schema in registryStore', () => {
    const registryStore = useRegistryStore()
    const comp = registryStore.getComponent('EmailNotificationComponent')

    expect(comp).toBeDefined()
    expect(comp?.displayName).toBe('Email Notification')
    expect(comp?.category).toBe('Actions')

    const outNames = comp?.outputs.map((o) => o.name)
    expect(outNames).toContain('success')
    expect(outNames).toContain('status_code')
    expect(outNames).toContain('response')
    expect(outNames).toContain('recipients_count')

    const inpNames = comp?.inputs.map((i) => i.name)
    expect(inpNames).toContain('smtp_host')
    expect(inpNames).toContain('from_email')
    expect(inpNames).toContain('to_email')
    expect(inpNames).toContain('subject')
  })

  it('updates EmailNotificationComponent inputs and serializes in flow payload', () => {
    const flowStore = useFlowStore()
    const nodeId = flowStore.addNode('EmailNotificationComponent', { x: 300, y: 200 }, {
      smtp_host: 'smtp.sendgrid.net',
      from_email: 'alerts@domain.com',
      to_email: 'dev@domain.com',
      subject: 'Weekly Report',
      body_html: '<h1>Report Ready</h1>',
    })

    const node = flowStore.nodes.find((n) => n.id === nodeId)
    expect(node?.data.inputs.smtp_host).toBe('smtp.sendgrid.net')
    expect(node?.data.inputs.from_email).toBe('alerts@domain.com')
    expect(node?.data.inputs.to_email).toBe('dev@domain.com')
    expect(node?.data.inputs.subject).toBe('Weekly Report')

    const payload = flowStore.toFlowPayload()
    const serialized = payload.nodes.find((n) => n.id === nodeId)
    expect(serialized?.data.inputs.smtp_host).toBe('smtp.sendgrid.net')
    expect(serialized?.data.inputs.to_email).toBe('dev@domain.com')
    expect(serialized?.data.inputs.body_html).toBe('<h1>Report Ready</h1>')
  })

  it('renders CustomNode with Email Notification title and ports', () => {
    const wrapper = mount(CustomNode, {
      props: {
        id: 'node-email-1',
        type: 'EmailNotificationComponent',
        data: {
          inputs: {
            smtp_host: 'smtp.gmail.com',
            from_email: 'bot@example.com',
            to_email: 'team@example.com',
            subject: 'Daily Digest',
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

    expect(wrapper.text()).toContain('Email Notification')
    expect(wrapper.text()).toContain('Success')
    expect(wrapper.text()).toContain('Status Code')
    expect(wrapper.text()).toContain('Response')
    expect(wrapper.text()).toContain('Recipients Count')
  })

  it('lists Email Notification in ComponentPalette under Actions category', () => {
    const wrapper = mount(ComponentPalette)
    expect(wrapper.text()).toContain('Actions')
    expect(wrapper.text()).toContain('Email Notification')
  })
})
