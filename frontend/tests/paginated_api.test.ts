import { describe, it, expect, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useFlowStore } from '../src/stores/flowStore'
import { useExecutionStore } from '../src/stores/executionStore'

describe('Paginated API Loop & Break Suite Tests', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('loads paginated_api_flow template with trigger, paginated http client, and transform node', () => {
    const flowStore = useFlowStore()
    flowStore.loadTemplate('paginated_api_flow')

    expect(flowStore.flowId).toBe('flow-paginated-api')
    expect(flowStore.nodes.length).toBe(3)
    expect(flowStore.edges.length).toBe(2)

    const triggerNode = flowStore.nodes.find((n) => n.type === 'ManualTriggerComponent')
    const pageHttpNode = flowStore.nodes.find((n) => n.type === 'PaginatedHttpComponent')
    const transformNode = flowStore.nodes.find((n) => n.type === 'JsonTransformComponent')

    expect(triggerNode).toBeDefined()
    expect(pageHttpNode).toBeDefined()
    expect(transformNode).toBeDefined()

    // Verify PaginatedHttp inputs configuration
    expect(pageHttpNode?.data.inputs.pagination_mode).toBe('page_number')
    expect(pageHttpNode?.data.inputs.page_param).toBe('page')
    expect(pageHttpNode?.data.inputs.break_condition).toBe('total_items >= 25')
    expect(pageHttpNode?.data.inputs.max_pages).toBe(5)

    // Verify DAG edge mapping: trigger -> params, all_items handle -> transform input_data handle
    const triggerEdge = flowStore.edges.find((e) => e.target === pageHttpNode?.id)
    expect(triggerEdge).toBeDefined()
    expect(triggerEdge?.targetHandle).toBe('params')

    const dataEdge = flowStore.edges.find((e) => e.target === transformNode?.id)
    expect(dataEdge).toBeDefined()
    expect(dataEdge?.source).toBe(pageHttpNode?.id)
    expect(dataEdge?.sourceHandle).toBe('all_items')
    expect(dataEdge?.targetHandle).toBe('input_data')

    // Preconditions must be valid (has trigger node)
    const validation = flowStore.validateExecutionPreconditions()
    expect(validation.valid).toBe(true)
  })

  it('executionStore captures and logs PaginatedHttpComponent results with aggregated telemetry', () => {
    const executionStore = useExecutionStore()

    executionStore.handleEvent({
      event: 'flow_started',
      flow_id: 'flow-paginated-api',
    })

    executionStore.handleEvent({
      event: 'node_started',
      node_id: 'page-http-1',
      type: 'PaginatedHttpComponent',
    })
    expect(executionStore.getNodeState('page-http-1').status).toBe('running')

    const mockOutput = {
      all_items: [{ id: 1, name: 'repo-1' }, { id: 2, name: 'repo-2' }, { id: 3, name: 'repo-3' }],
      total_items: 3,
      pages_fetched: 2,
      summary: {
        total_items: 3,
        pages_fetched: 2,
        stop_reason: 'break_condition_met',
        mode: 'page_number',
      },
    }

    executionStore.handleEvent({
      event: 'node_completed',
      node_id: 'page-http-1',
      type: 'PaginatedHttpComponent',
      output: mockOutput,
    })

    const nodeState = executionStore.getNodeState('page-http-1')
    expect(nodeState.status).toBe('completed')
    expect(nodeState.output.total_items).toBe(3)
    expect(nodeState.output.pages_fetched).toBe(2)
    expect(nodeState.output.all_items.length).toBe(3)

    executionStore.handleEvent({
      event: 'flow_completed',
      flow_id: 'flow-paginated-api',
      summary: {
        status: 'completed',
        successful_nodes: ['trigger-1', 'page-http-1', 'summary-1'],
      },
    })

    expect(executionStore.isRunning).toBe(false)
    expect(executionStore.flowSummary?.status).toBe('completed')
  })
})
