<script setup lang="ts">
import { ref, onMounted } from 'vue'
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
  Sparkles
} from 'lucide-vue-next'
import { useFlowStore } from '../stores/flowStore'

const props = defineProps<{
  isOpen: boolean
}>()

const emit = defineEmits<{
  (e: 'close'): void
}>()

const flowStore = useFlowStore()
const copiedWebhookId = ref<string | null>(null)
const isSaving = ref(false)

onMounted(async () => {
  await flowStore.fetchSavedFlows()
})

function getWebhookPath(flowData: any): string | null {
  const node = flowData?.nodes?.find((n: any) => n.type === 'WebhookTriggerComponent')
  if (!node) return null
  const path = node.data?.inputs?.path || 'webhook/default'
  return path.startsWith('/') ? path.slice(1) : path
}

function copyWebhookUrl(flowId: string, path: string) {
  const fullUrl = `http://localhost:8000/api/v1/webhooks/${path}`
  navigator.clipboard.writeText(fullUrl)
  copiedWebhookId.value = flowId
  setTimeout(() => {
    copiedWebhookId.value = null
  }, 2000)
}

async function onSaveCurrentFlow() {
  isSaving.value = true
  await flowStore.saveFlowToBackend(flowStore.isActive)
  isSaving.value = false
}

async function onToggleActive(flow: any) {
  const updatedActive = !flow.is_active
  await fetch(`http://localhost:8000/api/v1/flows/${flow.id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ flow: flow.flow_data, is_active: updatedActive })
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

function onCreateNewFlow() {
  flowStore.nodes = []
  flowStore.edges = []
  flowStore.flowId = `flow-${Date.now()}`
  flowStore.flowName = 'Novo Fluxo de Automação'
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
    <div class="w-full max-w-3xl rounded-xl bg-[#0f1011] border border-[#23252a] text-[#f7f8f8] shadow-2xl flex flex-col max-h-[85vh] overflow-hidden">
      <!-- Modal Header -->
      <div class="flex items-center justify-between border-b border-[#23252a] px-5 py-3.5 bg-[#141516]">
        <div class="flex items-center space-x-2.5">
          <Sparkles class="h-4 w-4 text-[#5e6ad2]" />
          <h2 class="text-sm font-semibold tracking-tight text-white">Gerenciador de Fluxos de Automação</h2>
        </div>
        <button
          @click="emit('close')"
          class="h-7 w-7 rounded flex items-center justify-center text-[#8a8f98] hover:text-white hover:bg-[#23252a] transition-colors"
        >
          <X class="h-4 w-4" />
        </button>
      </div>

      <!-- Action Toolbar -->
      <div class="p-4 border-b border-[#23252a] flex items-center justify-between bg-[#0a0a0c]">
        <div class="flex items-center space-x-3">
          <button
            @click="onCreateNewFlow"
            class="text-xs px-3 py-1.5 rounded-md bg-[#23252a] hover:bg-[#34343a] text-white flex items-center space-x-1.5 transition-colors"
          >
            <Plus class="h-3.5 w-3.5 text-[#5e6ad2]" />
            <span>Criar Novo Fluxo</span>
          </button>
        </div>

        <button
          @click="onSaveCurrentFlow"
          :disabled="isSaving"
          class="text-xs px-3.5 py-1.5 rounded-md bg-[#5e6ad2] hover:bg-[#828fff] text-white flex items-center space-x-1.5 shadow transition-colors font-medium"
        >
          <Save class="h-3.5 w-3.5" />
          <span>{{ isSaving ? 'Salvando...' : 'Salvar Fluxo Atual' }}</span>
        </button>
      </div>

      <!-- Flows List -->
      <div class="flex-1 overflow-y-auto p-4 space-y-3">
        <div
          v-if="flowStore.savedFlows.length === 0"
          class="py-12 text-center text-xs text-[#62666d] space-y-2"
        >
          <p>Nenhum fluxo salvo no banco de dados.</p>
          <p class="text-[11px] text-[#3e3e44]">Clique em "Salvar Fluxo Atual" para persistir seu canvas com SQLite.</p>
        </div>

        <div
          v-for="flow in flowStore.savedFlows"
          :key="flow.id"
          class="rounded-lg border border-[#23252a] bg-[#141516] p-3.5 flex flex-col space-y-2.5 hover:border-[#3e3e44] transition-all"
        >
          <div class="flex items-start justify-between">
            <div class="min-w-0 flex-1">
              <div class="flex items-center space-x-2">
                <span class="text-xs font-semibold text-white truncate">{{ flow.name }}</span>
                <!-- Active / Inactive Badge & Switch -->
                <button
                  @click="onToggleActive(flow)"
                  class="flex items-center space-x-1 text-[10px] font-bold px-2 py-0.5 rounded-full border transition-all"
                  :class="flow.is_active ? 'bg-[#27a644]/15 text-[#27a644] border-[#27a644]/30' : 'bg-[#23252a] text-[#8a8f98] border-[#3e3e44]'"
                  title="Clique para ativar/desativar agendamentos e webhooks deste fluxo"
                >
                  <Power class="h-2.5 w-2.5" />
                  <span>{{ flow.is_active ? 'ATIVO' : 'DESATIVADO' }}</span>
                </button>
              </div>
              <p class="text-[11px] text-[#8a8f98] truncate pt-0.5">{{ flow.description || 'Sem descrição informada.' }}</p>
            </div>

            <div class="flex items-center space-x-1.5 shrink-0">
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
            v-if="getWebhookPath(flow.flow_data)"
            class="flex items-center justify-between p-2 rounded bg-[#090a0b] border border-[#23252a] text-[11px] font-mono text-[#8a8f98]"
          >
            <div class="flex items-center space-x-1.5 truncate">
              <Webhook class="h-3 w-3 text-cyan-400 shrink-0" />
              <span class="text-white truncate">/api/v1/webhooks/{{ getWebhookPath(flow.flow_data) }}</span>
            </div>
            <button
              @click="copyWebhookUrl(flow.id, getWebhookPath(flow.flow_data)!)"
              class="px-2 py-0.5 rounded bg-[#18191a] hover:bg-[#23252a] text-xs text-white flex items-center space-x-1 shrink-0 transition-colors"
            >
              <Check v-if="copiedWebhookId === flow.id" class="h-3 w-3 text-[#27a644]" />
              <Copy v-else class="h-3 w-3" />
              <span>{{ copiedWebhookId === flow.id ? 'Copiado!' : 'Copiar URL' }}</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
