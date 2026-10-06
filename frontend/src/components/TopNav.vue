<script setup lang="ts">
import { ref } from 'vue'
import {
  Play,
  RotateCcw,
  Download,
  Upload,
  Layers,
  ChevronDown,
  Terminal,
  Sparkles,
  FolderGit2,
  Key,
  Save,
} from 'lucide-vue-next'
import { useFlowStore } from '../stores/flowStore'
import { useExecutionStore } from '../stores/executionStore'
import { useVariablesStore } from '../stores/variablesStore'
import FlowsModal from './FlowsModal.vue'
import VariablesModal from './VariablesModal.vue'

const flowStore = useFlowStore()
const executionStore = useExecutionStore()
const varStore = useVariablesStore()

const showTemplatesDropdown = ref(false)
const isFlowsModalOpen = ref(false)
const isSaving = ref(false)
const fileInputRef = ref<HTMLInputElement | null>(null)

async function onSaveFlow() {
  isSaving.value = true
  await flowStore.publishOrSaveFlow()
  isSaving.value = false
}

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

function onTriggerImport() {
  fileInputRef.value?.click()
}

function onFileSelected(event: Event) {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (!file) return

  const reader = new FileReader()
  reader.onload = (e) => {
    try {
      const content = e.target?.result as string
      const parsed = JSON.parse(content)
      flowStore.loadFlow(parsed)
    } catch {
      alert('Arquivo JSON inválido. Verifique o formato do fluxo.')
    }
  }
  reader.readAsText(file)
  target.value = ''
}

