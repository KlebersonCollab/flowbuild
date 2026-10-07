import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount, flushPromises } from '@vue/test-utils'
import { createPinia, setActivePinia } from 'pinia'
import FlowsModal from '../src/components/FlowsModal.vue'
import { useFlowStore } from '../src/stores/flowStore'

describe('FlowsModal Worktree Navigation and Selection', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.restoreAllMocks()
    localStorage.clear()
    const store = useFlowStore()
    vi.spyOn(store, 'fetchSavedFlows').mockImplementation(async () => {})
  })

  it('renders worktree sidebar with root and hierarchical folders', async () => {
    const store = useFlowStore()
    store.savedFlows = [
      {
        id: 'f1',
        name: 'Fluxo Geral 1',
        folder: 'Geral',
        environment: 'dev',
        version: 'v1.0.0',
        is_active: true,
        flow_data: { id: 'f1', name: 'Fluxo Geral 1', nodes: [], edges: [] },
      },
      {
        id: 'f2',
        name: 'Cobrança Boleto',
        folder: 'Financeiro/Cobrança',
        environment: 'dev',
        version: 'v1.0.0',
        is_active: true,
        flow_data: { id: 'f2', name: 'Cobrança Boleto', nodes: [], edges: [] },
      },
      {
        id: 'f3',
        name: 'Notas Fiscais',
        folder: 'Financeiro/Fiscal',
        environment: 'dev',
        version: 'v1.0.0',
        is_active: true,
        flow_data: { id: 'f3', name: 'Notas Fiscais', nodes: [], edges: [] },
      },
    ]

    const wrapper = mount(FlowsModal, {
      props: {
        isOpen: true,
      },
    })
    await flushPromises()

    // Sidebar should be present
    expect(wrapper.text()).toContain('Worktree de Pastas')
    expect(wrapper.text()).toContain('Todos os Fluxos')

    // Root folder Financeiro and Geral should be visible
    expect(wrapper.text()).toContain('Financeiro')
    expect(wrapper.text()).toContain('Geral')

    // Since autoExpandRoots is triggered, child folders should also be visible
    expect(wrapper.text()).toContain('Cobrança')
    expect(wrapper.text()).toContain('Fiscal')
  })

  it('filters right panel flows when selecting a specific folder in the worktree', async () => {
    const store = useFlowStore()
    store.savedFlows = [
      {
        id: 'f1',
        name: 'Fluxo Geral 1',
        folder: 'Geral',
        environment: 'dev',
        version: 'v1.0.0',
        is_active: true,
        flow_data: { id: 'f1', name: 'Fluxo Geral 1', nodes: [], edges: [] },
      },
      {
        id: 'f2',
        name: 'Cobrança Boleto',
        folder: 'Financeiro/Cobrança',
        environment: 'dev',
        version: 'v1.0.0',
        is_active: true,
        flow_data: { id: 'f2', name: 'Cobrança Boleto', nodes: [], edges: [] },
      },
      {
        id: 'f3',
        name: 'Notas Fiscais',
        folder: 'Financeiro/Fiscal',
        environment: 'dev',
        version: 'v1.0.0',
        is_active: true,
        flow_data: { id: 'f3', name: 'Notas Fiscais', nodes: [], edges: [] },
      },
    ]

    const wrapper = mount(FlowsModal, {
      props: {
        isOpen: true,
      },
    })
    await flushPromises()

    // Initially, all 3 flows are visible under "Todos os Fluxos"
    expect(wrapper.text()).toContain('Fluxo Geral 1')
    expect(wrapper.text()).toContain('Cobrança Boleto')
    expect(wrapper.text()).toContain('Notas Fiscais')

    // Click on "Cobrança" item
    const cobrancaItem = wrapper.findAll('.cursor-pointer').find(el => el.text().includes('Cobrança'))
    expect(cobrancaItem).toBeDefined()
    await cobrancaItem!.trigger('click')

    // Breadcrumb updates to Financeiro / Cobrança
    expect(wrapper.text()).toContain('Financeiro')
    expect(wrapper.text()).toContain('Cobrança')

    // Only Cobrança Boleto flow is shown
    expect(wrapper.text()).toContain('Cobrança Boleto')
    expect(wrapper.text()).not.toContain('Fluxo Geral 1')
    expect(wrapper.text()).not.toContain('Notas Fiscais')
  })

  it('filters folders when typing in search input', async () => {
    const store = useFlowStore()
    store.savedFlows = [
      {
        id: 'f1',
        name: 'Fluxo RH',
        folder: 'Recursos Humanos',
        environment: 'dev',
        is_active: true,
        flow_data: { id: 'f1', name: 'Fluxo RH', nodes: [], edges: [] },
      },
      {
        id: 'f2',
        name: 'Fluxo Fiscal',
        folder: 'Financeiro/Fiscal',
        environment: 'dev',
        is_active: true,
        flow_data: { id: 'f2', name: 'Fluxo Fiscal', nodes: [], edges: [] },
      },
    ]

    const wrapper = mount(FlowsModal, {
      props: {
        isOpen: true,
      },
    })
    await flushPromises()

    const searchInput = wrapper.find('input[placeholder="Filtrar pastas..."]')
    expect(searchInput.exists()).toBe(true)

    await searchInput.setValue('Humanos')

    const sidebar = wrapper.find('aside')
    expect(sidebar.text()).toContain('Recursos Humanos')
    expect(sidebar.text()).not.toContain('Financeiro')
  })
})
