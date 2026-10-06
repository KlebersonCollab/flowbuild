<script setup lang="ts">
import { ref, computed } from 'vue'
import {
  Sliders,
  Activity,
  Trash2,
  Copy,
  Check,
  Clock,
  HelpCircle
} from 'lucide-vue-next'
import { useFlowStore } from '../stores/flowStore'
import { useRegistryStore } from '../stores/registryStore'
import { useExecutionStore } from '../stores/executionStore'

const flowStore = useFlowStore()
const registryStore = useRegistryStore()
const executionStore = useExecutionStore()

const activeTab = ref<'params' | 'telemetry'>('params')
const copied = ref(false)

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

function copyOutput() {
  if (!nodeState.value?.output) return
  navigator.clipboard.writeText(JSON.stringify(nodeState.value.output, null, 2))
  copied.value = true
  setTimeout(() => {
    copied.value = false
  }, 2000)
}
</script>

<template>
  <aside class="w-80 border-l border-[#23252a] bg-[#0f1011] text-[#f7f8f8] flex flex-col h-full overflow-hidden select-none z-10">
    <!-- Header -->
    <div class="p-3.5 border-b border-[#23252a] flex items-center justify-between bg-[#141516]">
      <div class="min-w-0">
        <h3 class="text-xs font-semibold tracking-tight text-[#f7f8f8] truncate">
          {{ definition?.displayName || 'Node Inspector' }}
        </h3>
        <p class="text-[10px] text-[#8a8f98] font-mono truncate">
          {{ node?.id || 'Nenhum nó selecionado' }}
        </p>
      </div>

      <button
        v-if="node"
        @click="deleteCurrentNode"
        class="h-7 px-2 rounded text-xs text-rose-400 hover:text-rose-300 bg-rose-500/10 hover:bg-rose-500/20 transition-colors flex items-center space-x-1"
        title="Excluir Nó"
      >
        <Trash2 class="h-3.5 w-3.5" />
        <span>Excluir</span>
      </button>
    </div>

    <!-- Inspector Tabs (when node is selected) -->
    <div v-if="node && definition" class="flex border-b border-[#23252a] bg-[#0c0d0e] p-1 gap-1 text-xs">
      <button
        @click="activeTab = 'params'"
        class="flex-1 py-1.5 rounded-md flex items-center justify-center space-x-1.5 transition-all font-medium"
        :class="activeTab === 'params' ? 'bg-[#18191a] text-white shadow-sm' : 'text-[#8a8f98] hover:text-[#f7f8f8]'"
      >
        <Sliders class="h-3 w-3" />
        <span>Parâmetros</span>
      </button>
      <button
        @click="activeTab = 'telemetry'"
        class="flex-1 py-1.5 rounded-md flex items-center justify-center space-x-1.5 transition-all font-medium"
        :class="activeTab === 'telemetry' ? 'bg-[#18191a] text-white shadow-sm' : 'text-[#8a8f98] hover:text-[#f7f8f8]'"
      >
        <Activity class="h-3 w-3" />
        <span>Saídas & Estado</span>
      </button>
    </div>

    <!-- Body: Empty State -->
    <div
      v-if="!node || !definition"
      class="flex-1 flex flex-col items-center justify-center p-6 text-center text-[#62666d] space-y-2"
    >
      <Sliders class="h-8 w-8 text-[#23252a]" />
      <p class="text-xs font-medium text-[#8a8f98]">Nenhum nó selecionado</p>
      <p class="text-[11px] text-[#62666d]">Clique em qualquer nó no canvas para configurar parâmetros e inspecionar retornos.</p>
    </div>

    <!-- Body: Parameters Tab -->
    <div v-else-if="activeTab === 'params'" class="flex-1 overflow-y-auto p-4 space-y-4">
      <!-- Node Description -->
      <p v-if="definition.description" class="text-xs text-[#8a8f98] leading-relaxed">
        {{ definition.description }}
      </p>

      <!-- Dynamic Form Inputs -->
      <div class="space-y-3.5 pt-1">
        <div
          v-for="input in definition.inputs"
          :key="input.name"
          class="space-y-1.5"
        >
          <div class="flex items-center justify-between">
            <label class="block text-xs font-medium text-[#d0d6e0]">
              {{ input.label }}
              <span v-if="input.required" class="text-[#5e6ad2] font-bold">*</span>
            </label>
            <span class="text-[9px] font-mono text-[#62666d] uppercase">{{ input.type }}</span>
          </div>

          <!-- String / URL Input -->
          <input
            v-if="input.type === 'str'"
            type="text"
            :value="getInputValue(input.name, input.default || '')"
            @input="onFieldChange(input.name, ($event.target as HTMLInputElement).value)"
            :placeholder="input.placeholder || 'Digite o valor...'"
            class="w-full text-xs rounded-md bg-[#141516] border border-[#23252a] px-3 py-1.5 text-[#f7f8f8] placeholder-[#62666d] focus:border-[#5e6ad2] focus:ring-1 focus:ring-[#5e6ad2] outline-none transition-colors"
          />

          <!-- Number / Int / Float Input -->
          <input
            v-else-if="input.type === 'int' || input.type === 'float'"
            type="number"
            :value="getInputValue(input.name, input.default ?? 0)"
            @input="onFieldChange(input.name, Number(($event.target as HTMLInputElement).value))"
            class="w-full text-xs rounded-md bg-[#141516] border border-[#23252a] px-3 py-1.5 text-[#f7f8f8] focus:border-[#5e6ad2] focus:ring-1 focus:ring-[#5e6ad2] outline-none transition-colors"
          />

          <!-- Select Dropdown Input -->
          <select
            v-else-if="input.type === 'select'"
            :value="getInputValue(input.name, input.default)"
            @change="onFieldChange(input.name, ($event.target as HTMLSelectElement).value)"
            class="w-full text-xs rounded-md bg-[#141516] border border-[#23252a] px-3 py-1.5 text-[#f7f8f8] focus:border-[#5e6ad2] focus:ring-1 focus:ring-[#5e6ad2] outline-none transition-colors cursor-pointer"
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
            class="flex items-center space-x-2.5 text-xs text-[#d0d6e0] cursor-pointer pt-1"
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
            rows="6"
            class="w-full font-mono text-xs rounded-md bg-[#141516] border border-[#23252a] p-2.5 text-[#f7f8f8] placeholder-[#62666d] focus:border-[#5e6ad2] focus:ring-1 focus:ring-[#5e6ad2] outline-none transition-colors leading-relaxed"
          ></textarea>

          <p v-if="input.description" class="text-[10px] text-[#62666d] flex items-center space-x-1">
            <HelpCircle class="h-2.5 w-2.5" />
            <span>{{ input.description }}</span>
          </p>
        </div>
      </div>
    </div>

    <!-- Body: Telemetry & Outputs Tab -->
    <div v-else class="flex-1 overflow-y-auto p-4 space-y-4 select-text">
      <div class="rounded-lg border border-[#23252a] bg-[#141516] p-3 space-y-3">
        <div class="flex items-center justify-between">
          <span class="text-xs font-semibold text-[#f7f8f8]">Estado do Nó</span>
          <span
            class="px-2 py-0.5 rounded text-[10px] font-bold uppercase"
            :class="[
              nodeState?.status === 'completed' ? 'bg-[#27a644]/20 text-[#27a644]' : '',
              nodeState?.status === 'failed' ? 'bg-rose-500/20 text-rose-400' : '',
              nodeState?.status === 'running' ? 'bg-[#5e6ad2]/20 text-[#828fff] animate-pulse' : '',
              nodeState?.status === 'idle' ? 'bg-[#23252a] text-[#8a8f98]' : '',
            ]"
          >
            {{ nodeState?.status || 'idle' }}
          </span>
        </div>

        <div v-if="nodeState?.durationMs" class="flex items-center space-x-1.5 text-xs text-[#8a8f98]">
          <Clock class="h-3.5 w-3.5" />
          <span>Tempo de execução: <strong class="text-white">{{ nodeState.durationMs }}ms</strong></span>
        </div>
      </div>

      <!-- Output Payload -->
      <div v-if="nodeState?.output" class="space-y-1.5">
        <div class="flex items-center justify-between">
          <span class="text-xs font-semibold text-[#d0d6e0]">Payload de Retorno</span>
          <button
            @click="copyOutput"
            class="text-[10px] px-2 py-0.5 rounded bg-[#23252a] hover:bg-[#34343a] text-[#8a8f98] hover:text-[#f7f8f8] flex items-center space-x-1"
          >
            <Check v-if="copied" class="h-3 w-3 text-[#27a644]" />
            <Copy v-else class="h-3 w-3" />
            <span>{{ copied ? 'Copiado' : 'Copiar' }}</span>
          </button>
        </div>
        <pre class="text-[11px] font-mono p-3 rounded-lg bg-[#0c0d0e] text-emerald-400 border border-[#23252a] overflow-x-auto leading-relaxed max-h-60">{{ JSON.stringify(nodeState.output, null, 2) }}</pre>
      </div>

      <!-- Error Trace -->
      <div v-else-if="nodeState?.error" class="space-y-1.5">
        <span class="text-xs font-semibold text-rose-400">Falha / Exceção</span>
        <pre class="text-[11px] font-mono p-3 rounded-lg bg-rose-500/10 text-rose-300 border border-rose-500/30 overflow-x-auto leading-relaxed">{{ nodeState.error }}</pre>
      </div>

      <!-- Idle state -->
      <div v-else class="text-xs text-[#62666d] text-center py-8">
        Execute o fluxo para visualizar as saídas geradas por este nó.
      </div>
    </div>
  </aside>
</template>
