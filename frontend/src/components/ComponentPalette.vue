<script setup lang="ts">
import { ref, computed } from 'vue'
import {
  Search,
  Zap,
  Radio,
  Globe,
  Terminal,
  FileCode,
  Sliders,
  ChevronDown,
  ChevronRight,
  Plus,
  Boxes,
  Clock,
  GitFork,
  Filter,
  MessageSquare,
  MessageCircle,
  Send,
  Mail,
  ArrowRightLeft,
  Calculator,
  FileSpreadsheet,
  Database,
  HardDrive,
  Repeat,
  ShieldAlert
} from 'lucide-vue-next'
import { useRegistryStore } from '../stores/registryStore'
import { useFlowStore } from '../stores/flowStore'
import type { ComponentDefinition } from '../types/flow'

const registryStore = useRegistryStore()
const flowStore = useFlowStore()
const searchQuery = ref<string>('')
const collapsedCategories = ref<Record<string, boolean>>({})

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

function toggleCategory(category: string) {
  collapsedCategories.value[category] = !collapsedCategories.value[category]
}

function getNodeIcon(comp: ComponentDefinition) {
  const name = comp.name.toLowerCase()
  const cat = comp.category.toLowerCase()

  if (name.includes('telegram')) return Send
  if (name.includes('email') || name.includes('mail')) return Mail
  if (name.includes('webhook')) return Radio
  if (cat.includes('trigger') || name.includes('trigger')) return Zap
  if (name.includes('delay') || name.includes('sleep') || name.includes('await') || name.includes('timer')) return Clock
  if (name.includes('switch') || name.includes('router')) return GitFork
  if (name.includes('loop') || name.includes('iterator') || name.includes('batch')) return Repeat
  if (name.includes('trycatch') || name.includes('catch') || name.includes('try')) return ShieldAlert
  if (name.includes('filter')) return Filter
  if (name.includes('mapper')) return ArrowRightLeft
  if (name.includes('aggregator')) return Calculator
  if (name.includes('csv')) return FileSpreadsheet
  if (name.includes('keyvalue') || name.includes('store') || name.includes('kv')) return HardDrive
  if (name.includes('database') || name.includes('sql') || cat.includes('storage')) return Database
  if (name.includes('discord')) return MessageCircle
  if (name.includes('slack') || name.includes('notification')) return MessageSquare
  if (name.includes('http') || name.includes('request')) return Globe
  if (name.includes('python') || name.includes('script')) return Terminal
  if (cat.includes('transform') || name.includes('json')) return FileCode
  return Sliders
}

function getNodeIconColor(comp: ComponentDefinition) {
  const name = comp.name.toLowerCase()
  const cat = comp.category.toLowerCase()

  if (name.includes('telegram')) return 'text-sky-400 bg-sky-500/10 border-sky-500/20'
  if (name.includes('email') || name.includes('mail')) return 'text-violet-400 bg-violet-500/10 border-violet-500/20'
  if (name.includes('webhook')) return 'text-cyan-400 bg-cyan-500/10 border-cyan-500/20'
  if (cat.includes('trigger') || name.includes('trigger')) return 'text-amber-400 bg-amber-500/10 border-amber-500/20'
  if (name.includes('delay') || name.includes('sleep') || name.includes('await') || name.includes('timer')) return 'text-amber-400 bg-amber-500/10 border-amber-500/20'
  if (name.includes('switch') || name.includes('router') || name.includes('loop') || name.includes('iterator')) return 'text-indigo-400 bg-indigo-500/10 border-indigo-500/20'
  if (name.includes('trycatch') || name.includes('catch') || name.includes('try')) return 'text-rose-400 bg-rose-500/10 border-rose-500/20'
  if (name.includes('filter') || name.includes('mapper') || name.includes('aggregator') || name.includes('csv')) return 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20'
  if (name.includes('database') || name.includes('sql') || cat.includes('storage')) return 'text-teal-400 bg-teal-500/10 border-teal-500/20'
  if (name.includes('discord')) return 'text-[#828fff] bg-[#5865F2]/10 border-[#5865F2]/20'
  if (name.includes('slack') || name.includes('notification')) return 'text-rose-400 bg-rose-500/10 border-rose-500/20'
  if (name.includes('http') || name.includes('request')) return 'text-blue-400 bg-blue-500/10 border-blue-500/20'
  if (name.includes('python') || name.includes('script')) return 'text-purple-400 bg-purple-500/10 border-purple-500/20'
  if (cat.includes('transform') || name.includes('json')) return 'text-emerald-400 bg-emerald-500/10 border-emerald-500/20'
  return 'text-[#828fff] bg-[#5e6ad2]/10 border-[#5e6ad2]/20'
}

