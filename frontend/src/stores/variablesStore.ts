import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { VariableItem } from '../types/flow'

export const useVariablesStore = defineStore('variables', () => {
  const variables = ref<VariableItem[]>([])
  const currentFlowId = ref<string>('')
  const selectedEnvironment = ref<'dev' | 'qa' | 'prd' | 'all'>('dev')
  const isLoading = ref<boolean>(false)
  const isModalOpen = ref<boolean>(false)

  const globalVariables = computed(() =>
    variables.value.filter((v) => v.scope === 'global')
  )

  const flowVariables = computed(() =>
    variables.value.filter((v) => v.scope === 'flow' && v.flow_id === currentFlowId.value)
  )

  function getVariablesForEnvironment(env: 'dev' | 'qa' | 'prd' | 'all'): VariableItem[] {
    if (env === 'all') return variables.value
    return variables.value.filter(
      (v) => (v.environment || 'all') === env || (v.environment || 'all') === 'all'
    )
  }

  async function fetchVariables(
    flowId?: string,
    baseUrl: string = 'http://localhost:8000'
  ): Promise<void> {
    if (flowId) {
      currentFlowId.value = flowId
    }
    isLoading.value = true
    try {
      const url = currentFlowId.value
        ? `${baseUrl}/api/v1/variables?flow_id=${encodeURIComponent(currentFlowId.value)}`
        : `${baseUrl}/api/v1/variables`
      const res = await fetch(url)
      if (res.ok) {
        variables.value = await res.json()
      }
    } catch {
      // Ignore network errors in offline/test mode
    } finally {
      isLoading.value = false
    }
  }

  async function createVariable(
    data: {
      key: string
      value: string
      scope: 'global' | 'flow'
      flow_id?: string | null
      environment?: 'dev' | 'qa' | 'prd' | 'all'
      is_secret?: boolean
    },
    baseUrl: string = 'http://localhost:8000'
  ): Promise<boolean> {
    const payload = {
      ...data,
      environment: data.environment || 'all',
      flow_id: data.scope === 'flow' ? (data.flow_id || currentFlowId.value) : null,
    }
    try {
      const res = await fetch(`${baseUrl}/api/v1/variables`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      })
      if (res.ok) {
        const created: VariableItem = await res.json()
        variables.value.push(created)
        return true
      }
      return false
    } catch {
      return false
    }
  }

  async function updateVariable(
    id: string,
    value: string,
    is_secret?: boolean,
    environment?: 'dev' | 'qa' | 'prd' | 'all',
    baseUrl: string = 'http://localhost:8000'
  ): Promise<boolean> {
    try {
      const res = await fetch(`${baseUrl}/api/v1/variables/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ value, is_secret, environment }),
      })
      if (res.ok) {
        const updated: VariableItem = await res.json()
        const idx = variables.value.findIndex((v) => v.id === id)
        if (idx !== -1) {
          variables.value[idx] = updated
        }
        return true
      }
      return false
    } catch {
      return false
    }
  }

  async function deleteVariable(
    id: string,
    baseUrl: string = 'http://localhost:8000'
  ): Promise<boolean> {
    try {
      const res = await fetch(`${baseUrl}/api/v1/variables/${id}`, {
        method: 'DELETE',
      })
      if (res.ok) {
        variables.value = variables.value.filter((v) => v.id !== id)
        return true
      }
      return false
    } catch {
      return false
    }
  }

  async function fetchResolvedVariables(
    flowId?: string,
    environment: string = 'dev',
    baseUrl: string = 'http://localhost:8000'
  ): Promise<Record<string, string>> {
    const targetId = flowId || currentFlowId.value
    const url = targetId
      ? `${baseUrl}/api/v1/variables/resolved?flow_id=${encodeURIComponent(targetId)}&environment=${encodeURIComponent(environment)}`
      : `${baseUrl}/api/v1/variables/resolved?environment=${encodeURIComponent(environment)}`
    try {
      const res = await fetch(url)
      if (res.ok) {
        return await res.json()
      }
      return {}
    } catch {
      return {}
    }
  }

  function openModal(flowId?: string) {
    if (flowId) currentFlowId.value = flowId
    isModalOpen.value = true
    fetchVariables()
  }

  function closeModal() {
    isModalOpen.value = false
  }

  return {
    variables,
    currentFlowId,
    selectedEnvironment,
    isLoading,
    isModalOpen,
    globalVariables,
    flowVariables,
    getVariablesForEnvironment,
    fetchVariables,
    createVariable,
    updateVariable,
    deleteVariable,
    fetchResolvedVariables,
    openModal,
    closeModal,
  }
})
