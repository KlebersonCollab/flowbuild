<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import {
  X,
  Plus,
  Save,
  Trash2,
  ExternalLink,
  Power,
  Copy,
  Check,
  Webhook,
  Sparkles,
  Folder,
  FolderOpen,
  FolderPlus,
  ChevronRight,
  ChevronDown,
  Search,
  ArrowRight,
  Loader2,
  FileText,
  Pencil,
  Terminal,
} from 'lucide-vue-next'
import { useFlowStore } from '../stores/flowStore'
import { getWebhookInfo, getWebhookAuthBadge, getWebhookCurlCommand } from '../utils/webhook'
import {
  buildFolderTree,
  matchFlowFolder,
  flattenVisibleTree,
  sanitizeFolderPath,
  type FlatTreeItem,
} from '../utils/folderTree'

const props = defineProps<{
  isOpen: boolean
}>()

const emit = defineEmits<{
  (e: 'close'): void
}>()

const flowStore = useFlowStore()
const copiedWebhookId = ref<string | null>(null)
const copiedCurlId = ref<string | null>(null)
const isSaving = ref(false)
const selectedFolder = ref<string>('all')
const expandedFolders = ref<Set<string>>(new Set())
const folderSearchQuery = ref('')
const isCreatingFolder = ref(false)
const newFolderName = ref('')
const promotingFlowId = ref<string | null>(null)
const editingDescFlowId = ref<string | null>(null)
const tempDescription = ref('')
const notificationMessage = ref<{
  type: 'success' | 'error'
  text: string
  targetEnv?: 'qa' | 'prd'
} | null>(null)

const devCount = computed(() =>
  flowStore.savedFlows.filter((f: any) => (f.environment || 'dev') === 'dev').length
)
const qaCount = computed(() =>
  flowStore.savedFlows.filter((f: any) => f.environment === 'qa').length
)
const prdCount = computed(() =>
  flowStore.savedFlows.filter((f: any) => f.environment === 'prd').length
)

const folderTree = computed(() => {
  const envFlows = flowStore.savedFlows.filter(
    (f: any) => (f.environment || 'dev') === flowStore.currentEnvironment
  )
  return buildFolderTree(envFlows)
})

const visibleTreeItems = computed<FlatTreeItem[]>(() => {
  return flattenVisibleTree(
    folderTree.value,
    expandedFolders.value,
    folderSearchQuery.value
  )
})

const filteredFlows = computed(() => {
  return flowStore.savedFlows.filter((f: any) => {
    const matchesEnv = (f.environment || 'dev') === flowStore.currentEnvironment
    const matchesFolder = matchFlowFolder(f.folder, selectedFolder.value)
    return matchesEnv && matchesFolder
  })
})

function toggleFolderExpand(path: string, event?: Event) {
  if (event) event.stopPropagation()
  const next = new Set(expandedFolders.value)
  if (next.has(path)) {
    next.delete(path)
  } else {
    next.add(path)
  }
  expandedFolders.value = next
}

function selectFolder(path: string) {
  selectedFolder.value = path
  if (path !== 'all') {
    const next = new Set(expandedFolders.value)
    next.add(path)
    expandedFolders.value = next
  }
}

function handleCreateFolder() {
  const trimmed = newFolderName.value.trim()
  if (!trimmed) return
  const sanitized = sanitizeFolderPath(trimmed)
  selectFolder(sanitized)
  flowStore.currentFolder = sanitized
  newFolderName.value = ''
  isCreatingFolder.value = false
}

function autoExpandRoots() {
  const next = new Set(expandedFolders.value)
  folderTree.value.forEach(node => {
    if (node.children.length > 0) {
      next.add(node.fullPath)
    }
  })
  expandedFolders.value = next
}

onMounted(async () => {
  await flowStore.fetchSavedFlows()
  autoExpandRoots()
})

watch(
  () => flowStore.currentEnvironment,
  () => {
    autoExpandRoots()
  }
)


function copyWebhookUrl(flowId: string, path: string) {
  const fullUrl = `http://localhost:8000/api/v1/webhooks/${path}`
  navigator.clipboard.writeText(fullUrl)
  copiedWebhookId.value = flowId
  setTimeout(() => {
    copiedWebhookId.value = null
  }, 2000)
}

