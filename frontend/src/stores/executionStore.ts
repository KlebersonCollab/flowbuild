import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { ExecutionEvent, NodeExecutionState, FlowModel } from '../types/flow'

export const useExecutionStore = defineStore('execution', () => {
  const isRunning = ref<boolean>(false)
  const nodeStates = ref<Record<string, NodeExecutionState>>({})
  const flowSummary = ref<any>(null)
  const logs = ref<string[]>([])

  function resetExecution(): void {
    nodeStates.value = {}
    flowSummary.value = null
    logs.value = []
    isRunning.value = false
  }

  function getNodeState(nodeId: string): NodeExecutionState {
    if (!nodeStates.value[nodeId]) {
      nodeStates.value[nodeId] = { status: 'idle' }
    }
    return nodeStates.value[nodeId]
  }

  function handleEvent(event: ExecutionEvent): void {
    logs.value.push(JSON.stringify(event))

    switch (event.event) {
      case 'flow_started':
        isRunning.value = true
        break

      case 'node_started':
        if (event.node_id) {
          nodeStates.value[event.node_id] = { status: 'running' }
        }
        break

      case 'node_completed':
        if (event.node_id) {
          nodeStates.value[event.node_id] = {
            status: 'completed',
            output: event.output,
          }
        }
        break

      case 'node_failed':
        if (event.node_id) {
          nodeStates.value[event.node_id] = {
            status: 'failed',
            error: event.error,
          }
        }
        break

      case 'node_skipped':
        if (event.node_id) {
          nodeStates.value[event.node_id] = {
            status: 'failed',
            error: 'Dependency failed',
          }
        }
        break

      case 'flow_completed':
      case 'flow_failed':
        isRunning.value = false
        if (event.summary) {
          flowSummary.value = event.summary
        }
        break
    }
  }

  async function runFlowStream(flow: FlowModel, baseUrl: string = 'http://localhost:8000'): Promise<void> {
    resetExecution()
    isRunning.value = true

    try {
      const response = await fetch(`${baseUrl}/api/v1/flows/execute/stream`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(flow),
      })

      if (!response.ok) {
        throw new Error(`Failed to start flow execution: ${response.statusText}`)
      }

      const reader = response.body?.getReader()
      if (!reader) return

      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n\n')
        buffer = lines.pop() || ''

        for (const line of lines) {
          const trimmed = line.trim()
          if (trimmed.startsWith('data: ')) {
            const rawJson = trimmed.substring(6)
            try {
              const event: ExecutionEvent = JSON.parse(rawJson)
              handleEvent(event)
            } catch {
              // Ignore corrupted chunks
            }
          }
        }
      }
    } catch (err: any) {
      logs.value.push(`Execution error: ${err.message}`)
    } finally {
      isRunning.value = false
    }
  }

  return {
    isRunning,
    nodeStates,
    flowSummary,
    logs,
    resetExecution,
    getNodeState,
    handleEvent,
    runFlowStream,
  }
})
