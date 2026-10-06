<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import {
  X,
  Plus,
  Key,
  Globe,
  GitBranch,
  Trash2,
  Copy,
  Check,
  Eye,
  EyeOff,
  Save,
  Lock,
} from 'lucide-vue-next'
import { useVariablesStore } from '../stores/variablesStore'
import { useFlowStore } from '../stores/flowStore'
import type { VariableItem } from '../types/flow'

const props = defineProps<{
  isOpen: boolean
}>()

const emit = defineEmits<{
  (e: 'close'): void
}>()

const varStore = useVariablesStore()
const flowStore = useFlowStore()

const activeTab = ref<'global' | 'flow'>('global')
const selectedEnvFilter = ref<'dev' | 'qa' | 'prd' | 'all'>('all')
const newKey = ref('')
const newValue = ref('')
const newEnvironment = ref<'dev' | 'qa' | 'prd' | 'all'>('all')
const newIsSecret = ref(false)
const copiedKey = ref<string | null>(null)
const revealedSecrets = ref<Record<string, boolean>>({})
const editingValues = ref<Record<string, string>>({})

watch(
  () => props.isOpen,
  (open) => {
    if (open) {
      varStore.currentFlowId = flowStore.flowId
      varStore.fetchVariables(flowStore.flowId)
    }
  }
)

const activeList = computed(() => {
  const baseList =
    activeTab.value === 'global' ? varStore.globalVariables : varStore.flowVariables
  if (selectedEnvFilter.value === 'all') return baseList
  return baseList.filter(
    (v) =>
      (v.environment || 'all') === selectedEnvFilter.value ||
      (v.environment || 'all') === 'all'
  )
})

function toggleSecretVisibility(id: string) {
  revealedSecrets.value[id] = !revealedSecrets.value[id]
}

function copyToClipboard(key: string) {
  const token = `{{${key}}}`
  navigator.clipboard.writeText(token)
  copiedKey.value = key
  setTimeout(() => {
    copiedKey.value = null
  }, 2000)
}

async function handleCreateVariable() {
  const trimmedKey = newKey.value.trim()
  if (!trimmedKey) return

  const success = await varStore.createVariable({
    key: trimmedKey,
    value: newValue.value,
    scope: activeTab.value,
    flow_id: activeTab.value === 'flow' ? flowStore.flowId : null,
    environment: newEnvironment.value,
    is_secret: newIsSecret.value,
  })

  if (success) {
    newKey.value = ''
    newValue.value = ''
    newEnvironment.value = 'all'
    newIsSecret.value = false
  }
}

async function handleUpdateVariable(variable: VariableItem) {
  const updatedValue = editingValues.value[variable.id]
  if (updatedValue === undefined) return

  await varStore.updateVariable(variable.id, updatedValue, variable.is_secret)
  delete editingValues.value[variable.id]
}

async function handleDeleteVariable(id: string) {
  if (confirm('Tem certeza que deseja excluir esta variável?')) {
    await varStore.deleteVariable(id)
  }
}
</script>

