import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { ExecutionEvent, NodeExecutionState, FlowModel, FlowLogEntry } from '../types/flow'

export const useExecutionStore = defineStore('execution', () => {
  const isRunning = ref<boolean>(false)
  const nodeStates = ref<Record<string, NodeExecutionState>>({})
  const flowSummary = ref<any>(null)
  const logs = ref<string[]>([])
  const structuredLogs = ref<FlowLogEntry[]>([])
  const isDrawerOpen = ref<boolean>(false)
  const activeDrawerTab = ref<'logs' | 'outputs' | 'payload' | 'history'>('logs')

  const nodeStartTimes = new Map<string, number>()
  let flowStartTime = 0

  function resetExecution(): void {
    nodeStates.value = {}
    flowSummary.value = null
    logs.value = []
    structuredLogs.value = []
    isRunning.value = false
    nodeStartTimes.clear()
    flowStartTime = 0
  }

  function getNodeState(nodeId: string): NodeExecutionState {
    if (!nodeStates.value[nodeId]) {
      nodeStates.value[nodeId] = { status: 'idle' }
    }
    return nodeStates.value[nodeId]
  }

  function handleEvent(event: ExecutionEvent): void {
    logs.value.push(JSON.stringify(event))
    const now = new Date()
    const timeStr = now.toTimeString().split(' ')[0] + '.' + String(now.getMilliseconds()).padStart(3, '0')

    switch (event.event) {
      case 'flow_started':
        isRunning.value = true
        isDrawerOpen.value = true
        flowStartTime = Date.now()
        structuredLogs.value.push({
          id: `log-${Date.now()}-${Math.random().toString(36).substring(2, 6)}`,
          timestamp: timeStr,
          level: 'info',
          message: `Iniciando execução do fluxo [ID: ${event.flow_id || 'ativo'}]...`
        })
        break

      case 'node_started':
        if (event.node_id) {
          nodeStartTimes.set(event.node_id, Date.now())
          nodeStates.value[event.node_id] = { status: 'running' }
          structuredLogs.value.push({
            id: `log-${Date.now()}-${Math.random().toString(36).substring(2, 6)}`,
            timestamp: timeStr,
            nodeId: event.node_id,
            nodeName: event.type,
            level: 'info',
            message: `Executando nó: ${event.type || event.node_id}`
          })
        }
        break

      case 'node_completed':
        if (event.node_id) {
          const startTime = nodeStartTimes.get(event.node_id) || Date.now()
          const duration = Date.now() - startTime
          nodeStates.value[event.node_id] = {
            status: 'completed',
            output: event.output,
            durationMs: duration,
          }
          structuredLogs.value.push({
            id: `log-${Date.now()}-${Math.random().toString(36).substring(2, 6)}`,
            timestamp: timeStr,
            nodeId: event.node_id,
            nodeName: event.type,
            level: 'success',
            message: `Nó ${event.type || event.node_id} concluído com sucesso (${duration}ms)`,
            durationMs: duration,
            output: event.output,
          })
        }
        break

      case 'node_failed':
        if (event.node_id) {
          const startTime = nodeStartTimes.get(event.node_id) || Date.now()
          const duration = Date.now() - startTime
          nodeStates.value[event.node_id] = {
            status: 'failed',
            error: event.error,
            durationMs: duration,
          }
          structuredLogs.value.push({
            id: `log-${Date.now()}-${Math.random().toString(36).substring(2, 6)}`,
            timestamp: timeStr,
            nodeId: event.node_id,
            nodeName: event.type,
            level: 'error',
            message: `Erro no nó ${event.type || event.node_id}: ${event.error}`,
            durationMs: duration,
          })
        }
        break

      case 'node_skipped':
        if (event.node_id) {
          nodeStates.value[event.node_id] = {
            status: 'failed',
            error: 'Dependency failed',
          }
          structuredLogs.value.push({
            id: `log-${Date.now()}-${Math.random().toString(36).substring(2, 6)}`,
            timestamp: timeStr,
            nodeId: event.node_id,
            nodeName: event.type,
            level: 'warn',
            message: `Nó ${event.type || event.node_id} ignorado devido a falha prévia.`
          })
        }
        break

      case 'flow_completed':
        isRunning.value = false
        if (event.summary) {
          flowSummary.value = event.summary
        }
        const totalDuration = flowStartTime ? Date.now() - flowStartTime : 0
        structuredLogs.value.push({
          id: `log-${Date.now()}-${Math.random().toString(36).substring(2, 6)}`,
          timestamp: timeStr,
          level: 'success',
          message: `Fluxo concluído com êxito! Duração total: ${totalDuration}ms. Nós executados: ${event.summary?.successful_nodes?.length || 0}.`
        })
        break

      case 'flow_failed':
        isRunning.value = false
        if (event.summary) {
          flowSummary.value = event.summary
        }
        structuredLogs.value.push({
          id: `log-${Date.now()}-${Math.random().toString(36).substring(2, 6)}`,
          timestamp: timeStr,
          level: 'error',
          message: `Execução do fluxo finalizada com falhas.`
        })
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

  const historyList = ref<any[]>([])

  async function fetchExecutionHistory(flowId?: string, baseUrl: string = 'http://localhost:8000'): Promise<void> {
    try {
      const url = flowId ? `${baseUrl}/api/v1/executions?flow_id=${flowId}` : `${baseUrl}/api/v1/executions`
      const res = await fetch(url)
      if (res.ok) {
        historyList.value = await res.json()
      }
    } catch {
      // Ignore in test or offline
    }
  }

  async function retryExecution(
    executionId: string,
    mode: 'freeze' | 'unfreeze' = 'freeze',
    baseUrl: string = 'http://localhost:8000'
  ): Promise<any> {
    isRunning.value = true
    try {
      const res = await fetch(`${baseUrl}/api/v1/executions/${executionId}/retry?mode=${mode}`, {
        method: 'POST',
      })
      if (!res.ok) {
        throw new Error(`Retry failed: ${res.statusText}`)
      }
      const data = await res.json()
      flowSummary.value = data
      await fetchExecutionHistory(undefined, baseUrl)
      return data
    } finally {
      isRunning.value = false
    }
  }

  return {
    isRunning,
    nodeStates,
    flowSummary,
    logs,
    structuredLogs,
    isDrawerOpen,
    activeDrawerTab,
    historyList,
    resetExecution,
    getNodeState,
    handleEvent,
    runFlowStream,
    fetchExecutionHistory,
    retryExecution,
  }
})
