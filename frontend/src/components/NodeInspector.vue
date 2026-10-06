<script setup lang="ts">
import { computed } from 'vue'
import { useFlowStore } from '../stores/flowStore'
import { useRegistryStore } from '../stores/registryStore'
import { useExecutionStore } from '../stores/executionStore'

const flowStore = useFlowStore()
const registryStore = useRegistryStore()
const executionStore = useExecutionStore()

const node = computed(() => flowStore.selectedNode)
const definition = computed(() => {
  if (!node.value) return null
  return registryStore.getComponent(node.value.type)
})

const nodeState = computed(() => {
  if (!node.value) return null
  return executionStore.getNodeState(node.value.id)
})

function getInputValue(fieldName: string, defaultValue: any) {
  if (!node.value?.data?.inputs) return defaultValue
  const val = node.value.data.inputs[fieldName]
  return val !== undefined ? val : defaultValue
}

function onFieldChange(fieldName: string, value: any) {
  if (!node.value) return
  flowStore.updateNodeInput(node.value.id, fieldName, value)
}

function deleteCurrentNode() {
  if (!node.value) return
  flowStore.removeNode(node.value.id)
}
</script>

<template>
  <aside class="w-80 border-l border-[#23252a] bg-[#0f1011] text-[#f7f8f8] flex flex-col h-full overflow-hidden select-none">
    <!-- Header -->
    <div class="p-4 border-b border-[#23252a] flex items-center justify-between bg-[#141516]">
      <div>
        <h3 class="text-sm font-semibold tracking-tight text-[#f7f8f8]">
          {{ definition?.displayName || 'Node Inspector' }}
        </h3>
        <p class="text-[11px] text-[#8a8f98] font-mono truncate max-w-[180px]">
          {{ node?.id || 'Nenhum nó selecionado' }}
        </p>
      </div>
      <button
        v-if="node"
        @click="deleteCurrentNode"
        class="text-xs text-rose-400 hover:text-rose-300 px-2 py-1 rounded bg-rose-500/10 hover:bg-rose-500/20 transition-colors"
        title="Excluir Nó"
      >
        Excluir
      </button>
    </div>

    <!-- Inspector Body -->
    <div v-if="node && definition" class="flex-1 overflow-y-auto p-4 space-y-4">
      <!-- Node Description -->
      <p v-if="definition.description" class="text-xs text-[#8a8f98] leading-relaxed">
        {{ definition.description }}
      </p>

      <!-- Dynamic Form Inputs -->
      <div class="space-y-3 pt-2">
        <div
          v-for="input in definition.inputs"
          :key="input.name"
          class="space-y-1.5"
        >
          <label class="block text-xs font-medium text-[#d0d6e0]">
            {{ input.label }}
            <span v-if="input.required" class="text-[#5e6ad2]">*</span>
          </label>

          <!-- String / URL Input -->
          <input
            v-if="input.type === 'str'"
            type="text"
            :value="getInputValue(input.name, input.default || '')"
            @input="onFieldChange(input.name, ($event.target as HTMLInputElement).value)"
            :placeholder="input.placeholder || ''"
            class="w-full text-xs rounded-md bg-[#141516] border border-[#23252a] px-2.5 py-1.5 text-[#f7f8f8] placeholder-[#62666d] focus:border-[#5e6ad2] focus:ring-1 focus:ring-[#5e6ad2] outline-none transition-colors"
          />

          <!-- Number / Int / Float Input -->
          <input
            v-else-if="input.type === 'int' || input.type === 'float'"
            type="number"
            :value="getInputValue(input.name, input.default ?? 0)"
            @input="onFieldChange(input.name, Number(($event.target as HTMLInputElement).value))"
            class="w-full text-xs rounded-md bg-[#141516] border border-[#23252a] px-2.5 py-1.5 text-[#f7f8f8] focus:border-[#5e6ad2] focus:ring-1 focus:ring-[#5e6ad2] outline-none transition-colors"
          />

          <!-- Select Dropdown Input -->
          <select
            v-else-if="input.type === 'select'"
            :value="getInputValue(input.name, input.default)"
            @change="onFieldChange(input.name, ($event.target as HTMLSelectElement).value)"
            class="w-full text-xs rounded-md bg-[#141516] border border-[#23252a] px-2.5 py-1.5 text-[#f7f8f8] focus:border-[#5e6ad2] focus:ring-1 focus:ring-[#5e6ad2] outline-none transition-colors cursor-pointer"
          >
            <option
              v-for="opt in input.options || []"
              :key="opt"
              :value="opt"
              class="bg-[#141516] text-[#f7f8f8]"
            >
              {{ opt }}
            </option>
          </select>

          <!-- Boolean Toggle -->
          <label
            v-else-if="input.type === 'bool'"
            class="flex items-center space-x-2 text-xs text-[#d0d6e0] cursor-pointer pt-1"
          >
            <input
              type="checkbox"
              :checked="Boolean(getInputValue(input.name, input.default || false))"
              @change="onFieldChange(input.name, ($event.target as HTMLInputElement).checked)"
              class="rounded bg-[#141516] border-[#23252a] text-[#5e6ad2] focus:ring-[#5e6ad2]"
            />
            <span>Ativo</span>
          </label>

          <!-- Code or Dictionary (Multiline Textarea) -->
          <textarea
            v-else-if="input.type === 'code' || input.type === 'dict'"
            :value="typeof getInputValue(input.name, input.default) === 'object' ? JSON.stringify(getInputValue(input.name, input.default), null, 2) : getInputValue(input.name, input.default || '')"
            @input="onFieldChange(input.name, ($event.target as HTMLTextAreaElement).value)"
            rows="5"
            class="w-full font-mono text-xs rounded-md bg-[#141516] border border-[#23252a] p-2 text-[#f7f8f8] placeholder-[#62666d] focus:border-[#5e6ad2] focus:ring-1 focus:ring-[#5e6ad2] outline-none transition-colors leading-relaxed"
          ></textarea>

          <p v-if="input.description" class="text-[10px] text-[#62666d]">
            {{ input.description }}
          </p>
        </div>
      </div>

      <!-- Execution Telemetry Card -->
      <div v-if="nodeState && nodeState.status !== 'idle'" class="mt-4 pt-3 border-t border-[#23252a] space-y-2">
        <div class="flex items-center justify-between text-xs font-semibold">
          <span>Resultado de Execução</span>
          <span
            :class="[
              'px-2 py-0.5 rounded text-[10px] font-bold uppercase',
              nodeState.status === 'completed' ? 'bg-[#27a644]/20 text-[#27a644]' : '',
              nodeState.status === 'failed' ? 'bg-rose-500/20 text-rose-400' : '',
              nodeState.status === 'running' ? 'bg-[#5e6ad2]/20 text-[#828fff] animate-pulse' : '',
            ]"
          >
            {{ nodeState.status }}
          </span>
        </div>

        <div v-if="nodeState.output !== undefined" class="rounded bg-[#010102] p-2 text-[11px] font-mono text-[#d0d6e0] overflow-x-auto max-h-40 border border-[#23252a]">
          <pre>{{ JSON.stringify(nodeState.output, null, 2) }}</pre>
        </div>

        <div v-if="nodeState.error" class="rounded bg-rose-950/40 p-2 text-[11px] font-mono text-rose-400 border border-rose-900/50">
          {{ nodeState.error }}
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else class="flex-1 flex flex-col items-center justify-center p-6 text-center text-[#62666d]">
      <div class="h-10 w-10 mb-3 rounded-full border border-[#23252a] flex items-center justify-center text-[#8a8f98]">
        ◈
      </div>
      <p class="text-xs text-[#8a8f98]">Selecione um nó no canvas para inspecionar e editar suas propriedades.</p>
    </div>
  </aside>
</template>