<template>
  <div
    v-if="isOpen"
    class="fixed inset-0 z-50 flex items-center justify-center bg-black/75 backdrop-blur-sm select-none"
    @click.self="emit('close')"
  >
    <div
      class="w-full max-w-3xl rounded-xl bg-[#0f1011] border border-[#23252a] text-[#f7f8f8] shadow-2xl flex flex-col max-h-[85vh] overflow-hidden"
    >
      <!-- Header -->
      <div class="flex items-center justify-between border-b border-[#23252a] px-5 py-3.5 bg-[#141516]">
        <div class="flex items-center space-x-2.5">
          <Key class="h-4 w-4 text-[#5e6ad2]" />
          <div>
            <h2 class="text-sm font-semibold tracking-tight text-white">
              Gerenciador de Variáveis & Ambientes
            </h2>
          </div>
        </div>
        <button
          @click="emit('close')"
          class="p-1 rounded-md text-[#8a8f98] hover:text-white hover:bg-[#23252a] transition-colors"
        >
          <X class="h-4 w-4" />
        </button>
      </div>

      <!-- Scope Tabs & Description -->
      <div class="px-5 pt-3 border-b border-[#23252a] bg-[#141516]/50">
        <p class="text-xs text-[#8a8f98] mb-3">
          Variáveis podem ser chamadas em qualquer nó via
          <code class="text-[#828fff] bg-[#1c1d20] px-1 py-0.5 rounded font-mono">&#123;&#123;NOME&#125;&#125;</code>
          ou conectadas visualmente com o nó
          <span class="text-white font-medium">Variable</span>. Variáveis locais do fluxo sobrescrevem globais. Resolução obedece a hierarquia DEV / QA / PRD.
        </p>

        <div class="flex flex-wrap items-center justify-between gap-2">
          <div class="flex space-x-2">
            <button
              @click="activeTab = 'global'"
              class="pb-2.5 px-3 text-xs font-medium border-b-2 flex items-center space-x-2 transition-colors"
              :class="
                activeTab === 'global'
                  ? 'border-[#5e6ad2] text-white'
                  : 'border-transparent text-[#8a8f98] hover:text-[#f7f8f8]'
              "
            >
              <Globe class="h-3.5 w-3.5" />
              <span>Variáveis Globais</span>
              <span
                class="text-[10px] px-1.5 py-0.2 rounded-full font-mono"
                :class="activeTab === 'global' ? 'bg-[#5e6ad2]/20 text-[#828fff]' : 'bg-[#23252a] text-[#8a8f98]'"
              >
                {{ varStore.globalVariables.length }}
              </span>
            </button>

            <button
              @click="activeTab = 'flow'"
              class="pb-2.5 px-3 text-xs font-medium border-b-2 flex items-center space-x-2 transition-colors"
              :class="
                activeTab === 'flow'
                  ? 'border-[#5e6ad2] text-white'
                  : 'border-transparent text-[#8a8f98] hover:text-[#f7f8f8]'
              "
            >
              <GitBranch class="h-3.5 w-3.5 text-amber-400" />
              <span>Variáveis deste Fluxo</span>
              <span
                class="text-[10px] px-1.5 py-0.2 rounded-full font-mono"
                :class="activeTab === 'flow' ? 'bg-amber-500/20 text-amber-300' : 'bg-[#23252a] text-[#8a8f98]'"
              >
                {{ varStore.flowVariables.length }}
              </span>
            </button>
          </div>

          <!-- Environment Filter -->
          <div class="flex items-center space-x-1 pb-2 text-xs">
            <span class="text-[10px] text-[#62666d] uppercase font-semibold mr-1">Ambiente:</span>
            <button
              v-for="env in (['all', 'dev', 'qa', 'prd'] as const)"
              :key="env"
              @click="selectedEnvFilter = env"
              :class="selectedEnvFilter === env ? 'bg-[#5e6ad2]/20 text-[#828fff] border-[#5e6ad2]/40 font-semibold' : 'bg-[#141516] text-[#8a8f98] hover:text-[#d0d6e0] border-[#23252a]'"
              class="px-2 py-0.5 rounded border text-[10px] uppercase transition-colors"
            >
              {{ env === 'all' ? 'Todos' : env }}
            </button>
          </div>
        </div>
      </div>

      <!-- Content Area -->
      <div class="p-5 overflow-y-auto space-y-4 flex-1">
        <!-- Add New Variable Card -->
        <div class="p-3.5 rounded-lg bg-[#141516] border border-[#23252a] space-y-3">
          <div class="text-xs font-medium text-white flex items-center justify-between">
            <span>Criar Nova Variável ({{ activeTab === 'global' ? 'Global' : 'Escopo do Fluxo' }})</span>
            <span class="text-[11px] text-[#8a8f98] font-mono">
              {{ activeTab === 'global' ? 'Disponível em todos os fluxos' : `Restrita a: ${flowStore.flowName}` }}
            </span>
          </div>

          <div class="grid grid-cols-1 sm:grid-cols-12 gap-2.5 items-end">
            <div class="sm:col-span-3">
              <label class="block text-[10px] font-medium uppercase tracking-wider text-[#8a8f98] mb-1">
                Nome da Variável
              </label>
              <input
                v-model="newKey"
                type="text"
                placeholder="Ex: API_HOST"
                class="w-full text-xs bg-[#090a0a] border border-[#23252a] focus:border-[#5e6ad2] rounded-md px-2.5 py-1.5 text-white placeholder-[#4b4e54] outline-none font-mono uppercase"
                @keyup.enter="handleCreateVariable"
              />
            </div>

            <div class="sm:col-span-4">
              <label class="block text-[10px] font-medium uppercase tracking-wider text-[#8a8f98] mb-1">
                Valor
              </label>
              <input
                v-model="newValue"
                :type="newIsSecret ? 'password' : 'text'"
                placeholder="Valor da variável"
                class="w-full text-xs bg-[#090a0a] border border-[#23252a] focus:border-[#5e6ad2] rounded-md px-2.5 py-1.5 text-white placeholder-[#4b4e54] outline-none font-mono"
                @keyup.enter="handleCreateVariable"
              />
            </div>

            <div class="sm:col-span-2">
              <label class="block text-[10px] font-medium uppercase tracking-wider text-[#8a8f98] mb-1">
                Ambiente
              </label>
              <select
                v-model="newEnvironment"
                class="w-full text-xs bg-[#090a0a] border border-[#23252a] focus:border-[#5e6ad2] rounded-md px-2 py-1.5 text-white outline-none"
              >
                <option value="all">Todos ('all')</option>
                <option value="dev">DEV</option>
                <option value="qa">QA</option>
                <option value="prd">PRD</option>
              </select>
            </div>

            <div class="sm:col-span-3 flex items-center space-x-2">
              <label class="flex items-center space-x-1 text-xs text-[#8a8f98] cursor-pointer select-none">
                <input
                  v-model="newIsSecret"
                  type="checkbox"
                  class="rounded bg-[#090a0a] border-[#23252a] text-[#5e6ad2] focus:ring-0"
                />
                <span class="text-[11px]">Segredo</span>
              </label>

              <button
                @click="handleCreateVariable"
                :disabled="!newKey.trim()"
                class="flex-1 text-xs font-medium px-3 py-1.5 rounded-md bg-[#5e6ad2] hover:bg-[#828fff] disabled:opacity-40 text-white transition-colors flex items-center justify-center space-x-1"
              >
                <Plus class="h-3.5 w-3.5" />
                <span>Adicionar</span>
              </button>
            </div>
          </div>
        </div>

        <!-- Variables List -->
        <div class="space-y-2">
          <div
            v-if="activeList.length === 0"
            class="py-10 text-center border border-dashed border-[#23252a] rounded-lg"
          >
            <Key class="h-6 w-6 text-[#4b4e54] mx-auto mb-2" />
            <p class="text-xs text-[#8a8f98]">
              Nenhuma variável {{ activeTab === 'global' ? 'global' : 'deste fluxo' }} cadastrada no filtro selecionado.
            </p>
            <p class="text-[11px] text-[#62666d] mt-0.5">
              Utilize o formulário acima para adicionar uma nova chave.
            </p>
          </div>

          <div
            v-for="v in activeList"
            :key="v.id"
            class="p-3 rounded-lg bg-[#141516] border border-[#23252a] hover:border-[#35373e] transition-colors flex flex-col sm:flex-row sm:items-center justify-between gap-3"
          >
            <!-- Key & Badges -->
            <div class="flex items-center space-x-2 sm:w-1/3 flex-wrap">
              <span class="px-2 py-0.5 rounded bg-[#1c1d20] border border-[#2c2e35] text-xs font-mono text-[#828fff] font-medium">
                {{ v.key }}
              </span>

              <!-- Environment Badge -->
              <span
                class="text-[9px] font-bold px-1.5 py-0.2 rounded uppercase border font-mono"
                :class="{
                  'bg-emerald-500/15 text-emerald-400 border-emerald-500/30': (v.environment || 'all') === 'dev',
                  'bg-amber-500/15 text-amber-400 border-amber-500/30': v.environment === 'qa',
                  'bg-[#5e6ad2]/20 text-[#828fff] border-[#5e6ad2]/40': v.environment === 'prd',
                  'bg-[#1c1d20] text-[#8a8f98] border-[#2c2e35]': (v.environment || 'all') === 'all',
                }"
              >
                {{ (v.environment || 'all') === 'all' ? 'TODOS' : v.environment }}
              </span>

              <button
                @click="copyToClipboard(v.key)"
                class="text-[#8a8f98] hover:text-white p-1 rounded hover:bg-[#23252a] transition-colors"
                :title="`Copiar token {{${v.key}}}`"
              >
                <Check v-if="copiedKey === v.key" class="h-3.5 w-3.5 text-emerald-400" />
                <Copy v-else class="h-3.5 w-3.5" />
              </button>

              <span
                v-if="v.is_secret"
                class="text-[10px] text-amber-400/80 flex items-center space-x-0.5"
                title="Variável marcada como segredo"
              >
                <Lock class="h-3 w-3" />
              </span>
            </div>

            <!-- Value & Inline Edit -->
            <div class="flex-1 flex items-center space-x-2">
              <div class="relative flex-1">
                <input
                  :type="v.is_secret && !revealedSecrets[v.id] ? 'password' : 'text'"
                  :value="editingValues[v.id] !== undefined ? editingValues[v.id] : v.value"
                  @input="(e) => (editingValues[v.id] = (e.target as HTMLInputElement).value)"
                  class="w-full text-xs bg-[#090a0a] border border-[#23252a] focus:border-[#5e6ad2] rounded px-2.5 py-1 text-white font-mono outline-none"
                />

                <button
                  v-if="v.is_secret"
                  @click="toggleSecretVisibility(v.id)"
                  class="absolute right-2 top-1/2 -translate-y-1/2 text-[#8a8f98] hover:text-white"
                  title="Alternar visibilidade do segredo"
                >
                  <EyeOff v-if="revealedSecrets[v.id]" class="h-3.5 w-3.5" />
                  <Eye v-else class="h-3.5 w-3.5" />
                </button>
              </div>

              <!-- Save button if edited -->
              <button
                v-if="editingValues[v.id] !== undefined && editingValues[v.id] !== v.value"
                @click="handleUpdateVariable(v)"
                class="p-1 rounded bg-[#5e6ad2] hover:bg-[#828fff] text-white text-xs transition-colors"
                title="Salvar alteração de valor"
              >
                <Save class="h-3.5 w-3.5" />
              </button>
            </div>

            <!-- Actions -->
            <div class="flex items-center space-x-1.5 justify-end">
              <button
                @click="handleDeleteVariable(v.id)"
                class="p-1 rounded text-[#8a8f98] hover:text-rose-400 hover:bg-[#23252a] transition-colors"
                title="Excluir variável"
              >
                <Trash2 class="h-3.5 w-3.5" />
              </button>
            </div>
          </div>
        </div>
      </div>

      <!-- Footer -->
      <div class="border-t border-[#23252a] px-5 py-3 bg-[#141516] flex items-center justify-between">
        <span class="text-[11px] text-[#8a8f98]">
          Total de variáveis ativas: {{ varStore.variables.length }}
        </span>
        <button
          @click="emit('close')"
          class="text-xs px-3 py-1.5 rounded-md bg-[#23252a] hover:bg-[#2c2e35] text-white transition-colors"
        >
          Fechar
        </button>
      </div>
    </div>
  </div>
</template>
