import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import FlowsModal from '../src/components/FlowsModal.vue'
import { useFlowStore } from '../src/stores/flowStore'

describe('FlowsModal Responsive Viewport, Maximize & Grid Suite', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.restoreAllMocks()
    localStorage.clear()
    const store = useFlowStore()
    vi.spyOn(store, 'fetchSavedFlows').mockImplementation(async () => {})
    store.savedFlows = [
      {
        id: 'f1',
        name: 'Fluxo 1',
        folder: 'Geral',
        environment: 'dev',
        version: 'v1.0.0',
        is_active: true,
        flow_data: { id: 'f1', name: 'Fluxo 1', nodes: [], edges: [] },
      },
      {
        id: 'f2',
        name: 'Fluxo 2',
        folder: 'Financeiro',
        environment: 'dev',
        version: 'v1.0.0',
        is_active: true,
        flow_data: { id: 'f2', name: 'Fluxo 2', nodes: [], edges: [] },
      },
    ]
  })

  it('renders with fluid width and supports maximize/minimize toggle', async () => {
    const wrapper = mount(FlowsModal, {
      props: {
        isOpen: true,
      },
    })
    await flushPromises()

    const modalCard = wrapper.find('.bg-\\[\\#0f1011\\]')
    expect(modalCard.exists()).toBe(true)
    expect(modalCard.classes()).toContain('w-[96vw]')

    // Find maximize button
    const maxBtn = wrapper.find('button[title*="Maximizar"]')
    expect(maxBtn.exists()).toBe(true)

    // Trigger maximize
    await maxBtn.trigger('click')

    // Now it should have fullscreen classes
    expect(modalCard.classes()).toContain('fixed')
    expect(modalCard.classes()).toContain('inset-0')
    expect(modalCard.classes()).toContain('rounded-none')

    // Minimize back
    const minBtn = wrapper.find('button[title*="Restaurar"]')
    expect(minBtn.exists()).toBe(true)
    await minBtn.trigger('click')

    expect(modalCard.classes()).toContain('w-[96vw]')
    expect(modalCard.classes()).not.toContain('rounded-none')
  })

  it('allows collapsing and expanding the worktree sidebar to free horizontal space', async () => {
    const wrapper = mount(FlowsModal, {
      props: {
        isOpen: true,
      },
    })
    await flushPromises()

    // Sidebar should be open initially
    expect(wrapper.find('aside').exists()).toBe(true)

    // Find sidebar collapse button
    const toggleSidebarBtn = wrapper.find('button[title*="painel de pastas"]')
    expect(toggleSidebarBtn.exists()).toBe(true)

    // Click to collapse
    await toggleSidebarBtn.trigger('click')

    // Sidebar should be hidden
    expect(wrapper.find('aside').exists()).toBe(false)

    // Click to restore sidebar
    const reopenBtn = wrapper.find('button[title*="painel de pastas"]')
    expect(reopenBtn.exists()).toBe(true)
    await reopenBtn.trigger('click')

    expect(wrapper.find('aside').exists()).toBe(true)
  })

  it('supports toggling between list and 2-column grid display modes', async () => {
    const wrapper = mount(FlowsModal, {
      props: {
        isOpen: true,
      },
    })
    await flushPromises()

    const flowsContainer = wrapper.find('.flows-container')
    expect(flowsContainer.exists()).toBe(true)
    expect(flowsContainer.classes()).toContain('space-y-3')

    // Find grid button
    const gridBtn = wrapper.find('button[title*="Exibir em grade"]')
    expect(gridBtn.exists()).toBe(true)
    await gridBtn.trigger('click')

    // Container should now have grid classes
    expect(flowsContainer.classes()).toContain('grid')
    expect(flowsContainer.classes()).toContain('xl:grid-cols-2')

    // Find list button
    const listBtn = wrapper.find('button[title*="Exibir em lista"]')
    expect(listBtn.exists()).toBe(true)
    await listBtn.trigger('click')

    expect(flowsContainer.classes()).toContain('space-y-3')
    expect(flowsContainer.classes()).not.toContain('grid')
  })
})
