<script setup lang="ts">
import { computed } from 'vue'
import { VueFlow, useVueFlow } from '@vue-flow/core'
import { Background } from '@vue-flow/background'
import { Controls } from '@vue-flow/controls'
import CustomNode from './CustomNode.vue'
import { useFlowStore } from '../stores/flowStore'
import { useRegistryStore } from '../stores/registryStore'
import type { ComponentDefinition } from '../types/flow'

const flowStore = useFlowStore()
const registryStore = useRegistryStore()

const { onConnect, onNodeClick, onPaneClick, project } = useVueFlow()

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
      v-model:edges="flowStore.edges"
      :node-types="nodeTypes"
      fit-view-on-init
      class="h-full w-full bg-[#010102]"
    >
      <Background :pattern-color="'#18191a'" :gap="20" />
      <Controls class="!bg-[#0f1011] !border-[#23252a] !text-[#f7f8f8] !rounded-md shadow-lg" />
    </VueFlow>
  </main>
</template>