function onSelectTemplate(type: 'http_enrich' | 'webhook_flow' | 'python_pipeline') {
  flowStore.loadTemplate(type)
  showTemplatesDropdown.value = false
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
    <!-- Brand & Flow Title -->
    <div class="flex items-center space-x-3.5">
      <div class="h-8 w-8 rounded-lg bg-gradient-to-br from-[#5e6ad2] to-[#3b47aa] flex items-center justify-center font-bold text-white shadow-md shadow-[#5e6ad2]/25 border border-[#828fff]/30">
        <Sparkles class="h-4 w-4" />
      </div>

      <div class="flex items-center space-x-2">
        <input
          v-model="flowStore.flowName"
          type="text"
          class="text-sm font-semibold text-[#f7f8f8] bg-transparent border border-transparent hover:border-[#23252a] focus:border-[#5e6ad2] rounded px-2 py-0.5 outline-none transition-colors max-w-[200px] md:max-w-[260px] truncate"
          title="Clique para renomear o fluxo"
        />

        <!-- Folder & Version Tag -->
        <span class="text-[10px] px-2 py-0.5 rounded-full bg-[#141516] text-[#8a8f98] font-mono border border-[#23252a] flex items-center space-x-1.5">
          <span class="text-[#d0d6e0]">📁 {{ flowStore.currentFolder || 'Geral' }}</span>
          <span class="text-[#3e3e44]">·</span>
          <span class="text-amber-400/90 font-semibold">{{ flowStore.version || 'v1.0.0' }}</span>
        </span>

        <!-- Draft vs Saved Badge -->
        <span
          v-if="flowStore.isDraft"
          class="text-[10px] font-bold px-2 py-0.5 rounded-full bg-amber-500/15 text-amber-400 border border-amber-500/30 flex items-center space-x-1"
          title="Modificações não salvas. Clique em 'Salvar Fluxo' para gerar nova versão e ativar."
        >
          <span class="w-1.5 h-1.5 rounded-full bg-amber-400 animate-pulse"></span>
          <span>RASCUNHO</span>
        </span>
        <span
          v-else
          class="text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-500/15 text-emerald-400 border border-emerald-500/30 flex items-center space-x-1"
          title="Fluxo salvo e sincronizado."
        >
          <span class="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
          <span>SALVO</span>
        </span>
      </div>

      <!-- Environment Switcher (DEV / QA / PRD) -->
      <div class="flex items-center bg-[#0f1011] rounded-lg p-0.5 border border-[#23252a] text-xs">
        <button
          @click="flowStore.setEnvironment('dev')"
          :class="flowStore.currentEnvironment === 'dev' ? 'bg-emerald-500/20 text-emerald-400 font-semibold shadow-sm border border-emerald-500/30' : 'text-[#8a8f98] hover:text-[#d0d6e0] border border-transparent'"
          class="px-2.5 py-1 rounded-md transition-all text-[11px] flex items-center space-x-1"
          title="Ambiente de Desenvolvimento"
        >
          <span class="w-1.5 h-1.5 rounded-full bg-emerald-400"></span>
          <span>DEV</span>
        </button>

        <button
          @click="flowStore.setEnvironment('qa')"
          :class="flowStore.currentEnvironment === 'qa' ? 'bg-amber-500/20 text-amber-400 font-semibold shadow-sm border border-amber-500/30' : 'text-[#8a8f98] hover:text-[#d0d6e0] border border-transparent'"
          class="px-2.5 py-1 rounded-md transition-all text-[11px] flex items-center space-x-1"
          title="Ambiente de Homologação / QA"
        >
          <span class="w-1.5 h-1.5 rounded-full bg-amber-400"></span>
          <span>QA</span>
        </button>

        <button
          @click="flowStore.setEnvironment('prd')"
          :class="flowStore.currentEnvironment === 'prd' ? 'bg-[#5e6ad2]/25 text-[#828fff] font-semibold shadow-sm border border-[#5e6ad2]/40' : 'text-[#8a8f98] hover:text-[#d0d6e0] border border-transparent'"
          class="px-2.5 py-1 rounded-md transition-all text-[11px] flex items-center space-x-1"
          title="Ambiente de Produção (PRD)"
        >
          <span class="w-1.5 h-1.5 rounded-full bg-[#5e6ad2]"></span>
          <span>PRD</span>
        </button>
      </div>
    </div>

    <!-- Hidden file input for flow import -->
    <input
      ref="fileInputRef"
      type="file"
      accept=".json"
      class="hidden"
      @change="onFileSelected"
    />

    <!-- Actions & Toolbar -->
    <div class="flex items-center space-x-2">
      <!-- Templates Dropdown -->
      <div class="relative">
        <button
          @click="showTemplatesDropdown = !showTemplatesDropdown"
          class="text-xs px-3 py-1.5 rounded-md bg-[#0f1011] hover:bg-[#141516] text-[#d0d6e0] hover:text-[#f7f8f8] border border-[#23252a] transition-colors flex items-center space-x-1.5"
        >
          <Layers class="h-3.5 w-3.5 text-[#5e6ad2]" />
          <span>Modelos</span>
          <ChevronDown class="h-3 w-3 text-[#8a8f98]" />
        </button>

        <div
          v-if="showTemplatesDropdown"
          @click.outside="showTemplatesDropdown = false"
          class="absolute left-0 mt-1 w-64 rounded-lg bg-[#0f1011] border border-[#23252a] shadow-2xl py-1 z-50 text-xs"
        >
          <div class="px-3 py-1.5 text-[10px] font-semibold uppercase tracking-wider text-[#62666d] border-b border-[#23252a]">
            Fluxos Pré-Configurados
          </div>
          <button
            @click="onSelectTemplate('http_enrich')"
            class="w-full text-left px-3 py-2 hover:bg-[#141516] text-[#f7f8f8] transition-colors flex flex-col"
          >
            <span class="font-medium text-[#828fff]">HTTP Request & Enriquecimento</span>
            <span class="text-[10px] text-[#8a8f98]">Disparo Manual → API GitHub → Transform JSON</span>
          </button>
          <button
            @click="onSelectTemplate('python_pipeline')"
            class="w-full text-left px-3 py-2 hover:bg-[#141516] text-[#f7f8f8] transition-colors flex flex-col"
          >
            <span class="font-medium text-purple-400">Pipeline Python Script</span>
            <span class="text-[10px] text-[#8a8f98]">Disparo Manual → Execução Script com Retorno</span>
          </button>
          <button
            @click="onSelectTemplate('webhook_flow')"
            class="w-full text-left px-3 py-2 hover:bg-[#141516] text-[#f7f8f8] transition-colors flex flex-col"
          >
            <span class="font-medium text-cyan-400">Recepção Webhook Lead</span>
            <span class="text-[10px] text-[#8a8f98]">Webhook Trigger → Normalização de Payload</span>
          </button>
        </div>
      </div>

      <!-- Manage Flows (CRUD / Activation) -->
      <button
        @click="isFlowsModalOpen = true"
        class="text-xs px-3 py-1.5 rounded-md bg-[#0f1011] hover:bg-[#141516] text-[#d0d6e0] hover:text-[#f7f8f8] border border-[#23252a] transition-colors flex items-center space-x-1.5"
        title="Gerenciar fluxos salvos, ativar e desativar"
      >
        <FolderGit2 class="h-3.5 w-3.5 text-[#5e6ad2]" />
        <span>Meus Fluxos</span>
      </button>

      <!-- Manage Variables (Global & Flow) -->
      <button
        @click="varStore.openModal(flowStore.flowId)"
        class="text-xs px-3 py-1.5 rounded-md bg-[#0f1011] hover:bg-[#141516] text-[#d0d6e0] hover:text-[#f7f8f8] border border-[#23252a] transition-colors flex items-center space-x-1.5"
        title="Gerenciar variáveis globais e de fluxo"
      >
        <Key class="h-3.5 w-3.5 text-amber-400" />
        <span>Variáveis</span>
      </button>

      <!-- Import JSON -->
      <button
        @click="onTriggerImport"
        class="text-xs px-2.5 py-1.5 rounded-md bg-[#0f1011] hover:bg-[#141516] text-[#8a8f98] hover:text-[#f7f8f8] border border-[#23252a] transition-colors flex items-center space-x-1"
        title="Importar fluxo JSON"
      >
        <Upload class="h-3.5 w-3.5" />
        <span class="hidden sm:inline">Importar</span>
      </button>

      <!-- Export JSON -->
      <button
        @click="onExportJson"
        class="text-xs px-2.5 py-1.5 rounded-md bg-[#0f1011] hover:bg-[#141516] text-[#8a8f98] hover:text-[#f7f8f8] border border-[#23252a] transition-colors flex items-center space-x-1"
        title="Exportar fluxo JSON"
      >
        <Download class="h-3.5 w-3.5" />
        <span class="hidden sm:inline">Exportar</span>
      </button>

      <!-- Clear Canvas -->
      <button
        @click="onClearCanvas"
        class="text-xs px-2.5 py-1.5 rounded-md bg-[#0f1011] hover:bg-[#141516] text-[#8a8f98] hover:text-rose-400 border border-[#23252a] transition-colors flex items-center space-x-1"
        title="Limpar Canvas"
      >
        <RotateCcw class="h-3.5 w-3.5" />
        <span class="hidden sm:inline">Limpar</span>
      </button>

      <!-- Console / Drawer Toggle -->
      <button
        @click="executionStore.isDrawerOpen = !executionStore.isDrawerOpen"
        class="text-xs px-3 py-1.5 rounded-md border transition-colors flex items-center space-x-1.5"
        :class="executionStore.isDrawerOpen ? 'bg-[#23252a] text-white border-[#3e3e44]' : 'bg-[#0f1011] text-[#8a8f98] border-[#23252a] hover:text-[#f7f8f8]'"
        title="Abrir/Fechar Terminal de Execução"
      >
        <Terminal class="h-3.5 w-3.5 text-[#5e6ad2]" />
        <span>Console</span>
        <span
          v-if="executionStore.structuredLogs.length"
          class="text-[10px] px-1.5 py-0.2 rounded-full bg-[#5e6ad2]/20 text-[#828fff] font-mono"
        >
          {{ executionStore.structuredLogs.length }}
        </span>
      </button>

      <!-- Save Flow Button -->
      <button
        @click="onSaveFlow"
        :disabled="isSaving"
        class="text-xs font-semibold px-3 py-1.5 rounded-md flex items-center space-x-1.5 transition-all shadow-md"
        :class="flowStore.isDraft ? 'bg-amber-600 hover:bg-amber-500 text-white shadow-amber-600/25 ring-1 ring-amber-400/40' : 'bg-[#18191a] hover:bg-[#23252a] text-[#d0d6e0] border border-[#23252a]'"
        :title="flowStore.isDraft ? 'Salvar rascunho e gerar nova versão (incrementar versão)' : 'Salvar e gerar nova versão'"
      >
        <Save class="h-3.5 w-3.5" />
        <span>{{ isSaving ? 'Salvando...' : (flowStore.isDraft ? 'Salvar Fluxo' : 'Salvar Versão') }}</span>
      </button>

      <!-- Run Flow (Button Primary - Linear Token) -->
      <button
        @click="onRunFlow"
        :disabled="executionStore.isRunning"
        class="text-xs font-semibold px-4 py-1.5 rounded-md bg-[#5e6ad2] hover:bg-[#828fff] active:bg-[#5e69d1] disabled:opacity-50 text-white shadow-lg shadow-[#5e6ad2]/30 transition-all flex items-center space-x-2"
      >
        <span v-if="executionStore.isRunning" class="h-3.5 w-3.5 border-2 border-white/30 border-t-white rounded-full animate-spin"></span>
        <Play v-else class="h-3.5 w-3.5 fill-current" />
        <span>{{ executionStore.isRunning ? 'Executando...' : 'Executar Fluxo' }}</span>
      </button>
    </div>

    <!-- Flows Modal -->
    <FlowsModal :is-open="isFlowsModalOpen" @close="isFlowsModalOpen = false" />

    <!-- Variables Modal -->
    <VariablesModal :is-open="varStore.isModalOpen" @close="varStore.closeModal()" />
  </header>
</template>
