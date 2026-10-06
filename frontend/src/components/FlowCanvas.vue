<script setup lang="ts">
import { computed } from 'vue'
import { VueFlow, useVueFlow } from '@vue-flow/core'
import { Background } from '@vue-flow/background'
import { Controls } from '@vue-flow/controls'
import { MiniMap } from '@vue-flow/minimap'
import CustomNode from './CustomNode.vue'
import { useFlowStore } from '../stores/flowStore'
import { useRegistryStore } from '../stores/registryStore'
import { useExecutionStore } from '../stores/executionStore'
import type { ComponentDefinition } from '../types/flow'

const flowStore = useFlowStore()
const registryStore = useRegistryStore()
const executionStore = useExecutionStore()

const { onConnect, onNodeClick, onPaneClick, onNodeDragStop, project } = useVueFlow()

function handleNodeDragStop(e: any) {
  if (Array.isArray(e?.nodes)) {
    for (const n of e.nodes) {
      if (n?.id && n?.position) {
        flowStore.updateNodePosition(n.id, { x: n.position.x, y: n.position.y })
      }
    }
  } else {
    const node = e?.node || e
    if (node?.id && node?.position) {
      flowStore.updateNodePosition(node.id, { x: node.position.x, y: node.position.y })
    }
  }
}

if (typeof onNodeDragStop === 'function') {
  onNodeDragStop(handleNodeDragStop)
}

// Map all component names to CustomNode
const nodeTypes = computed(() => {
  const types: Record<string, any> = {
    custom: CustomNode,
  }
  for (const comp of registryStore.components) {
    types[comp.name] = CustomNode
  }
  return types
})

// Dynamic edges with active animation when running
const styledEdges = computed(() => {
  return flowStore.edges.map((e) => ({
    ...e,
    type: 'smoothstep',
    animated: executionStore.isRunning,
    style: {
      stroke: executionStore.isRunning ? '#828fff' : '#5e6ad2',
      strokeWidth: 2,
    },
  }))
})

function getMinimapNodeColor(node: any) {
  const comp = registryStore.getComponent(node.type)
  const cat = comp?.category?.toLowerCase() || ''
  if (cat.includes('trigger')) return '#f59e0b'
  if (cat.includes('action')) return '#3b82f6'
  if (cat.includes('transform')) return '#10b981'
  return '#5e6ad2'
}

onConnect((params) => {
  flowStore.addEdge({
    source: params.source,
    sourceHandle: params.sourceHandle || undefined,
    target: params.target,
    targetHandle: params.targetHandle || undefined,
  })
})

onNodeClick(({ node }) => {
  flowStore.selectNode(node.id)
})

onPaneClick(() => {
  flowStore.selectNode(null)
})

function onDragOver(event: DragEvent) {
  event.preventDefault()
  if (event.dataTransfer) {
    event.dataTransfer.dropEffect = 'move'
  }
}

function onDrop(event: DragEvent) {
  event.preventDefault()
  if (!event.dataTransfer) return

  const data = event.dataTransfer.getData('application/flowbuild-node')
  if (!data) return

  try {
    const comp: ComponentDefinition = JSON.parse(data)
    const bounds = (event.currentTarget as HTMLElement).getBoundingClientRect()
    const position = project({
      x: event.clientX - bounds.left,
      y: event.clientY - bounds.top,
    })

    const initialInputs: Record<string, any> = {}
    for (const inp of comp.inputs) {
      if (inp.default !== undefined && inp.default !== null) {
        initialInputs[inp.name] = inp.default
      }
    }

    flowStore.addNode(comp.name, position, initialInputs)
  } catch {
    // Ignore invalid drop data
  }
}
</script>

<template>
  <main
    class="flex-1 h-full relative bg-[#010102] overflow-hidden"
    @dragover="onDragOver"
    @drop="onDrop"
  >
    <VueFlow
      v-model:nodes="flowStore.nodes"
      :edges="styledEdges"
      :node-types="nodeTypes"
      fit-view-on-init
      class="h-full w-full bg-[#010102]"
      @node-drag-stop="handleNodeDragStop"
    >
      <!-- Canvas Grid Background -->
      <Background :pattern-color="'#18191a'" :gap="24" :size="1" />

      <!-- Canvas Controls -->
      <Controls class="!bg-[#0f1011] !border-[#23252a] !text-[#f7f8f8] !rounded-lg !shadow-xl !p-1" />

      <!-- Canvas MiniMap -->
      <MiniMap
        :node-color="getMinimapNodeColor"
        :mask-color="'rgba(1, 1, 2, 0.85)'"
        class="!bg-[#0f1011] !border !border-[#23252a] !rounded-lg !shadow-2xl !overflow-hidden"
      />
    </VueFlow>
  </main>
</template>