function onAddNode(comp: ComponentDefinition) {
  const initialInputs: Record<string, any> = {}
  for (const inp of comp.inputs) {
    if (inp.default !== undefined && inp.default !== null) {
      initialInputs[inp.name] = inp.default
    }
  }

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
  <aside class="w-72 border-r border-[#23252a] bg-[#0f1011] text-[#f7f8f8] flex flex-col h-full select-none z-10">
    <!-- Header -->
    <div class="p-3 border-b border-[#23252a] bg-[#141516] space-y-2.5">
      <div class="flex items-center justify-between">
        <div class="flex items-center space-x-2">
          <Boxes class="h-4 w-4 text-[#5e6ad2]" />
          <span class="text-xs font-semibold tracking-wider uppercase text-[#f7f8f8]">Biblioteca de Nós</span>
        </div>
        <span class="text-[10px] text-[#8a8f98] font-mono bg-[#0f1011] px-2 py-0.5 rounded border border-[#23252a]">
          {{ registryStore.components.length }} nós
        </span>
      </div>

      <!-- Search Input -->
      <div class="relative">
        <Search class="h-3.5 w-3.5 text-[#62666d] absolute left-2.5 top-2.5 pointer-events-none" />
        <input
          v-model="searchQuery"
          type="text"
          placeholder="Buscar automação..."
          class="w-full text-xs rounded-md bg-[#0f1011] border border-[#23252a] pl-8 pr-2.5 py-1.5 text-[#f7f8f8] placeholder-[#62666d] focus:border-[#5e6ad2] focus:ring-1 focus:ring-[#5e6ad2] outline-none transition-colors"
        />
      </div>
    </div>

    <!-- Categories List -->
    <div class="flex-1 overflow-y-auto p-2.5 space-y-3">
      <div
        v-for="(list, category) in filteredCategories"
        :key="category"
        class="space-y-1"
      >
        <!-- Category Accordion Header -->
        <button
          @click="toggleCategory(category)"
          class="w-full flex items-center justify-between px-2 py-1.5 text-[11px] font-semibold tracking-wider uppercase text-[#8a8f98] hover:text-[#f7f8f8] transition-colors rounded hover:bg-[#141516]"
        >
          <div class="flex items-center space-x-1.5">
            <component :is="collapsedCategories[category] ? ChevronRight : ChevronDown" class="h-3 w-3 text-[#62666d]" />
            <span>{{ category }}</span>
          </div>
          <span class="text-[9px] font-mono text-[#62666d]">{{ list.length }}</span>
        </button>

        <!-- Components under Category -->
        <div v-if="!collapsedCategories[category]" class="space-y-1 pt-0.5">
          <div
            v-for="comp in list"
            :key="comp.name"
            draggable="true"
            @dragstart="onDragStart($event, comp)"
            @click="onAddNode(comp)"
            class="group flex items-center space-x-2.5 p-2 rounded-lg bg-[#141516] border border-[#23252a] hover:border-[#5e6ad2]/60 hover:bg-[#18191a] transition-all cursor-grab active:cursor-grabbing shadow-sm"
          >
            <!-- Node Icon -->
            <div
              class="h-7 w-7 rounded-md border flex items-center justify-center shrink-0 transition-colors"
              :class="getNodeIconColor(comp)"
            >
              <component :is="getNodeIcon(comp)" class="h-3.5 w-3.5" />
            </div>

            <!-- Details -->
            <div class="flex-1 min-w-0">
              <div class="text-xs font-medium text-[#f7f8f8] truncate group-hover:text-white flex items-center justify-between">
                <span>{{ comp.displayName }}</span>
                <Plus class="h-3 w-3 text-[#62666d] group-hover:text-[#828fff] opacity-0 group-hover:opacity-100 transition-opacity" />
              </div>
              <p class="text-[10px] text-[#8a8f98] truncate leading-tight">
                {{ comp.description }}
              </p>
            </div>
          </div>
        </div>
      </div>

      <!-- Empty state -->
      <div
        v-if="Object.keys(filteredCategories).length === 0"
        class="py-12 text-center text-xs text-[#62666d] space-y-1"
      >
        <p>Nenhum componente encontrado.</p>
        <p class="text-[10px] text-[#3e3e44]">Tente buscar por "HTTP", "JSON" ou "Trigger".</p>
      </div>
    </div>
  </aside>
</template>
