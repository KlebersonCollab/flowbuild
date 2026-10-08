import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { setActivePinia, createPinia } from 'pinia'
import TopNav from '../src/components/TopNav.vue'
import { useFlowStore } from '../src/stores/flowStore'

describe('Showcase Templates Suite (ADR 0021)', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.restoreAllMocks()
  })

  it('loads legacy templates correctly with valid trigger and nodes', () => {
    const flowStore = useFlowStore()

    flowStore.loadTemplate('http_enrich')
    expect(flowStore.nodes.length).toBeGreaterThanOrEqual(3)
    expect(flowStore.nodes[0].type).toBe('ManualTriggerComponent')

    flowStore.loadTemplate('python_pipeline')
    expect(flowStore.nodes.some((n) => n.type === 'PythonScriptComponent')).toBe(true)

    flowStore.loadTemplate('webhook_flow')
    expect(flowStore.nodes[0].type).toBe('WebhookTriggerComponent')

    flowStore.loadTemplate('if_condition_flow')
    expect(flowStore.nodes.some((n) => n.type === 'IfConditionComponent')).toBe(true)

    flowStore.loadTemplate('paginated_api_flow')
    expect(flowStore.nodes.some((n) => n.type === 'PaginatedHttpComponent')).toBe(true)
  })

  it('loads switch_router_flow template with SwitchNode and 4 routing branch edges', () => {
    const flowStore = useFlowStore()
    // @ts-expect-error templateType extension
    flowStore.loadTemplate('switch_router_flow')

    expect(flowStore.flowName).toContain('Roteamento')
    expect(flowStore.nodes.some((n) => n.type === 'SwitchNodeComponent')).toBe(true)
    expect(flowStore.nodes.some((n) => n.type === 'SlackWebhookComponent')).toBe(true)

    const switchNode = flowStore.nodes.find((n) => n.type === 'SwitchNodeComponent')
    expect(switchNode).toBeDefined()

    // Verify edges originate from case_1, case_2, case_3, and default_branch
    const caseHandles = flowStore.edges
      .filter((e) => e.source === switchNode?.id)
      .map((e) => e.sourceHandle)

    expect(caseHandles).toContain('case_1')
    expect(caseHandles).toContain('case_2')
    expect(caseHandles).toContain('case_3')
    expect(caseHandles).toContain('default_branch')
  })

  it('loads data_filter_alert_flow template with DataFilter and dual outputs', () => {
    const flowStore = useFlowStore()
    // @ts-expect-error templateType extension
    flowStore.loadTemplate('data_filter_alert_flow')

    expect(flowStore.flowName).toContain('Filtro')
    const filterNode = flowStore.nodes.find((n) => n.type === 'DataFilterComponent')
    expect(filterNode).toBeDefined()
    expect(filterNode?.data.inputs.operator).toBe('greater_than')

    const filterEdges = flowStore.edges.filter((e) => e.source === filterNode?.id)
    const outHandles = filterEdges.map((e) => e.sourceHandle)
    expect(outHandles).toContain('filtered_items')
    expect(flowStore.nodes.some((n) => n.type === 'SlackWebhookComponent')).toBe(true)
  })

  it('loads delay_polling_flow template with non-blocking DelayComponent', () => {
    const flowStore = useFlowStore()
    // @ts-expect-error templateType extension
    flowStore.loadTemplate('delay_polling_flow')

    expect(flowStore.flowName).toContain('Delay')
    const delayNode = flowStore.nodes.find((n) => n.type === 'DelayComponent')
    expect(delayNode).toBeDefined()
    expect(delayNode?.data.inputs.delay).toBeGreaterThan(0)
    expect(delayNode?.data.inputs.unit).toBe('seconds')
  })

  it('loads etl_pagination_filter_flow template connecting PaginatedHttp, DataFilter, and Slack', () => {
    const flowStore = useFlowStore()
    // @ts-expect-error templateType extension
    flowStore.loadTemplate('etl_pagination_filter_flow')

    expect(flowStore.flowName).toContain('ETL')
    expect(flowStore.nodes.some((n) => n.type === 'PaginatedHttpComponent')).toBe(true)
    expect(flowStore.nodes.some((n) => n.type === 'DataFilterComponent')).toBe(true)
    expect(flowStore.nodes.some((n) => n.type === 'SlackWebhookComponent')).toBe(true)
  })

  it('loads database_csv_export_flow template with DatabaseQuery, CsvParser, and EmailNotification', () => {
    const flowStore = useFlowStore()
    // @ts-expect-error templateType extension
    flowStore.loadTemplate('database_csv_export_flow')

    expect(flowStore.flowName).toContain('CSV')
    expect(flowStore.nodes.some((n) => n.type === 'CronTriggerComponent')).toBe(true)
    expect(flowStore.nodes.some((n) => n.type === 'DatabaseQueryComponent')).toBe(true)
    expect(flowStore.nodes.some((n) => n.type === 'CsvParserComponent')).toBe(true)
    expect(flowStore.nodes.some((n) => n.type === 'EmailNotificationComponent')).toBe(true)

    const csvNode = flowStore.nodes.find((n) => n.type === 'CsvParserComponent')
    expect(csvNode?.data.inputs.mode).toBe('generate')
    expect(flowStore.hasTriggerNode()).toBe(true)
  })

  it('loads batch_kv_discord_flow template with LoopIterator, KeyValueStore, and DiscordWebhook', () => {
    const flowStore = useFlowStore()
    // @ts-expect-error templateType extension
    flowStore.loadTemplate('batch_kv_discord_flow')

    expect(flowStore.flowName).toContain('Lote')
    expect(flowStore.nodes.some((n) => n.type === 'ManualTriggerComponent')).toBe(true)
    expect(flowStore.nodes.some((n) => n.type === 'LoopIteratorComponent')).toBe(true)
    expect(flowStore.nodes.some((n) => n.type === 'KeyValueStoreComponent')).toBe(true)
    expect(flowStore.nodes.some((n) => n.type === 'DiscordWebhookComponent')).toBe(true)

    const kvNode = flowStore.nodes.find((n) => n.type === 'KeyValueStoreComponent')
    expect(kvNode?.data.inputs.operation).toBe('increment')
    expect(kvNode?.data.inputs.namespace).toBe('billing')
    expect(flowStore.hasTriggerNode()).toBe(true)
  })

  it('loads resilient_try_catch_telegram_flow template with DataMapper, TryCatch, and TelegramWebhook', () => {
    const flowStore = useFlowStore()
    // @ts-expect-error templateType extension
    flowStore.loadTemplate('resilient_try_catch_telegram_flow')

    expect(flowStore.flowName).toContain('Resiliente')
    expect(flowStore.nodes.some((n) => n.type === 'WebhookTriggerComponent')).toBe(true)
    expect(flowStore.nodes.some((n) => n.type === 'DataMapperComponent')).toBe(true)
    expect(flowStore.nodes.some((n) => n.type === 'TryCatchComponent')).toBe(true)
    expect(flowStore.nodes.some((n) => n.type === 'TelegramWebhookComponent')).toBe(true)

    const tryCatchNode = flowStore.nodes.find((n) => n.type === 'TryCatchComponent')
    expect(tryCatchNode).toBeDefined()
    const edgesFromTry = flowStore.edges.filter((e) => e.source === tryCatchNode?.id)
    const handleNames = edgesFromTry.map((e) => e.sourceHandle)
    expect(handleNames).toContain('success_branch')
    expect(handleNames).toContain('error_branch')
    expect(flowStore.hasTriggerNode()).toBe(true)
  })

  it('renders TopNav with categorized template choices', async () => {
    const wrapper = mount(TopNav)
    // Open dropdown
    const modelBtn = wrapper.findAll('button').find((b) => b.text().includes('Modelos'))
    expect(modelBtn).toBeDefined()
    await modelBtn?.trigger('click')

    expect(wrapper.text()).toContain('Fluxos Básicos')
    expect(wrapper.text()).toContain('Lógica & Controle')
    expect(wrapper.text()).toContain('Dados & Alertas')
    expect(wrapper.text()).toContain('Banco de Dados, Lotes & Mensageria')
    expect(wrapper.text()).toContain('Roteamento Inteligente & Multi-Branch')
    expect(wrapper.text()).toContain('Filtragem de Dados & Alerta Slack')
    expect(wrapper.text()).toContain('Automação com Delay & Polling')
    expect(wrapper.text()).toContain('ETL Completo: Paginação → Filtro → Slack')
    expect(wrapper.text()).toContain('Exportação SQL para CSV & Email')
    expect(wrapper.text()).toContain('Processamento em Lote com KV & Discord')
    expect(wrapper.text()).toContain('Pipeline Resiliente: Try/Catch & Telegram')
  })
})
