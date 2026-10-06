<script setup lang="ts">
import { computed } from 'vue'
import { Handle, Position } from '@vue-flow/core'
import { useRegistryStore } from '../stores/registryStore'
import { useExecutionStore } from '../stores/executionStore'
import type { NodeData } from '../types/flow'

const props = defineProps<{
  id: string
  type: string
  data: NodeData
  selected?: boolean
}>()

const registryStore = useRegistryStore()
const executionStore = useExecutionStore()

const definition = computed(() => registryStore.getComponent(props.type))

const nodeState = computed(() => executionStore.getNodeState(props.id))

const statusClass = computed(() => {
  switch (nodeState.value.status) {
    case 'running':
      return 'border-[#5e6ad2] ring-2 ring-[#5e6ad2]/40 shadow-lg shadow-[#5e6ad2]/20 animate-pulse'
    case 'completed':
      return 'border-[#27a644] ring-1 ring-[#27a644]/30'
    case 'failed':
      return 'border-rose-500 ring-1 ring-rose-500/30'
    default:
      return props.selected ? 'border-[#5e6ad2] ring-1 ring-[#5e6ad2]/50' : 'border-[#23252a]'
  }
})
</script>

<template>
  <div
    :class="[
      'min-w-[240px] max-w-[320px] rounded-lg bg-[#0f1011] text-[#f7f8f8] shadow-xl transition-all duration-150',
      statusClass,
    ]"
  >
    <!-- Node Header -->
    <div class="flex items-center justify-between border-b border-[#23252a] px-3 py-2 bg-[#141516] rounded-t-lg">
      <div class="flex items-center space-x-2">
        <div class="h-2 w-2 rounded-full bg-[#5e6ad2]"></div>
        <span class="text-xs font-semibold tracking-tight text-[#f7f8f8]">
          {{ definition?.displayName || type }}
        </span>
      </div>
      <div class="flex items-center space-x-1">
        <span
          v-if="nodeState.status === 'running'"
          class="text-[10px] uppercase font-bold text-[#828fff] animate-pulse"
        >
          Running...
        </span>
        <span
          v-else-if="nodeState.status === 'completed'"
          class="text-[10px] uppercase font-bold text-[#27a644]"
        >
          Done
        </span>
        <span
          v-else-if="nodeState.status === 'failed'"
          class="text-[10px] uppercase font-bold text-rose-400"
        >
          Error
        </span>
        <span v-else class="text-[10px] text-[#8a8f98] font-mono">
          {{ definition?.category || 'Node' }}
        </span>
      </div>
    </div>

    <!-- Node Ports Body -->
    <div class="p-3 space-y-3">
      <!-- Description if any -->
      <p v-if="definition?.description" class="text-[11px] text-[#8a8f98] leading-tight">
        {{ definition.description }}
      </p>

      <!-- Input Ports (Left) -->
      <div v-if="definition?.inputs?.length" class="space-y-1.5 pt-1">
        <div
          v-for="input in definition.inputs"
          :key="input.name"
          class="relative flex items-center justify-between text-[11px] text-[#d0d6e0]"
        >
          <Handle
            v-if="input.is_handle !== false"
            :id="input.name"
            type="target"
            :position="Position.Left"
            class="!h-2.5 !w-2.5 !-left-[18px] !bg-[#5e6ad2] !border-2 !border-[#0f1011] hover:!scale-125 transition-transform"
          />
          <span class="truncate pr-2 font-medium">{{ input.label }}</span>
          <span class="text-[9px] text-[#62666d] font-mono">{{ input.type }}</span>
        </div>
      </div>

      <!-- Output Ports (Right) -->
      <div v-if="definition?.outputs?.length" class="space-y-1.5 border-t border-[#18191a] pt-2">
        <div
          v-for="output in definition.outputs"
          :key="output.name"
          class="relative flex items-center justify-between text-[11px] text-[#d0d6e0]"
        >
          <span class="text-[9px] text-[#62666d] font-mono">{{ output.type }}</span>
          <span class="truncate pl-2 font-medium text-right">{{ output.label }}</span>
          <Handle
            :id="output.name"
            type="source"
            :position="Position.Right"
            class="!h-2.5 !w-2.5 !-right-[18px] !bg-[#27a644] !border-2 !border-[#0f1011] hover:!scale-125 transition-transform"
          />
        </div>
      </div>
    </div>
  </div>
</template>