function copyWebhookCurl(flowId: string, info: any) {
  const fullUrl = `http://localhost:8000/api/v1/webhooks/${info.path}`
  const curl = getWebhookCurlCommand(fullUrl, info)
  navigator.clipboard.writeText(curl)
  copiedCurlId.value = flowId
  setTimeout(() => {
    copiedCurlId.value = null
  }, 2000)
}

async function onSaveCurrentFlow() {
  isSaving.value = true
  await flowStore.publishOrSaveFlow()
  isSaving.value = false
  notificationMessage.value = {
    type: 'success',
    text: `Fluxo "${flowStore.flowName}" salvo com sucesso com versão ${flowStore.version} (${flowStore.currentEnvironment.toUpperCase()})!`,
  }
}

async function onPromoteFlow(flow: any, targetEnv: 'qa' | 'prd') {
  promotingFlowId.value = flow.id
  const nextVersion =
    targetEnv === 'qa'
      ? 'v1.1.0'
      : 'v2.0.0'
  const ok = await flowStore.promoteFlow(flow.id, targetEnv, nextVersion)
  promotingFlowId.value = null
  if (ok) {
    await flowStore.fetchSavedFlows()
    notificationMessage.value = {
      type: 'success',
      text: `Fluxo "${flow.name}" promovido com sucesso para ${targetEnv.toUpperCase()} (${nextVersion})!`,
      targetEnv,
    }
  } else {
    notificationMessage.value = {
      type: 'error',
      text: `Falha ao promover fluxo "${flow.name}" para ${targetEnv.toUpperCase()}.`,
    }
  }
}

async function onToggleActive(flow: any) {
  const updatedActive = !flow.is_active
  await fetch(`http://localhost:8000/api/v1/flows/${flow.id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ flow: flow.flow_data, is_active: updatedActive }),
  })
  await flowStore.fetchSavedFlows()
}

function onLoadFlow(flow: any) {
  flowStore.loadFlow(flow.flow_data)
  flowStore.isActive = flow.is_active
  emit('close')
}

async function onDeleteFlow(flowId: string) {
  if (confirm('Tem certeza que deseja excluir permanentemente este fluxo?')) {
    await flowStore.deleteSavedFlow(flowId)
  }
}

function startEditDescription(flow: any) {
  editingDescFlowId.value = flow.id
  tempDescription.value = flow.description || ''
}

async function saveFlowDescription(flow: any) {
  if (!editingDescFlowId.value) return
  const newDesc = tempDescription.value.trim()
  const updatedData = { ...flow.flow_data, description: newDesc }
  await fetch(`http://localhost:8000/api/v1/flows/${flow.id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ flow: updatedData, description: newDesc }),
  })
  flow.description = newDesc
  flow.flow_data.description = newDesc
  if (flowStore.flowId === flow.id) {
    flowStore.flowDescription = newDesc
  }
  editingDescFlowId.value = null
  await flowStore.fetchSavedFlows()
}

function onCreateNewFlow() {
  flowStore.nodes = []
  flowStore.edges = []
  flowStore.flowId = `flow-${Date.now()}`
  flowStore.flowName = 'Novo Fluxo de Automação'
  flowStore.flowDescription = ''
  flowStore.isActive = true
  emit('close')
}
</script>

