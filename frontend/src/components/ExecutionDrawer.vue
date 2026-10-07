<script setup lang="ts">
import { computed, ref, onMounted, onUnmounted, watch } from 'vue'
import {
  Terminal,
  Layers,
  FileCode,
  History,
  ChevronUp,
  ChevronDown,
  Trash2,
  Copy,
  Check,
  CheckCircle2,
  XCircle,
  Clock,
  RotateCw,
  Snowflake,
  RefreshCw,
  ExternalLink,
} from 'lucide-vue-next'
import { useExecutionStore } from '../stores/executionStore'
import { useFlowStore } from '../stores/flowStore'

const executionStore = useExecutionStore()
const flowStore = useFlowStore()

const copied = ref(false)
const isRefreshingHistory = ref(false)
const expandedExecutionId = ref<string | null>(null)
const copiedNodeOutputId = ref<string | null>(null)
let historyPollTimer: ReturnType<typeof setInterval> | null = null

const activeTab = computed({
  get: () => executionStore.activeDrawerTab,
  set: (val) => { executionStore.activeDrawerTab = val }
})

const isOpen = computed({
  get: () => executionStore.isDrawerOpen,
  set: (val) => { executionStore.isDrawerOpen = val }
})

const completedNodesList = computed(() => {
  const list: Array<{ id: string; type: string; state: any }> = []
  const seenNodeIds = new Set<string>()

  for (const node of flowStore.nodes) {
    seenNodeIds.add(node.id)
    list.push({
      id: node.id,
      type: node.type,
      state: executionStore.getNodeState(node.id),
    })
  }

  for (const [nodeId, state] of Object.entries(executionStore.nodeStates)) {
    if (!seenNodeIds.has(nodeId)) {
      list.push({
        id: nodeId,
        type: 'Nó Executado',
        state,
      })
    }
  }

  return list
})

function toggleExpandExecution(id: string) {
  expandedExecutionId.value = expandedExecutionId.value === id ? null : id
}

function getNodeLabel(nodeId: string): string {
  const node = flowStore.nodes.find((n) => n.id === nodeId)
  return node ? `${node.type} (${nodeId})` : nodeId
}

function copyNodeOutput(key: string, data: any) {
  navigator.clipboard.writeText(typeof data === 'string' ? data : JSON.stringify(data, null, 2))
  copiedNodeOutputId.value = key
  setTimeout(() => {
    copiedNodeOutputId.value = null
  }, 2000)
}

function loadExecutionIntoOutputs(record: any) {
  if (!record.node_states) return
  executionStore.loadExecution(record)
  activeTab.value = 'outputs'
}

function startHistoryPolling() {
  stopHistoryPolling()
  historyPollTimer = setInterval(async () => {
    if (isOpen.value && activeTab.value === 'history') {
      await executionStore.fetchExecutionHistory()
    }
  }, 3500)
}

function stopHistoryPolling() {
  if (historyPollTimer) {
    clearInterval(historyPollTimer)
    historyPollTimer = null
  }
}

watch(
  [isOpen, activeTab],
  ([open, tab]) => {
    if (open && tab === 'history') {
      executionStore.fetchExecutionHistory()
      startHistoryPolling()
    } else {
      stopHistoryPolling()
    }
  },
  { immediate: true }
)

onMounted(async () => {
  await executionStore.fetchExecutionHistory()
})

onUnmounted(() => {
  stopHistoryPolling()
})

async function refreshHistory() {
  isRefreshingHistory.value = true
  await executionStore.fetchExecutionHistory()
  setTimeout(() => {
    isRefreshingHistory.value = false
  }, 400)
}

function copyPayload() {
  const payload = flowStore.toFlowPayload()
  navigator.clipboard.writeText(JSON.stringify(payload, null, 2))
  copied.value = true
  setTimeout(() => {
    copied.value = false
  }, 2000)
}

