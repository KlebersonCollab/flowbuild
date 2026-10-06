<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRegistryStore } from '../stores/registryStore'
import { useFlowStore } from '../stores/flowStore'
import type { ComponentDefinition } from '../types/flow'

const registryStore = useRegistryStore()
const flowStore = useFlowStore()
const searchQuery = ref<string>('')

const filteredCategories = computed(() => {
  const q = searchQuery.value.toLowerCase().trim()
  const result: Record<string, ComponentDefinition[]> = {}

  for (const [category, list] of Object.entries(registryStore.categorizedComponents)) {
    const matched = list.filter(
      (c) =>
        c.displayName.toLowerCase().includes(q) ||
        c.name.toLowerCase().includes(q) ||
        (c.description && c.description.toLowerCase().includes(q))
    )
    if (matched.length > 0) {
      result[category] = matched
    }
  }

  return result
})

function onAddNode(comp: ComponentDefinition) {
  // Extract default values for inputs
  const initialInputs: Record<string, any> = {}
  for (const inp of comp.inputs) {
    if (inp.default !== undefined && inp.default !== null) {
      initialInputs[inp.name] = inp.default
    }
  }

  // Position staggered
  const count = flowStore.nodes.length
  const pos = { x: 100 + (count % 4) * 80, y: 120 + (count % 4) * 60 }
  flowStore.addNode(comp.name, pos, initialInputs)
}

function onDragStart(event: DragEvent, comp: ComponentDefinition) {
  if (event.dataTransfer) {
    event.dataTransfer.setData('application/flowbuild-node', JSON.stringify(comp))
    event.dataTransfer.effectAllowed = 'move'
  }
}
</script>

<template>
  <aside class="w-72 border-r border-[#23252a] bg-[#0f1011] text-[#f7f8f8] flex flex-col h-full select-none">
    <!-- Palette Header & Search -->
    <div class="p-3 border-b border-[#23252a] bg-[#141516] space-y-2">
      <div class="flex items-center justify-between">
        <span class="text-xs font-semibold tracking-wider uppercase text-[#8a8f98]">Componentes</span>
        <span class="text-[10px] text-[#62666d] font-mono">{{ registryStore.components.length }} tipos</span>
      </div>
      <input
        v-model="searchQuery"
        type="text"
        placeholder="Buscar nós de automação..."
        class="w-full text-xs rounded-md bg-[#0f1011] border border-[#23252a] px-2.5 py-1.5 text-[#f7f8f8] placeholder-[#62666d] focus:border-[#5e6ad2] focus:ring-1 focus:ring-[#5e6ad2] outline-none transition-colors"
      />
    </div>

    <!-- Category Groups -->
    <div class="flex-1 overflow-y-auto p-3 space-y-4">
      <div
        v-for="(list, category) in filteredCategories"
        :key="category"
        class="space-y-1.5"
      >
        <div class="text-[11px] font-semibold tracking-wider uppercase text-[#8a8f98] px-1">
          {{ category }}
        </div>

        <div class="space-y-1">
          <div
            v-for="comp in list"
            :key="comp.name"
            draggable="true"
            @dragstart="onDragStart($event, comp)"
            @click="onAddNode(comp)"
            class="group flex items-start space-x-2.5 p-2 rounded-md bg-[#141516] border border-[#23252a] hover:border-[#5e6ad2]/70 hover:bg-[#18191a] transition-all cursor-pointer"
          >
            <div class="h-6 w-6 rounded bg-[#23252a] group-hover:bg-[#5e6ad2]/20 flex items-center justify-center text-xs text-[#d0d6e0] group-hover:text-[#828fff] transition-colors shrink-0">
              ⚡
            </div>
            <div class="flex-1 min-w-0">
              <div class="text-xs font-medium text-[#f7f8f8] truncate group-hover:text-white">
                {{ comp.displayName }}
              </div>
              <p class="text-[10px] text-[#8a8f98] truncate leading-tight">
                {{ comp.description }}
              </p>
            </div>
          </div>
        </div>
      </div>

      <div
        v-if="Object.keys(filteredCategories).length === 0"
        class="py-8 text-center text-xs text-[#62666d]"
      >
        Nenhum componente encontrado
      </div>
    </div>
  </aside>
</template>
