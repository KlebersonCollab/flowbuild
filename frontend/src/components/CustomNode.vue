<script setup lang="ts">
import { computed } from 'vue'
import { Handle, Position } from '@vue-flow/core'
import {
  Zap,
  Globe,
  Terminal,
  FileCode,
  Radio,
  Sliders,
  CheckCircle2,
  XCircle,
  SkipForward,
  Trash2,
  ChevronDown,
  ChevronUp,
  Clock,
  GitFork,
  Filter,
  MessageSquare,
  MessageCircle,
  Send,
  Mail,
  ArrowRightLeft,
  Calculator
} from 'lucide-vue-next'
import { useRegistryStore } from '../stores/registryStore'
import { useExecutionStore } from '../stores/executionStore'
import { useFlowStore } from '../stores/flowStore'
import type { NodeData } from '../types/flow'

const props = defineProps<{
  id: string
  type: string
  data: NodeData
  selected?: boolean
}>()

const registryStore = useRegistryStore()
const executionStore = useExecutionStore()
const flowStore = useFlowStore()

const isExpanded = computed({
  get: () => props.data?.expanded !== false,
  set: (val: boolean) => {
    flowStore.updateNodeExpanded(props.id, val)
  }
})

const definition = computed(() => registryStore.getComponent(props.type))
const nodeState = computed(() => executionStore.getNodeState(props.id))

const categoryMeta = computed(() => {
  const cat = (definition.value?.category || '').toLowerCase()
  const name = props.type.toLowerCase()

  if (cat.includes('trigger') || name.includes('trigger')) {
    if (name.includes('webhook')) {
      return {
        icon: Radio,
        bg: 'bg-cyan-500/10',
        text: 'text-cyan-400',
        border: 'border-cyan-500/30',
        badge: 'bg-cyan-500/15 text-cyan-300 border-cyan-500/30',
        dot: 'bg-cyan-400'
      }
    }
    return {
      icon: Zap,
      bg: 'bg-amber-500/10',
      text: 'text-amber-400',
      border: 'border-amber-500/30',
      badge: 'bg-amber-500/15 text-amber-300 border-amber-500/30',
      dot: 'bg-amber-400'
    }
  }

  if (name.includes('http') || name.includes('request')) {
    return {
      icon: Globe,
      bg: 'bg-blue-500/10',
      text: 'text-blue-400',
      border: 'border-blue-500/30',
      badge: 'bg-blue-500/15 text-blue-300 border-blue-500/30',
      dot: 'bg-blue-400'
    }
  }

  if (name.includes('python') || name.includes('script')) {
    return {
      icon: Terminal,
      bg: 'bg-purple-500/10',
      text: 'text-purple-400',
      border: 'border-purple-500/30',
      badge: 'bg-purple-500/15 text-purple-300 border-purple-500/30',
      dot: 'bg-purple-400'
    }
  }

  if (name.includes('filter')) {
    return {
      icon: Filter,
      bg: 'bg-emerald-500/10',
      text: 'text-emerald-400',
      border: 'border-emerald-500/30',
      badge: 'bg-emerald-500/15 text-emerald-300 border-emerald-500/30',
      dot: 'bg-emerald-400'
    }
  }

  if (name.includes('mapper')) {
    return {
      icon: ArrowRightLeft,
      bg: 'bg-emerald-500/10',
      text: 'text-emerald-400',
      border: 'border-emerald-500/30',
      badge: 'bg-emerald-500/15 text-emerald-300 border-emerald-500/30',
      dot: 'bg-emerald-400'
    }
  }

  if (name.includes('aggregator')) {
    return {
      icon: Calculator,
      bg: 'bg-emerald-500/10',
      text: 'text-emerald-400',
      border: 'border-emerald-500/30',
      badge: 'bg-emerald-500/15 text-emerald-300 border-emerald-500/30',
      dot: 'bg-emerald-400'
    }
  }

  if (cat.includes('transform') || name.includes('json') || name.includes('transform')) {
    return {
      icon: FileCode,
      bg: 'bg-emerald-500/10',
      text: 'text-emerald-400',
      border: 'border-emerald-500/30',
      badge: 'bg-emerald-500/15 text-emerald-300 border-emerald-500/30',
      dot: 'bg-emerald-400'
    }
  }

  if (name.includes('delay') || name.includes('sleep') || name.includes('await') || name.includes('timer')) {
    return {
      icon: Clock,
      bg: 'bg-amber-500/10',
      text: 'text-amber-400',
      border: 'border-amber-500/30',
      badge: 'bg-amber-500/15 text-amber-300 border-amber-500/30',
      dot: 'bg-amber-400'
    }
  }

  if (name.includes('switch') || name.includes('router')) {
    return {
      icon: GitFork,
      bg: 'bg-indigo-500/10',
      text: 'text-indigo-400',
      border: 'border-indigo-500/30',
      badge: 'bg-indigo-500/15 text-indigo-300 border-indigo-500/30',
      dot: 'bg-indigo-400'
    }
  }

  if (name.includes('discord')) {
    return {
      icon: MessageCircle,
      bg: 'bg-[#5865F2]/10',
      text: 'text-[#828fff]',
      border: 'border-[#5865F2]/30',
      badge: 'bg-[#5865F2]/15 text-[#828fff] border-[#5865F2]/30',
      dot: 'bg-[#5865F2]'
    }
  }

  if (name.includes('telegram')) {
    return {
      icon: Send,
      bg: 'bg-sky-500/10',
      text: 'text-sky-400',
      border: 'border-sky-500/30',
      badge: 'bg-sky-500/15 text-sky-300 border-sky-500/30',
      dot: 'bg-sky-400'
    }
  }

  if (name.includes('email') || name.includes('mail')) {
    return {
      icon: Mail,
      bg: 'bg-violet-500/10',
      text: 'text-violet-400',
      border: 'border-violet-500/30',
      badge: 'bg-violet-500/15 text-violet-300 border-violet-500/30',
      dot: 'bg-violet-400'
    }
  }

  if (name.includes('slack') || name.includes('notification')) {
    return {
      icon: MessageSquare,
      bg: 'bg-rose-500/10',
      text: 'text-rose-400',
      border: 'border-rose-500/30',
      badge: 'bg-rose-500/15 text-rose-300 border-rose-500/30',
      dot: 'bg-rose-400'
    }
  }

  return {
    icon: Sliders,
    bg: 'bg-[#5e6ad2]/10',
    text: 'text-[#828fff]',
    border: 'border-[#5e6ad2]/30',
    badge: 'bg-[#5e6ad2]/15 text-[#828fff] border-[#5e6ad2]/30',
    dot: 'bg-[#5e6ad2]'
  }
})

