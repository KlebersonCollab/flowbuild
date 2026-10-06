<script setup lang="ts">
import { useFlowStore } from '../stores/flowStore'
import { useExecutionStore } from '../stores/executionStore'

const flowStore = useFlowStore()
const executionStore = useExecutionStore()

async function onRunFlow() {
  const payload = flowStore.toFlowPayload()
  await executionStore.runFlowStream(payload)
}

function onExportJson() {
  const payload = flowStore.toFlowPayload()
  const dataStr = 'data:text/json;charset=utf-8,' + encodeURIComponent(JSON.stringify(payload, null, 2))
  const downloadAnchor = document.createElement('a')
  downloadAnchor.setAttribute('href', dataStr)
  downloadAnchor.setAttribute('download', `${payload.name.toLowerCase().replace(/\s+/g, '-')}.json`)
  document.body.appendChild(downloadAnchor)
  downloadAnchor.click()
  downloadAnchor.remove()
}

function onClearCanvas() {
  if (confirm('Deseja limpar todos os nós e conexões do canvas?')) {
    flowStore.nodes = []
    flowStore.edges = []
    flowStore.selectedNodeId = null
    executionStore.resetExecution()
  }
}
</script>

<template>
  <header class="h-14 border-b border-[#23252a] bg-[#010102] text-[#f7f8f8] px-4 flex items-center justify-between select-none shrink-0 z-20">
    <!-- Brand / Title -->
    <div class="flex items-center space-x-3">
      <div class="h-7 w-7 rounded-md bg-[#5e6ad2] flex items-center justify-center font-bold text-white shadow-md shadow-[#5e6ad2]/20">
        FB
      </div>
      <div>
        <div class="flex items-center space-x-2">
          <input
            v-model="flowStore.flowName"
            type="text"
            class="text-sm font-semibold text-[#f7f8f8] bg-transparent border border-transparent hover:border-[#23252a] focus:border-[#5e6ad2] rounded px-1.5 py-0.5 outline-none transition-colors"
          />
          <span class="text-[10px] px-1.5 py-0.5 rounded bg-[#141516] text-[#8a8f98] font-mono border border-[#23252a]">
            v0.1.0
          </span>
        </div>
      </div>
    </div>

    <!-- Actions -->
    <div class="flex items-center space-x-2.5">
      <!-- Clear Canvas -->
      <button
        @click="onClearCanvas"
        class="text-xs px-3 py-1.5 rounded-md bg-[#0f1011] hover:bg-[#141516] text-[#8a8f98] hover:text-[#f7f8f8] border border-[#23252a] transition-colors"
      >
        Limpar
      </button>

      <!-- Export JSON -->
      <button
        @click="onExportJson"
        class="text-xs px-3 py-1.5 rounded-md bg-[#0f1011] hover:bg-[#141516] text-[#f7f8f8] border border-[#23252a] transition-colors flex items-center space-x-1.5"
      >
        <span>Exportar JSON</span>
      </button>

      <!-- Run Flow (Button Primary - Linear Token) -->
      <button
        @click="onRunFlow"
        :disabled="executionStore.isRunning"
        class="text-xs font-medium px-4 py-1.5 rounded-md bg-[#5e6ad2] hover:bg-[#828fff] disabled:opacity-50 text-white shadow-sm transition-all flex items-center space-x-1.5 active:bg-[#5e69d1]"
      >
        <span v-if="executionStore.isRunning" class="h-3 w-3 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
        <span>{{ executionStore.isRunning ? 'Executando...' : 'Executar Fluxo' }}</span>
      </button>
    </div>
  </header>
</template>
