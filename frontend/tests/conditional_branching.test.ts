import { describe, it, expect, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useFlowStore } from '../src/stores/flowStore'
import { useExecutionStore } from '../src/stores/executionStore'

describe('Conditional Branching Suite Tests', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('loads if_condition_flow template with trigger, condition and branching nodes', () => {
    const flowStore = useFlowStore()
    flowStore.loadTemplate('if_condition_flow')

    expect(flowStore.flowId).toBe('flow-if-condition')
    expect(flowStore.nodes.length).toBe(4)
    expect(flowStore.edges.length).toBe(3)

    const triggerNode = flowStore.nodes.find((n) => n.type === 'ManualTriggerComponent')
    const ifNode = flowStore.nodes.find((n) => n.type === 'IfConditionComponent')
    const transformNodes = flowStore.nodes.filter((n) => n.type === 'JsonTransformComponent')

    expect(triggerNode).toBeDefined()
    expect(ifNode).toBeDefined()
    expect(transformNodes.length).toBe(2)

    // Verify edges routing true and false branches
    const trueEdge = flowStore.edges.find((e) => e.sourceHandle === 'true_branch')
    const falseEdge = flowStore.edges.find((e) => e.sourceHandle === 'false_branch')

    expect(trueEdge).toBeDefined()
    expect(falseEdge).toBeDefined()
    expect(trueEdge?.source).toBe(ifNode?.id)
    expect(falseEdge?.source).toBe(ifNode?.id)

    // Preconditions must be valid (has trigger node)
    const validation = flowStore.validateExecutionPreconditions()
    expect(validation.valid).toBe(true)
  })

  it('executionStore handles node_skipped event gracefully as skipped status without failing execution', () => {
    const executionStore = useExecutionStore()

    // 1. Flow starts
    executionStore.handleEvent({
      event: 'flow_started',
      flow_id: 'flow-if-condition',
    })
    expect(executionStore.isRunning).toBe(true)

    // 2. Trigger completes
    executionStore.handleEvent({
      event: 'node_completed',
      node_id: 'trigger-1',
      type: 'ManualTriggerComponent',
      output: { score: 85, user: 'Alice' },
    })
    expect(executionStore.getNodeState('trigger-1').status).toBe('completed')

    // 3. IF condition completes (True branch active)
    executionStore.handleEvent({
      event: 'node_completed',
      node_id: 'if-1',
      type: 'IfConditionComponent',
      output: { result: true, branch: 'true', true_branch: { score: 85 }, false_branch: null },
    })
    expect(executionStore.getNodeState('if-1').status).toBe('completed')

    // 4. True branch executes and completes
    executionStore.handleEvent({
      event: 'node_completed',
      node_id: 'tf-true',
      type: 'JsonTransformComponent',
      output: { status: 'aprovado', score: 85 },
    })
    expect(executionStore.getNodeState('tf-true').status).toBe('completed')

    // 5. False branch is skipped
    executionStore.handleEvent({
      event: 'node_skipped',
      node_id: 'tf-false',
      type: 'JsonTransformComponent',
      reason: 'condition_not_met',
    } as any)

    const skippedState = executionStore.getNodeState('tf-false')
    expect(skippedState.status).toBe('skipped')
    expect(skippedState.output).toEqual({ reason: 'condition_not_met' })

    // 6. Flow completes successfully
    executionStore.handleEvent({
      event: 'flow_completed',
      flow_id: 'flow-if-condition',
      summary: {
        status: 'completed',
        successful_nodes: ['trigger-1', 'if-1', 'tf-true'],
        skipped_nodes: ['tf-false'],
        failed_nodes: [],
      },
    })

    expect(executionStore.isRunning).toBe(false)
    expect(executionStore.flowSummary?.status).toBe('completed')

    // Verify structured logs contain info message for skipped node
    const skipLog = executionStore.structuredLogs.find((l) => l.nodeId === 'tf-false')
    expect(skipLog).toBeDefined()
    expect(skipLog?.level).toBe('info')
    expect(skipLog?.message).toContain('ramificação condicional não selecionada')
  })
})