function clearConsole() {
  executionStore.resetExecution()
}

function toggleDrawer() {
  isOpen.value = !isOpen.value
}

async function selectHistoryTab() {
  activeTab.value = 'history'
  await executionStore.fetchExecutionHistory()
}

async function onRetry(execId: string, mode: 'freeze' | 'unfreeze') {
  await executionStore.retryExecution(execId, mode)
}
</script>

<template>
  <div
    class="border-t border-[#23252a] bg-[#0c0d0e] text-[#f7f8f8] flex flex-col transition-all duration-300 shadow-2xl z-30 select-none"
    :class="isOpen ? 'h-80' : 'h-10'"
  >
    <!-- Drawer Header Bar -->
    <div
      @click="toggleDrawer"
      class="h-10 px-4 bg-[#141516] border-b border-[#23252a] flex items-center justify-between cursor-pointer hover:bg-[#18191a] transition-colors shrink-0"
    >
      <!-- Left: Status & Tabs -->
      <div class="flex items-center space-x-4">
        <!-- Live status icon / indicator -->
        <div class="flex items-center space-x-2">
          <div
            v-if="executionStore.isRunning"
            class="flex items-center space-x-1.5 text-xs font-semibold text-[#828fff]"
          >
            <span class="h-2 w-2 rounded-full bg-[#5e6ad2] animate-ping"></span>
            <span>Executando...</span>
          </div>
          <div
            v-else-if="executionStore.flowSummary?.status === 'completed'"
            class="flex items-center space-x-1.5 text-xs font-medium text-[#27a644]"
          >
            <CheckCircle2 class="h-3.5 w-3.5" />
            <span>Execução Concluída ({{ executionStore.flowSummary?.successful_nodes?.length || 0 }} nós)</span>
          </div>
          <div
            v-else-if="executionStore.flowSummary?.status === 'failed'"
            class="flex items-center space-x-1.5 text-xs font-medium text-rose-400"
          >
            <XCircle class="h-3.5 w-3.5" />
            <span>Falha na Execução</span>
          </div>
          <div
            v-else
            class="flex items-center space-x-1.5 text-xs text-[#8a8f98]"
          >
            <Terminal class="h-3.5 w-3.5 text-[#5e6ad2]" />
            <span class="font-medium text-[#d0d6e0]">Console de Execução</span>
          </div>
        </div>

        <!-- Navigation Tabs (Only when open) -->
        <div
          v-if="isOpen"
          @click.stop
          class="flex items-center bg-[#0a0a0c] p-0.5 rounded-lg border border-[#23252a] text-xs font-medium"
        >
          <button
            @click="activeTab = 'logs'"
            class="flex items-center space-x-1.5 px-3 py-1 rounded-md transition-all"
            :class="activeTab === 'logs' ? 'bg-[#23252a] text-white shadow-sm' : 'text-[#8a8f98] hover:text-[#f7f8f8]'"
          >
            <Terminal class="h-3 w-3" />
            <span>Logs</span>
            <span
              v-if="executionStore.structuredLogs.length"
              class="text-[10px] px-1.5 py-0.2 rounded-full bg-[#5e6ad2]/20 text-[#828fff] font-mono"
            >
              {{ executionStore.structuredLogs.length }}
            </span>
          </button>

          <button
            @click="activeTab = 'outputs'"
            class="flex items-center space-x-1.5 px-3 py-1 rounded-md transition-all"
            :class="activeTab === 'outputs' ? 'bg-[#23252a] text-white shadow-sm' : 'text-[#8a8f98] hover:text-[#f7f8f8]'"
          >
            <Layers class="h-3 w-3" />
            <span>Resultados dos Nós</span>
          </button>

          <button
            @click="activeTab = 'payload'"
            class="flex items-center space-x-1.5 px-3 py-1 rounded-md transition-all"
            :class="activeTab === 'payload' ? 'bg-[#23252a] text-white shadow-sm' : 'text-[#8a8f98] hover:text-[#f7f8f8]'"
          >
            <FileCode class="h-3 w-3" />
            <span>JSON do Fluxo</span>
          </button>

          <button
            @click="selectHistoryTab"
            class="flex items-center space-x-1.5 px-3 py-1 rounded-md transition-all"
            :class="activeTab === 'history' ? 'bg-[#23252a] text-white shadow-sm' : 'text-[#8a8f98] hover:text-[#f7f8f8]'"
          >
            <History class="h-3 w-3 text-[#5e6ad2]" />
            <span>Histórico & Retry</span>
            <span
              v-if="executionStore.historyList.length"
              class="text-[10px] px-1.5 py-0.2 rounded-full bg-[#18191a] text-[#8a8f98] font-mono"
            >
              {{ executionStore.historyList.length }}
            </span>
          </button>
        </div>
      </div>

      <!-- Right: Drawer Actions -->
      <div class="flex items-center space-x-2" @click.stop>
        <button
          v-if="isOpen"
          @click="clearConsole"
          class="h-7 px-2.5 rounded text-xs text-[#8a8f98] hover:text-[#f7f8f8] hover:bg-[#23252a] flex items-center space-x-1 transition-colors"
          title="Limpar Console"
        >
          <Trash2 class="h-3.5 w-3.5" />
          <span>Limpar</span>
        </button>

        <button
          @click="toggleDrawer"
          class="h-7 w-7 rounded flex items-center justify-center text-[#8a8f98] hover:text-[#f7f8f8] hover:bg-[#23252a] transition-colors"
          :title="isOpen ? 'Recolher console' : 'Expandir console'"
        >
          <ChevronDown v-if="isOpen" class="h-4 w-4" />
          <ChevronUp v-else class="h-4 w-4" />
        </button>
      </div>
    </div>

    <!-- Drawer Body Area -->
    <div v-if="isOpen" class="flex-1 overflow-hidden bg-[#090a0b] flex flex-col">
      <!-- TAB 1: Structured Execution Logs -->
      <div
        v-if="activeTab === 'logs'"
        class="flex-1 overflow-y-auto p-3 font-mono text-[11px] space-y-1.5 select-text"
      >
        <div
          v-if="executionStore.structuredLogs.length === 0"
          class="h-full flex flex-col items-center justify-center text-[#62666d] space-y-2 py-8"
        >
          <Terminal class="h-6 w-6 text-[#34343a]" />
          <p class="text-xs">Nenhum evento registrado. Clique em "Executar Fluxo" para ver o stream de eventos em tempo real.</p>
        </div>

        <div
          v-for="item in executionStore.structuredLogs"
          :key="item.id"
          class="flex items-start space-x-3 py-1 px-2 rounded hover:bg-[#141516]/60 transition-colors border-l-2"
          :class="[
            item.level === 'success' ? 'border-[#27a644] bg-[#27a644]/5' : '',
            item.level === 'error' ? 'border-rose-500 bg-rose-500/5' : '',
            item.level === 'warn' ? 'border-amber-500 bg-amber-500/5' : '',
            item.level === 'info' ? 'border-[#5e6ad2] bg-[#5e6ad2]/5' : '',
          ]"
        >
          <span class="text-[#62666d] shrink-0">{{ item.timestamp }}</span>
          <span
            class="px-1.5 py-0.2 rounded text-[10px] font-bold shrink-0 uppercase tracking-wider"
            :class="[
              item.level === 'success' ? 'text-[#27a644] bg-[#27a644]/15' : '',
              item.level === 'error' ? 'text-rose-400 bg-rose-500/15' : '',
              item.level === 'warn' ? 'text-amber-400 bg-amber-500/15' : '',
              item.level === 'info' ? 'text-[#828fff] bg-[#5e6ad2]/15' : '',
            ]"
          >
            {{ item.level }}
          </span>
          <span class="flex-1 text-[#f7f8f8] leading-relaxed break-words">
            {{ item.message }}
          </span>
          <span v-if="item.durationMs" class="text-[#8a8f98] shrink-0 flex items-center space-x-1">
            <Clock class="h-2.5 w-2.5" />
            <span>{{ item.durationMs }}ms</span>
          </span>
        </div>
      </div>

      <!-- TAB 2: Node Output Inspector -->
      <div
        v-else-if="activeTab === 'outputs'"
        class="flex-1 overflow-y-auto p-4 space-y-3 select-text"
      >
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
          <div
            v-for="item in completedNodesList"
            :key="item.id"
            class="rounded-lg border border-[#23252a] bg-[#141516] p-3 flex flex-col space-y-2"
          >
            <div class="flex items-center justify-between border-b border-[#23252a] pb-2">
              <span class="text-xs font-semibold text-[#f7f8f8]">{{ item.type }}</span>
              <span
                class="text-[10px] font-bold px-2 py-0.5 rounded uppercase"
                :class="[
                  item.state.status === 'completed' ? 'bg-[#27a644]/15 text-[#27a644]' : '',
                  item.state.status === 'failed' ? 'bg-rose-500/15 text-rose-400' : '',
                  item.state.status === 'running' ? 'bg-[#5e6ad2]/15 text-[#828fff]' : '',
                  item.state.status === 'skipped' ? 'bg-amber-500/15 text-amber-400' : '',
                  item.state.status === 'idle' ? 'bg-[#23252a] text-[#8a8f98]' : '',
                ]"
              >
                {{ item.state.status }}
              </span>
            </div>

            <div class="flex-1">
              <div v-if="item.state.output" class="space-y-1">
                <span class="text-[10px] font-mono text-[#8a8f98] uppercase">Output Payload:</span>
                <pre class="text-[11px] font-mono p-2 rounded bg-[#090a0b] text-emerald-400 border border-[#23252a] max-h-32 overflow-y-auto leading-relaxed">{{ JSON.stringify(item.state.output, null, 2) }}</pre>
              </div>
              <div v-else-if="item.state.error" class="space-y-1">
                <span class="text-[10px] font-mono text-rose-400 uppercase">Error:</span>
                <pre class="text-[11px] font-mono p-2 rounded bg-rose-500/10 text-rose-300 border border-rose-500/30 max-h-32 overflow-y-auto">{{ item.state.error }}</pre>
              </div>
              <div v-else class="text-xs text-[#62666d] py-3 text-center">
                Aguardando execução deste nó...
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- TAB 3: Flow JSON Payload -->
      <div
        v-else-if="activeTab === 'payload'"
        class="flex-1 overflow-hidden flex flex-col p-3 select-text"
      >
        <div class="flex items-center justify-between pb-2">
          <span class="text-xs text-[#8a8f98] font-mono">Payload canônico serializado para a DAG FastAPI</span>
          <button
            @click="copyPayload"
            class="flex items-center space-x-1.5 px-3 py-1 rounded bg-[#23252a] hover:bg-[#34343a] text-xs text-[#f7f8f8] transition-colors"
          >
            <Check v-if="copied" class="h-3.5 w-3.5 text-[#27a644]" />
            <Copy v-else class="h-3.5 w-3.5" />
            <span>{{ copied ? 'Copiado!' : 'Copiar JSON' }}</span>
          </button>
        </div>
        <pre class="flex-1 overflow-y-auto p-3 rounded-lg bg-[#0c0d0e] text-[#828fff] font-mono text-[11px] border border-[#23252a] leading-relaxed">{{ JSON.stringify(flowStore.toFlowPayload(), null, 2) }}</pre>
      </div>

      <!-- TAB 4: Execution History & Freeze/Unfreeze Retry -->
      <div
        v-else-if="activeTab === 'history'"
        class="flex-1 overflow-y-auto p-4 space-y-2 select-text"
      >
        <!-- History Action Bar -->
        <div class="flex items-center justify-between pb-2 border-b border-[#23252a]/60 mb-2">
          <div class="flex items-center space-x-2 text-xs text-[#8a8f98]">
            <span class="font-medium text-white">Histórico de Execuções</span>
            <span class="flex items-center space-x-1 text-[10px] text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded-full font-mono">
              <span class="h-1.5 w-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
              <span>Sincronização em Tempo Real</span>
            </span>
          </div>

          <button
            @click="refreshHistory"
            :disabled="isRefreshingHistory"
            class="text-xs px-2.5 py-1 rounded bg-[#141516] hover:bg-[#23252a] text-[#d0d6e0] hover:text-white border border-[#23252a] flex items-center space-x-1.5 transition-colors"
            title="Atualizar histórico imediatamente"
          >
            <RefreshCw class="h-3 w-3" :class="isRefreshingHistory ? 'animate-spin text-[#5e6ad2]' : ''" />
            <span>Atualizar</span>
          </button>
        </div>
        <div
          v-if="executionStore.historyList.length === 0"
          class="h-full flex flex-col items-center justify-center text-[#62666d] space-y-2 py-8"
        >
          <History class="h-6 w-6 text-[#34343a]" />
          <p class="text-xs">Nenhuma execução registrada no banco de dados.</p>
        </div>

        <div
          v-for="record in executionStore.historyList"
          :key="record.id"
          class="rounded-lg border border-[#23252a] bg-[#141516] overflow-hidden hover:border-[#3e3e44] transition-all"
        >
          <!-- Main Card Header -->
          <div
            @click="toggleExpandExecution(record.id)"
            class="p-3 flex items-center justify-between cursor-pointer select-none bg-[#141516] hover:bg-[#18191a] transition-colors"
          >
            <div class="flex items-center space-x-3 min-w-0">
              <!-- Expand / Collapse chevron -->
              <button
                class="text-[#8a8f98] hover:text-white p-0.5 rounded transition-transform"
                :title="expandedExecutionId === record.id ? 'Recolher detalhes' : 'Ver resultados dos nós'"
              >
                <ChevronDown
                  class="h-4 w-4 transition-transform duration-200"
                  :class="expandedExecutionId === record.id ? 'rotate-180 text-[#5e6ad2]' : ''"
                />
              </button>

              <!-- Status Badge -->
              <span
                class="px-2 py-0.5 rounded text-[10px] font-bold uppercase shrink-0"
                :class="[
                  record.status === 'completed' ? 'bg-[#27a644]/15 text-[#27a644]' : '',
                  record.status === 'failed' ? 'bg-rose-500/15 text-rose-400' : '',
                  record.status === 'running' ? 'bg-[#5e6ad2]/15 text-[#828fff]' : '',
                ]"
              >
                {{ record.status }}
              </span>

              <div class="min-w-0">
                <div class="flex items-center space-x-2 text-xs font-semibold text-white truncate">
                  <span>{{ record.flow_id }}</span>
                  <span class="text-[10px] font-mono text-[#8a8f98] px-1.5 py-0.2 rounded bg-[#090a0b] border border-[#23252a]">
                    {{ record.trigger_type }}
                  </span>
                  <!-- Count of completed nodes -->
                  <span
                    v-if="record.node_states && Object.keys(record.node_states).length"
                    class="text-[10px] font-mono text-cyan-400 bg-cyan-500/10 border border-cyan-500/20 px-1.5 py-0.2 rounded"
                  >
                    {{ Object.keys(record.node_states).length }} nós
                  </span>
                </div>
                <div class="flex items-center space-x-3 text-[10px] text-[#8a8f98] pt-0.5 font-mono">
                  <span>{{ record.started_at ? new Date(record.started_at).toLocaleTimeString() : '' }}</span>
                  <span>•</span>
                  <span>{{ record.duration_ms ? `${record.duration_ms.toFixed(0)}ms` : '0ms' }}</span>
                  <span v-if="record.error_message" class="text-rose-400 truncate">• {{ record.error_message }}</span>
                </div>
              </div>
            </div>

            <!-- Card Actions -->
            <div class="flex items-center space-x-2 shrink-0" @click.stop>
              <!-- Toggle Details Button -->
              <button
                @click="toggleExpandExecution(record.id)"
                class="text-xs px-2.5 py-1 rounded bg-[#090a0b] hover:bg-[#1f2024] border border-[#23252a] text-[#d0d6e0] flex items-center space-x-1 transition-colors"
                title="Ver nós e outputs desta execução"
              >
                <Layers class="h-3 w-3 text-cyan-400" />
                <span>{{ expandedExecutionId === record.id ? 'Ocultar Nós' : 'Ver Resultados' }}</span>
              </button>

              <!-- Freeze Retry -->
              <button
                @click="onRetry(record.id, 'freeze')"
                :disabled="executionStore.isRunning"
                class="text-xs px-2.5 py-1 rounded bg-[#090a0b] hover:bg-[#5e6ad2]/20 border border-[#5e6ad2]/40 text-[#828fff] flex items-center space-x-1 transition-all disabled:opacity-50"
                title="Retry Freeze: Re-executa preservando upstream"
              >
                <Snowflake class="h-3 w-3 text-[#828fff]" />
                <span class="hidden sm:inline">Retry Freeze</span>
              </button>

              <!-- Unfreeze Retry -->
              <button
                @click="onRetry(record.id, 'unfreeze')"
                :disabled="executionStore.isRunning"
                class="text-xs px-2.5 py-1 rounded bg-[#23252a] hover:bg-[#34343a] text-white flex items-center space-x-1 transition-all disabled:opacity-50"
                title="Retry Unfreeze: Re-executa do zero"
              >
                <RotateCw class="h-3 w-3" />
                <span class="hidden sm:inline">Retry Unfreeze</span>
              </button>
            </div>
          </div>

          <!-- Expanded Node States & Payload Panel -->
          <div
            v-if="expandedExecutionId === record.id"
            class="p-3.5 bg-[#0a0b0d] border-t border-[#23252a] space-y-3"
          >
            <!-- Quick Action Bar -->
            <div class="flex items-center justify-between text-xs pb-1 border-b border-[#23252a]/60 font-mono">
              <span class="text-[#8a8f98]">ID: <span class="text-white">{{ record.id }}</span></span>
              <button
                @click="loadExecutionIntoOutputs(record)"
                class="text-[11px] text-[#5e6ad2] hover:text-[#828fff] flex items-center space-x-1 transition-colors font-sans"
              >
                <ExternalLink class="h-3 w-3" />
                <span>Inspecionar no painel "Resultados dos Nós"</span>
              </button>
            </div>

            <!-- Initial Payload (if present) -->
            <div
              v-if="record.initial_payload && Object.keys(record.initial_payload).length > 0"
              class="rounded bg-[#141516] border border-[#23252a] p-2.5 space-y-1.5"
            >
              <div class="flex items-center justify-between">
                <span class="text-[10px] font-mono text-[#8a8f98] uppercase font-semibold">Payload Inicial (Trigger Input)</span>
                <button
                  @click="copyNodeOutput(`init-${record.id}`, record.initial_payload)"
                  class="text-[10px] text-[#8a8f98] hover:text-white flex items-center space-x-1"
                >
                  <Check v-if="copiedNodeOutputId === `init-${record.id}`" class="h-2.5 w-2.5 text-[#27a644]" />
                  <Copy v-else class="h-2.5 w-2.5" />
                  <span>{{ copiedNodeOutputId === `init-${record.id}` ? 'Copiado' : 'Copiar' }}</span>
                </button>
              </div>
              <pre class="text-[11px] font-mono p-2 rounded bg-[#090a0b] text-cyan-300 border border-[#23252a] max-h-36 overflow-y-auto leading-relaxed">{{ JSON.stringify(record.initial_payload, null, 2) }}</pre>
            </div>

            <!-- Node States Grid -->
            <div class="space-y-2">
              <div class="flex items-center justify-between">
                <span class="text-xs font-medium text-white flex items-center space-x-1.5">
                  <Layers class="h-3.5 w-3.5 text-[#5e6ad2]" />
                  <span>Resultados dos Nós Executados</span>
                </span>
                <span class="text-[10px] font-mono text-[#8a8f98]">
                  {{ record.node_states ? Object.keys(record.node_states).length : 0 }} nós registrados
                </span>
              </div>

              <div
                v-if="!record.node_states || Object.keys(record.node_states).length === 0"
                class="text-xs text-[#62666d] py-3 text-center italic"
              >
                Nenhum estado de nó individual foi gravado para esta execução.
              </div>

              <div v-else class="grid grid-cols-1 md:grid-cols-2 gap-2.5">
                <div
                  v-for="[nodeId, nodeState] in Object.entries(record.node_states)"
                  :key="nodeId"
                  class="rounded-lg border border-[#23252a] bg-[#141516] p-2.5 flex flex-col space-y-1.5"
                >
                  <div class="flex items-center justify-between border-b border-[#23252a]/80 pb-1.5">
                    <span class="text-xs font-medium text-white truncate" :title="getNodeLabel(nodeId)">
                      {{ getNodeLabel(nodeId) }}
                    </span>
                    <span
                      class="text-[9px] font-bold px-1.5 py-0.2 rounded uppercase shrink-0"
                      :class="[
                        (nodeState as any).status === 'completed' ? 'bg-[#27a644]/15 text-[#27a644]' : '',
                        (nodeState as any).status === 'failed' ? 'bg-rose-500/15 text-rose-400' : '',
                        (nodeState as any).status === 'skipped' ? 'bg-amber-500/15 text-amber-400' : 'bg-[#23252a] text-[#8a8f98]',
                      ]"
                    >
                      {{ (nodeState as any).status }}
                    </span>
                  </div>

                  <div class="flex-1">
                    <div v-if="(nodeState as any).output !== undefined" class="space-y-1">
                      <div class="flex items-center justify-between text-[10px] font-mono text-[#8a8f98]">
                        <span class="uppercase">Output:</span>
                        <button
                          @click="copyNodeOutput(`${record.id}-${nodeId}`, (nodeState as any).output)"
                          class="hover:text-white flex items-center space-x-1"
                        >
                          <Check v-if="copiedNodeOutputId === `${record.id}-${nodeId}`" class="h-2.5 w-2.5 text-[#27a644]" />
                          <Copy v-else class="h-2.5 w-2.5" />
                          <span>{{ copiedNodeOutputId === `${record.id}-${nodeId}` ? 'Copiado' : 'Copiar' }}</span>
                        </button>
                      </div>
                      <pre class="text-[11px] font-mono p-2 rounded bg-[#090a0b] text-emerald-400 border border-[#23252a] max-h-36 overflow-y-auto leading-relaxed">{{ JSON.stringify((nodeState as any).output, null, 2) }}</pre>
                    </div>

                    <div v-else-if="(nodeState as any).error" class="space-y-1">
                      <span class="text-[10px] font-mono text-rose-400 uppercase">Error:</span>
                      <pre class="text-[11px] font-mono p-2 rounded bg-rose-500/10 text-rose-300 border border-rose-500/30 max-h-36 overflow-y-auto leading-relaxed">{{ (nodeState as any).error }}</pre>
                    </div>

                    <div v-else class="text-[11px] text-[#62666d] italic py-1">
                      Sem saída registrada
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