function getPortColor(typeStr: string) {
  switch (typeStr.toLowerCase()) {
    case 'dict':
      return '!bg-emerald-500 ring-2 ring-emerald-500/30'
    case 'list':
      return '!bg-teal-500 ring-2 ring-teal-500/30'
    case 'str':
      return '!bg-blue-500 ring-2 ring-blue-500/30'
    case 'int':
    case 'float':
      return '!bg-amber-500 ring-2 ring-amber-500/30'
    case 'code':
      return '!bg-purple-500 ring-2 ring-purple-500/30'
    case 'bool':
      return '!bg-cyan-500 ring-2 ring-cyan-500/30'
    default:
      return '!bg-[#5e6ad2] ring-2 ring-[#5e6ad2]/30'
  }
}

const statusClass = computed(() => {
  switch (nodeState.value.status) {
    case 'running':
      return 'border-[#5e6ad2] ring-2 ring-[#5e6ad2]/60 shadow-2xl shadow-[#5e6ad2]/25 scale-[1.01]'
    case 'completed':
      return 'border-[#27a644] ring-1 ring-[#27a644]/40 shadow-xl shadow-[#27a644]/15'
    case 'failed':
      return 'border-rose-500 ring-1 ring-rose-500/50 shadow-xl shadow-rose-500/25'
    case 'skipped':
      return 'border-amber-500/40 ring-1 ring-amber-500/20 opacity-70 bg-[#0f1011]/80'
    default:
      return props.selected
        ? 'border-[#5e6ad2] ring-2 ring-[#5e6ad2]/60 shadow-xl'
        : 'border-[#23252a] hover:border-[#3e3e44]'
  }
})

function onInputChange(name: string, val: any) {
  flowStore.updateNodeInput(props.id, name, val)
}

function onDeleteNode(e: Event) {
  e.stopPropagation()
  flowStore.removeNode(props.id)
}
</script>

