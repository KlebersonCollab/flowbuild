import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { ComponentDefinition } from '../types/flow'

export const useRegistryStore = defineStore('registry', () => {
  const components = ref<ComponentDefinition[]>([])
  const isLoading = ref<boolean>(false)
  const error = ref<string | null>(null)

  const categorizedComponents = computed(() => {
    const map: Record<string, ComponentDefinition[]> = {}
    for (const comp of components.value) {
      const cat = comp.category || 'General'
      if (!map[cat]) {
        map[cat] = []
      }
      map[cat].push(comp)
    }
    return map
  })

  function setComponents(list: ComponentDefinition[]): void {
    components.value = list
  }

  function getComponent(name: string): ComponentDefinition | undefined {
    return components.value.find((c) => c.name === name)
  }

  async function fetchComponents(baseUrl: string = 'http://localhost:8000'): Promise<void> {
    isLoading.value = true
    error.value = null
    try {
      const res = await fetch(`${baseUrl}/api/v1/components`)
      if (!res.ok) {
        throw new Error(`Failed to load components: ${res.statusText}`)
      }
      const data: ComponentDefinition[] = await res.json()
      components.value = data
    } catch (err: any) {
      error.value = err.message || 'Unknown network error'
    } finally {
      isLoading.value = false
    }
  }

  return {
    components,
    isLoading,
    error,
    categorizedComponents,
    setComponents,
    getComponent,
    fetchComponents,
  }
})