<template>
  <div
    v-if="isOpen"
    class="fixed inset-0 z-50 flex items-center justify-center bg-black/75 backdrop-blur-sm select-none"
    @click.self="emit('close')"
  >
    <div class="w-full max-w-5xl rounded-xl bg-[#0f1011] border border-[#23252a] text-[#f7f8f8] shadow-2xl flex flex-col h-[88vh] overflow-hidden">
      <!-- Modal Header -->
      <div class="flex items-center justify-between border-b border-[#23252a] px-5 py-3 bg-[#141516]">
        <div class="flex items-center space-x-2.5">
          <Sparkles class="h-4 w-4 text-[#5e6ad2]" />
          <h2 class="text-sm font-semibold tracking-tight text-white">Gerenciador de Fluxos</h2>
        </div>

        <!-- Environment Selector Tabs -->
        <div class="flex items-center space-x-1 bg-[#090a0b] p-1 rounded-lg border border-[#23252a]">
          <button
            @click="flowStore.setEnvironment('dev')"
            class="px-2.5 py-1 rounded text-xs font-semibold uppercase transition-all flex items-center space-x-1.5"
            :class="flowStore.currentEnvironment === 'dev' ? 'bg-emerald-500/20 text-emerald-400 border border-emerald-500/40 shadow-sm' : 'text-[#8a8f98] hover:text-white border border-transparent'"
          >
            <span>DEV</span>
            <span class="text-[10px] px-1.5 py-0.2 rounded-full bg-emerald-500/20 text-emerald-300 font-mono">{{ devCount }}</span>
          </button>
          <button
            @click="flowStore.setEnvironment('qa')"
            class="px-2.5 py-1 rounded text-xs font-semibold uppercase transition-all flex items-center space-x-1.5"
            :class="flowStore.currentEnvironment === 'qa' ? 'bg-amber-500/20 text-amber-400 border border-amber-500/40 shadow-sm' : 'text-[#8a8f98] hover:text-white border border-transparent'"
          >
            <span>QA</span>
            <span class="text-[10px] px-1.5 py-0.2 rounded-full bg-amber-500/20 text-amber-300 font-mono">{{ qaCount }}</span>
          </button>
          <button
            @click="flowStore.setEnvironment('prd')"
            class="px-2.5 py-1 rounded text-xs font-semibold uppercase transition-all flex items-center space-x-1.5"
            :class="flowStore.currentEnvironment === 'prd' ? 'bg-[#5e6ad2]/25 text-[#828fff] border border-[#5e6ad2]/50 shadow-sm' : 'text-[#8a8f98] hover:text-white border border-transparent'"
          >
            <span>PRD</span>
            <span class="text-[10px] px-1.5 py-0.2 rounded-full bg-[#5e6ad2]/20 text-[#828fff] font-mono">{{ prdCount }}</span>
          </button>
        </div>

        <button
          @click="emit('close')"
          class="h-7 w-7 rounded flex items-center justify-center text-[#8a8f98] hover:text-white hover:bg-[#23252a] transition-colors"
        >
          <X class="h-4 w-4" />
        </button>
      </div>

      <!-- Promotion & Save Notification Banner -->
      <div
        v-if="notificationMessage"
        class="px-4 py-2.5 flex items-center justify-between border-b text-xs transition-all"
        :class="notificationMessage.type === 'success' ? 'bg-emerald-950/40 border-emerald-500/30 text-emerald-300' : 'bg-rose-950/40 border-rose-500/30 text-rose-300'"
      >
        <div class="flex items-center space-x-2 truncate">
          <span class="font-bold">{{ notificationMessage.type === 'success' ? '✓' : '⚠️' }}</span>
          <span class="truncate">{{ notificationMessage.text }}</span>
        </div>
        <div class="flex items-center space-x-2 shrink-0">
          <button
            v-if="notificationMessage.targetEnv"
            @click="flowStore.setEnvironment(notificationMessage.targetEnv!); notificationMessage = null"
            class="px-2.5 py-1 rounded bg-[#141516] hover:bg-[#23252a] text-white border border-[#3e3e44] font-medium flex items-center space-x-1 transition-colors"
          >
            <span>Ver em {{ notificationMessage.targetEnv.toUpperCase() }}</span>
            <ArrowRight class="h-3 w-3" />
          </button>
          <button
            @click="notificationMessage = null"
            class="p-1 hover:text-white text-[#8a8f98] transition-colors"
            title="Fechar aviso"
          >
            <X class="h-3.5 w-3.5" />
          </button>
        </div>
      </div>

      <!-- Action Toolbar -->
      <div class="p-3.5 border-b border-[#23252a] flex flex-wrap items-center justify-between gap-3 bg-[#0a0a0c]">
        <div class="flex items-center space-x-2">
          <button
            @click="onCreateNewFlow"
            class="text-xs px-3 py-1.5 rounded-md bg-[#23252a] hover:bg-[#34343a] text-white flex items-center space-x-1.5 transition-colors"
          >
            <Plus class="h-3.5 w-3.5 text-[#5e6ad2]" />
            <span>Criar Novo Fluxo</span>
          </button>

          <!-- Folder assignment for active flow -->
          <div class="flex items-center space-x-1.5 bg-[#141516] border border-[#23252a] rounded-md px-2 py-1 text-xs">
            <Folder class="h-3 w-3 text-[#8a8f98]" />
            <input
              v-model="flowStore.currentFolder"
              type="text"
              class="bg-transparent text-xs text-white placeholder-[#62666d] outline-none w-28"
              placeholder="Pasta (ex: Financeiro)"
              title="Pasta do fluxo atual"
            />
          </div>

          <!-- Description for active flow -->
          <div class="flex items-center space-x-1.5 bg-[#141516] border border-[#23252a] rounded-md px-2 py-1 text-xs">
            <FileText class="h-3 w-3 text-[#8a8f98]" />
            <input
              v-model="flowStore.flowDescription"
              type="text"
              class="bg-transparent text-xs text-white placeholder-[#62666d] outline-none w-44 md:w-56"
              placeholder="Descrição do fluxo atual..."
              title="Descrição do fluxo atual"
            />
          </div>
        </div>

        <div class="flex items-center space-x-2">
          <button
            @click="onSaveCurrentFlow"
            :disabled="isSaving"
            class="text-xs px-3.5 py-1.5 rounded-md bg-[#5e6ad2] hover:bg-[#828fff] text-white flex items-center space-x-1.5 shadow transition-colors font-medium"
          >
            <Save class="h-3.5 w-3.5" />
            <span>{{ isSaving ? 'Salvando...' : 'Salvar Fluxo Atual' }}</span>
          </button>
        </div>
      </div>

      <!-- Main Split Body (Worktree Sidebar + Flows Content) -->
      <div class="flex-1 flex flex-col md:flex-row min-h-0 overflow-hidden">
        <!-- Left Pane: Worktree Sidebar -->
        <aside class="w-full md:w-64 border-b md:border-b-0 md:border-r border-[#23252a] bg-[#0b0c0e] flex flex-col shrink-0">
          <!-- Worktree Header & Search -->
          <div class="p-2.5 border-b border-[#23252a] space-y-2">
            <div class="flex items-center justify-between">
              <span class="text-[11px] font-bold uppercase tracking-wider text-[#8a8f98] flex items-center space-x-1.5">
                <Folder class="h-3.5 w-3.5 text-[#5e6ad2]" />
                <span>Worktree de Pastas</span>
              </span>
              <button
                @click="isCreatingFolder = !isCreatingFolder"
                class="p-1 rounded hover:bg-[#1a1b1e] text-[#8a8f98] hover:text-white transition-colors"
                title="Criar nova pasta"
              >
                <FolderPlus class="h-3.5 w-3.5 text-[#828fff]" />
              </button>
            </div>

            <!-- Quick folder search -->
            <div class="flex items-center space-x-1.5 bg-[#141516] border border-[#23252a] rounded px-2 py-1 text-xs">
              <Search class="h-3 w-3 text-[#62666d] shrink-0" />
              <input
                v-model="folderSearchQuery"
                type="text"
                placeholder="Filtrar pastas..."
                class="bg-transparent text-xs text-white placeholder-[#62666d] outline-none w-full"
              />
              <button
                v-if="folderSearchQuery"
                @click="folderSearchQuery = ''"
                class="text-[#62666d] hover:text-white text-xs"
              >
                ×
              </button>
            </div>

            <!-- Inline Create Folder -->
            <div v-if="isCreatingFolder" class="pt-1 flex items-center space-x-1.5">
              <input
                v-model="newFolderName"
                type="text"
                placeholder="Ex: Financeiro/PIX"
                class="bg-[#141516] border border-[#5e6ad2] rounded px-2 py-1 text-xs text-white placeholder-[#62666d] outline-none flex-1 font-mono text-[11px]"
                @keyup.enter="handleCreateFolder"
                @keyup.esc="isCreatingFolder = false"
                autoFocus
              />
              <button
                @click="handleCreateFolder"
                class="p-1 rounded bg-[#5e6ad2] hover:bg-[#828fff] text-white transition-colors text-xs font-semibold"
                title="Criar e Selecionar"
              >
                <Check class="h-3 w-3" />
              </button>
            </div>
          </div>

          <!-- Tree View Scrollable Navigation -->
          <div class="flex-1 overflow-y-auto p-2 space-y-0.5 text-xs font-sans">
            <!-- "Todos os Fluxos" root node -->
            <button
              @click="selectedFolder = 'all'"
              class="w-full flex items-center justify-between px-2.5 py-1.5 rounded text-left transition-all group"
              :class="selectedFolder === 'all'
                ? 'bg-[#5e6ad2]/20 text-[#828fff] border border-[#5e6ad2]/40 font-medium'
                : 'text-[#8a8f98] hover:text-white hover:bg-[#141516] border border-transparent'"
            >
              <div class="flex items-center space-x-2 truncate">
                <FolderOpen v-if="selectedFolder === 'all'" class="h-3.5 w-3.5 text-[#828fff] shrink-0" />
                <Folder v-else class="h-3.5 w-3.5 text-[#62666d] group-hover:text-[#8a8f98] shrink-0" />
                <span class="truncate">Todos os Fluxos</span>
              </div>
              <span
                class="text-[10px] px-1.5 py-0.2 rounded-full font-mono"
                :class="selectedFolder === 'all' ? 'bg-[#5e6ad2]/30 text-[#828fff]' : 'bg-[#18191a] text-[#62666d]'"
              >
                {{ flowStore.flowsInCurrentEnvironment.length }}
              </span>
            </button>

            <!-- Flat Visible Items of the Folder Tree -->
            <div
              v-for="item in visibleTreeItems"
              :key="item.id"
              class="flex items-center rounded text-left transition-all group select-none cursor-pointer"
              :class="selectedFolder === item.fullPath
                ? 'bg-[#5e6ad2]/20 text-[#828fff] border border-[#5e6ad2]/40 font-medium'
                : 'text-[#8a8f98] hover:text-white hover:bg-[#141516] border border-transparent'"
              :style="{ paddingLeft: `${item.depth * 14 + 6}px` }"
              @click="selectFolder(item.fullPath)"
            >
              <!-- Expand/Collapse Chevron -->
              <button
                v-if="item.hasChildren"
                @click.stop="toggleFolderExpand(item.fullPath, $event)"
                class="p-1 hover:text-white text-[#62666d] transition-colors shrink-0"
                :title="item.isExpanded ? 'Recolher' : 'Expandir'"
              >
                <ChevronDown v-if="item.isExpanded" class="h-3 w-3" />
                <ChevronRight v-else class="h-3 w-3" />
              </button>
              <span v-else class="w-5 shrink-0" />

              <!-- Folder Icon -->
              <FolderOpen
                v-if="selectedFolder === item.fullPath || item.isExpanded"
                class="h-3.5 w-3.5 mr-1.5 text-[#828fff] shrink-0"
              />
              <Folder
                v-else
                class="h-3.5 w-3.5 mr-1.5 text-[#62666d] group-hover:text-[#8a8f98] shrink-0"
              />

              <!-- Folder Name -->
              <span class="truncate flex-1 py-1.5 text-xs">{{ item.name }}</span>

              <!-- Count Badge -->
              <span
                class="text-[10px] px-1.5 py-0.2 rounded-full font-mono mr-2 shrink-0"
                :class="selectedFolder === item.fullPath ? 'bg-[#5e6ad2]/30 text-[#828fff]' : 'bg-[#18191a] text-[#62666d]'"
              >
                {{ item.flowCount }}
              </span>
            </div>

            <!-- Empty state when no folders match search -->
            <div
              v-if="folderSearchQuery && visibleTreeItems.length === 0"
              class="py-4 text-center text-[11px] text-[#62666d]"
            >
              Nenhuma pasta encontrada
            </div>
          </div>
        </aside>

        <!-- Right Pane: Flows List & Details -->
        <main class="flex-1 flex flex-col min-h-0 bg-[#0f1011]">
          <!-- Breadcrumb Bar -->
          <div class="px-4 py-2 border-b border-[#23252a] bg-[#0d0e0f] flex items-center justify-between text-xs">
            <div class="flex items-center space-x-1.5 text-[#8a8f98] truncate">
              <span class="text-[11px] uppercase font-semibold text-[#62666d]">Pasta:</span>
              <span v-if="selectedFolder === 'all'" class="font-medium text-white">Todos os Fluxos</span>
              <template v-else>
                <span
                  v-for="(seg, idx) in selectedFolder.split('/')"
                  :key="idx"
                  class="flex items-center space-x-1.5"
                >
                  <span v-if="idx > 0" class="text-[#3e3e44]">/</span>
                  <span :class="idx === selectedFolder.split('/').length - 1 ? 'font-medium text-[#828fff]' : 'text-[#8a8f98]'">
                    {{ seg }}
                  </span>
                </span>
              </template>
            </div>

            <span class="text-[11px] text-[#62666d] font-mono shrink-0">
              {{ filteredFlows.length }} {{ filteredFlows.length === 1 ? 'fluxo' : 'fluxos' }}
            </span>
          </div>

          <!-- Flows List -->
          <div class="flex-1 overflow-y-auto p-4 space-y-3">
        <div
          v-if="filteredFlows.length === 0"
          class="py-12 text-center text-xs text-[#62666d] space-y-2"
        >
          <p>Nenhum fluxo encontrado no ambiente <strong class="uppercase text-[#8a8f98]">{{ flowStore.currentEnvironment }}</strong> na pasta selecionada.</p>
          <p class="text-[11px] text-[#3e3e44]">Alterne de ambiente na barra superior ou clique em "Salvar Fluxo Atual".</p>
        </div>

        <div
          v-for="flow in filteredFlows"
          :key="flow.id"
          class="rounded-lg border border-[#23252a] bg-[#141516] p-3.5 flex flex-col space-y-2.5 hover:border-[#3e3e44] transition-all"
        >
          <div class="flex items-start justify-between gap-3">
            <div class="min-w-0 flex-1">
              <div class="flex flex-wrap items-center gap-1.5">
                <span class="text-xs font-semibold text-white truncate">{{ flow.name }}</span>

                <!-- Environment Badge -->
                <span
                  class="text-[10px] font-bold px-2 py-0.5 rounded-full border uppercase"
                  :class="{
                    'bg-emerald-500/15 text-emerald-400 border-emerald-500/30': (flow.environment || 'dev') === 'dev',
                    'bg-amber-500/15 text-amber-400 border-amber-500/30': flow.environment === 'qa',
                    'bg-[#5e6ad2]/20 text-[#828fff] border-[#5e6ad2]/40': flow.environment === 'prd',
                  }"
                >
                  {{ flow.environment || 'dev' }}
                </span>

                <!-- Version Badge -->
                <span class="text-[10px] px-1.5 py-0.5 rounded bg-[#0f1011] text-[#8a8f98] font-mono border border-[#23252a]">
                  {{ flow.version || 'v1.0.0' }}
                </span>

                <!-- Folder Badge -->
                <span class="text-[10px] px-2 py-0.5 rounded-full bg-[#18191a] text-[#8a8f98] border border-[#23252a]">
                  📁 {{ flow.folder || 'Geral' }}
                </span>

                <!-- Draft Badge -->
                <span
                  v-if="flow.is_draft"
                  class="text-[10px] font-bold px-2 py-0.5 rounded-full bg-amber-500/15 text-amber-400 border border-amber-500/30"
                  title="Fluxo possui alterações em rascunho ainda não salvas"
                >
                  🟡 RASCUNHO
                </span>

                <!-- Active / Inactive Badge & Switch -->
                <button
                  @click="!flow.is_draft && onToggleActive(flow)"
                  :disabled="flow.is_draft"
                  class="flex items-center space-x-1 text-[10px] font-bold px-2 py-0.5 rounded-full border transition-all"
                  :class="[
                    flow.is_draft ? 'bg-[#18191a] text-[#62666d] border-[#23252a] opacity-60 cursor-not-allowed' :
                    flow.is_active ? 'bg-[#27a644]/15 text-[#27a644] border-[#27a644]/30' : 'bg-[#23252a] text-[#8a8f98] border-[#3e3e44]'
                  ]"
                  :title="flow.is_draft ? 'Salve o fluxo antes de ativar para execução' : 'Clique para ativar/desativar agendamentos e webhooks deste fluxo'"
                >
                  <Power class="h-2.5 w-2.5" />
                  <span>{{ flow.is_draft ? 'DESATIVADO' : (flow.is_active ? 'ATIVO' : 'DESATIVADO') }}</span>
                </button>
              </div>

              <!-- Inline Editable Description -->
              <div class="pt-1 flex items-center space-x-1.5 group">
                <template v-if="editingDescFlowId === flow.id">
                  <input
                    v-model="tempDescription"
                    type="text"
                    class="text-[11px] bg-[#090a0b] text-white border border-[#5e6ad2] rounded px-2 py-0.5 outline-none flex-1 font-sans"
                    placeholder="Digite a descrição deste fluxo..."
                    @keyup.enter="saveFlowDescription(flow)"
                    @keyup.esc="editingDescFlowId = null"
                    autoFocus
                  />
                  <button
                    @click="saveFlowDescription(flow)"
                    class="p-1 rounded bg-[#27a644]/20 hover:bg-[#27a644]/30 text-[#27a644] transition-colors"
                    title="Salvar descrição"
                  >
                    <Check class="h-3 w-3" />
                  </button>
                  <button
                    @click="editingDescFlowId = null"
                    class="p-1 rounded bg-[#23252a] hover:bg-[#34343a] text-[#8a8f98] transition-colors"
                    title="Cancelar"
                  >
                    <X class="h-3 w-3" />
                  </button>
                </template>
                <template v-else>
                  <p
                    @click="startEditDescription(flow)"
                    class="text-[11px] cursor-pointer truncate transition-colors flex items-center space-x-1.5"
                    :class="flow.description ? 'text-[#8a8f98] hover:text-[#d0d6e0]' : 'italic text-[#62666d] hover:text-[#8a8f98]'"
                    title="Clique para editar a descrição deste fluxo"
                  >
                    <span>{{ flow.description || 'Sem descrição informada (clique para adicionar)...' }}</span>
                    <Pencil class="h-2.5 w-2.5 opacity-0 group-hover:opacity-100 text-[#5e6ad2] transition-opacity shrink-0" />
                  </p>
                </template>
              </div>
            </div>

            <!-- Promotion and Open/Delete Actions -->
            <div class="flex items-center space-x-1.5 shrink-0">
              <!-- Promote Button -->
              <button
                v-if="(flow.environment || 'dev') === 'dev'"
                @click="onPromoteFlow(flow, 'qa')"
                :disabled="promotingFlowId === flow.id || flow.is_draft"
                class="h-7 px-2.5 rounded text-xs bg-amber-500/15 hover:bg-amber-500/25 text-amber-400 border border-amber-500/30 flex items-center space-x-1.5 transition-colors font-medium disabled:opacity-40 disabled:cursor-not-allowed"
                :title="flow.is_draft ? 'Salve o fluxo antes de promover para QA' : 'Promover fluxo de Desenvolvimento para Homologação (QA)'"
              >
                <Loader2 v-if="promotingFlowId === flow.id" class="h-3 w-3 animate-spin text-amber-400" />
                <ArrowRight v-else class="h-3 w-3" />
                <span>{{ promotingFlowId === flow.id ? 'Promovendo...' : (flow.is_draft ? 'Salve p/ Promover' : 'Promover p/ QA') }}</span>
              </button>

              <button
                v-else-if="flow.environment === 'qa'"
                @click="onPromoteFlow(flow, 'prd')"
                :disabled="promotingFlowId === flow.id || flow.is_draft"
                class="h-7 px-2.5 rounded text-xs bg-[#5e6ad2]/20 hover:bg-[#5e6ad2]/30 text-[#828fff] border border-[#5e6ad2]/40 flex items-center space-x-1.5 transition-colors font-medium disabled:opacity-40 disabled:cursor-not-allowed"
                :title="flow.is_draft ? 'Salve o fluxo antes de promover para PRD' : 'Promover fluxo de Homologação (QA) para Produção (PRD)'"
              >
                <Loader2 v-if="promotingFlowId === flow.id" class="h-3 w-3 animate-spin text-[#828fff]" />
                <ArrowRight v-else class="h-3 w-3" />
                <span>{{ promotingFlowId === flow.id ? 'Promovendo...' : (flow.is_draft ? 'Salve p/ Promover' : 'Promover p/ PRD') }}</span>
              </button>

              <span
                v-else-if="flow.environment === 'prd'"
                class="h-7 px-2.5 rounded text-[11px] bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 flex items-center space-x-1 font-medium"
              >
                <span>🟢 Produção</span>
              </span>

              <button
                @click="onLoadFlow(flow)"
                class="h-7 px-2.5 rounded text-xs text-[#828fff] hover:bg-[#5e6ad2]/15 border border-[#5e6ad2]/30 flex items-center space-x-1 transition-colors"
                title="Abrir no Canvas"
              >
                <ExternalLink class="h-3 w-3" />
                <span>Abrir</span>
              </button>

              <button
                @click="onDeleteFlow(flow.id)"
                class="h-7 w-7 rounded text-[#8a8f98] hover:text-rose-400 hover:bg-rose-500/10 flex items-center justify-center transition-colors"
                title="Excluir Fluxo"
              >
                <Trash2 class="h-3.5 w-3.5" />
              </button>
            </div>
          </div>

          <!-- Webhook endpoint banner if present -->
          <div
            v-if="getWebhookInfo(flow.flow_data)"
            class="flex flex-col sm:flex-row sm:items-center justify-between p-2.5 rounded bg-[#090a0b] border border-[#23252a] text-[11px] font-mono text-[#8a8f98] gap-2"
          >
            <div class="flex flex-wrap items-center gap-1.5 min-w-0">
              <Webhook class="h-3.5 w-3.5 text-cyan-400 shrink-0" />
              <span class="text-[10px] font-bold px-1.5 py-0.5 rounded bg-cyan-500/10 text-cyan-400 border border-cyan-500/25 shrink-0">
                {{ getWebhookInfo(flow.flow_data)?.method }}
              </span>
              <span
                class="text-[10px] font-semibold px-1.5 py-0.5 rounded border shrink-0 flex items-center space-x-1"
                :class="getWebhookAuthBadge(getWebhookInfo(flow.flow_data)!).class"
                :title="getWebhookInfo(flow.flow_data)?.authType === 'none' ? 'Webhook público sem restrição' : 'Requer autenticação configurada'"
              >
                <span>{{ getWebhookInfo(flow.flow_data)?.authType === 'none' ? '🔓' : '🔒' }}</span>
                <span>{{ getWebhookAuthBadge(getWebhookInfo(flow.flow_data)!).label }}</span>
              </span>
              <span class="text-white truncate">/api/v1/webhooks/{{ getWebhookInfo(flow.flow_data)?.path }}</span>
            </div>
            <div class="flex items-center space-x-1.5 shrink-0 self-end sm:self-auto">
              <button
                @click="copyWebhookUrl(flow.id, getWebhookInfo(flow.flow_data)!.path)"
                class="px-2 py-0.5 rounded bg-[#18191a] hover:bg-[#23252a] text-xs text-white flex items-center space-x-1 shrink-0 transition-colors border border-[#2e3035]"
                title="Copiar URL completa do webhook"
              >
                <Check v-if="copiedWebhookId === flow.id" class="h-3 w-3 text-[#27a644]" />
                <Copy v-else class="h-3 w-3" />
                <span>{{ copiedWebhookId === flow.id ? 'Copiado!' : 'Copiar URL' }}</span>
              </button>
              <button
                @click="copyWebhookCurl(flow.id, getWebhookInfo(flow.flow_data)!)"
                class="px-2 py-0.5 rounded bg-[#18191a] hover:bg-[#23252a] text-xs text-white flex items-center space-x-1 shrink-0 transition-colors border border-[#2e3035]"
                title="Copiar comando cURL com autenticação e headers configurados"
              >
                <Check v-if="copiedCurlId === flow.id" class="h-3 w-3 text-[#27a644]" />
                <Terminal v-else class="h-3 w-3 text-amber-400" />
                <span>{{ copiedCurlId === flow.id ? 'cURL Copiado!' : 'Copiar cURL' }}</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</div>
</div>
</template>