<template>
  <div
    :class="[
      'w-[320px] rounded-xl bg-[#0f1011] text-[#f7f8f8] border shadow-2xl transition-all duration-200 select-none backdrop-blur-md',
      statusClass,
    ]"
  >
    <!-- Top Header -->
    <div class="flex items-center justify-between border-b border-[#23252a] px-3.5 py-2.5 bg-[#141516] rounded-t-xl">
      <div class="flex items-center space-x-2.5 min-w-0">
        <!-- Node Category Icon -->
        <div
          class="h-7 w-7 rounded-lg flex items-center justify-center shrink-0 border"
          :class="[categoryMeta.bg, categoryMeta.text, categoryMeta.border]"
        >
          <component :is="categoryMeta.icon" class="h-4 w-4" />
        </div>

        <div class="min-w-0">
          <div class="text-xs font-semibold tracking-tight text-[#f7f8f8] truncate">
            {{ definition?.displayName || type }}
          </div>
          <div class="flex items-center space-x-1.5 pt-0.5">
            <span
              class="text-[9px] font-mono px-1.5 py-0.2 rounded border leading-tight uppercase font-medium"
              :class="categoryMeta.badge"
            >
              {{ definition?.category || 'Node' }}
            </span>
          </div>
        </div>
      </div>

      <!-- Action badges & controls -->
      <div class="flex items-center space-x-1 shrink-0">
        <!-- Status indicator badge -->
        <span
          v-if="nodeState.status === 'running'"
          class="flex items-center space-x-1 text-[10px] font-bold text-[#828fff] bg-[#5e6ad2]/20 px-2 py-0.5 rounded-full border border-[#5e6ad2]/40 animate-pulse"
        >
          <span class="h-1.5 w-1.5 rounded-full bg-[#828fff] animate-ping"></span>
          <span>RODANDO</span>
        </span>
        <span
          v-else-if="nodeState.status === 'completed'"
          class="flex items-center space-x-1 text-[10px] font-bold text-[#27a644] bg-[#27a644]/15 px-2 py-0.5 rounded-full border border-[#27a644]/30"
        >
          <CheckCircle2 class="h-3 w-3" />
          <span>{{ nodeState.durationMs ? `${nodeState.durationMs}ms` : 'OK' }}</span>
        </span>
        <span
          v-else-if="nodeState.status === 'failed'"
          class="flex items-center space-x-1 text-[10px] font-bold text-rose-400 bg-rose-500/15 px-2 py-0.5 rounded-full border border-rose-500/30"
        >
          <XCircle class="h-3 w-3" />
          <span>ERRO</span>
        </span>
        <span
          v-else-if="nodeState.status === 'skipped'"
          class="flex items-center space-x-1 text-[10px] font-bold text-amber-400 bg-amber-500/15 px-2 py-0.5 rounded-full border border-amber-500/30"
          title="Nó ignorado devido à condição não atendida"
        >
          <SkipForward class="h-3 w-3" />
          <span>PULADO</span>
        </span>

        <!-- Expand / Collapse Toggle -->
        <button
          @click.stop="isExpanded = !isExpanded"
          class="h-6 w-6 rounded flex items-center justify-center text-[#8a8f98] hover:text-[#f7f8f8] hover:bg-[#23252a] transition-colors"
          :title="isExpanded ? 'Recolher campos' : 'Expandir campos'"
        >
          <ChevronUp v-if="isExpanded" class="h-3.5 w-3.5" />
          <ChevronDown v-else class="h-3.5 w-3.5" />
        </button>

        <!-- Delete button -->
        <button
          @click="onDeleteNode"
          class="h-6 w-6 rounded flex items-center justify-center text-[#8a8f98] hover:text-rose-400 hover:bg-rose-500/15 transition-colors"
          title="Excluir nó"
        >
          <Trash2 class="h-3.5 w-3.5" />
        </button>
      </div>
    </div>

    <!-- Description -->
    <div v-if="definition?.description && isExpanded" class="px-3.5 pt-2.5 pb-1">
      <p class="text-[11px] text-[#8a8f98] leading-tight">
        {{ definition.description }}
      </p>
    </div>

    <!-- Body Ports & Controls -->
    <div v-if="isExpanded" class="p-3.5 space-y-3">
      <!-- Input Handles & Controls -->
      <div v-if="definition?.inputs?.length" class="space-y-2.5">
        <div
          v-for="input in definition.inputs"
          :key="input.name"
          class="relative space-y-1"
        >
          <!-- Port Handle + Label -->
          <div class="flex items-center justify-between text-[11px] text-[#d0d6e0]">
            <div class="flex items-center space-x-1.5 min-w-0">
              <Handle
                v-if="input.is_handle !== false"
                :id="input.name"
                type="target"
                :position="Position.Left"
                :class="[
                  '!h-3.5 !w-3.5 !-left-[22px] !border-2 !border-[#0f1011] hover:!scale-125 transition-transform shadow-md',
                  getPortColor(input.type)
                ]"
              />
              <span class="truncate font-medium">{{ input.label }}</span>
              <span v-if="input.required" class="text-[#5e6ad2] font-bold">*</span>
            </div>
            <span class="text-[9px] text-[#62666d] font-mono shrink-0 uppercase tracking-wider">
              {{ input.type }}
            </span>
          </div>

          <!-- Quick Inline Card Inputs -->
          <div class="pt-0.5">
            <input
              v-if="input.type === 'str'"
              type="text"
              :value="data.inputs[input.name] ?? input.default ?? ''"
              @input="onInputChange(input.name, ($event.target as HTMLInputElement).value)"
              :placeholder="input.placeholder || 'Digite o valor...'"
              class="w-full text-[11px] rounded-md bg-[#141516] border border-[#23252a] px-2.5 py-1 text-[#f7f8f8] placeholder-[#62666d] focus:border-[#5e6ad2] focus:ring-1 focus:ring-[#5e6ad2] outline-none transition-colors nodrag font-mono"
            />
            <input
              v-else-if="input.type === 'int' || input.type === 'float'"
              type="number"
              step="any"
              :value="data.inputs[input.name] ?? input.default ?? 0"
              @input="onInputChange(input.name, Number(($event.target as HTMLInputElement).value))"
              class="w-full text-[11px] rounded-md bg-[#141516] border border-[#23252a] px-2.5 py-1 text-[#f7f8f8] focus:border-[#5e6ad2] focus:ring-1 focus:ring-[#5e6ad2] outline-none transition-colors nodrag font-mono"
            />
            <select
              v-else-if="input.type === 'select'"
              :value="data.inputs[input.name] ?? input.default"
              @change="onInputChange(input.name, ($event.target as HTMLSelectElement).value)"
              class="w-full text-[11px] rounded-md bg-[#141516] border border-[#23252a] px-2.5 py-1 text-[#f7f8f8] focus:border-[#5e6ad2] focus:ring-1 focus:ring-[#5e6ad2] outline-none transition-colors nodrag cursor-pointer"
            >
              <option v-for="opt in input.options || []" :key="opt" :value="opt" class="bg-[#141516] text-[#f7f8f8]">
                {{ opt }}
              </option>
            </select>
            <label
              v-else-if="input.type === 'bool'"
              class="flex items-center space-x-2 text-[11px] text-[#d0d6e0] cursor-pointer pt-0.5 nodrag"
            >
              <input
                type="checkbox"
                :checked="Boolean(data.inputs[input.name] ?? input.default ?? false)"
                @change="onInputChange(input.name, ($event.target as HTMLInputElement).checked)"
                class="rounded bg-[#141516] border-[#23252a] text-[#5e6ad2] focus:ring-[#5e6ad2] h-3.5 w-3.5 cursor-pointer"
              />
              <span class="text-[10px] text-[#8a8f98]">Ativar</span>
            </label>
          </div>
        </div>
      </div>

      <!-- Output Handles -->
      <div v-if="definition?.outputs?.length" class="space-y-2 border-t border-[#1e2024] pt-2.5">
        <div
          v-for="output in definition.outputs"
          :key="output.name"
          class="relative flex items-center justify-between text-[11px] text-[#d0d6e0]"
        >
          <span class="text-[9px] text-[#62666d] font-mono uppercase tracking-wider">{{ output.type }}</span>
          <span class="truncate pl-2 font-medium text-right text-[#f7f8f8]">{{ output.label }}</span>
          <Handle
            :id="output.name"
            type="source"
            :position="Position.Right"
            :class="[
              '!h-3.5 !w-3.5 !-right-[22px] !border-2 !border-[#0f1011] hover:!scale-125 transition-transform shadow-md',
              getPortColor(output.type)
            ]"
          />
        </div>
      </div>
    </div>
  </div>
</template>
