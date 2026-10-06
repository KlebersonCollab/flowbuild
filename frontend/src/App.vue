<script setup lang="ts">
import { onMounted } from 'vue'
import TopNav from './components/TopNav.vue'
import ComponentPalette from './components/ComponentPalette.vue'
import FlowCanvas from './components/FlowCanvas.vue'
import NodeInspector from './components/NodeInspector.vue'
import { useRegistryStore } from './stores/registryStore'
import { useFlowStore } from './stores/flowStore'

const registryStore = useRegistryStore()
const flowStore = useFlowStore()

onMounted(async () => {
  await registryStore.fetchComponents()

  // If canvas is empty, seed with initial trigger and action nodes
  if (flowStore.nodes.length === 0) {
    const triggerId = flowStore.addNode('ManualTriggerComponent', { x: 120, y: 160 }, {
      initial_payload: { message: "Hello from FlowBuild" }
    })
    const actionId = flowStore.addNode('JsonTransformComponent', { x: 440, y: 160 }, {
      expression: "payload['message'].upper()"
    })
    flowStore.addEdge({
      source: triggerId,
      sourceHandle: 'data',
      target: actionId,
      targetHandle: 'input_data'
    })
  }
})
</script>

<template>
  <div class="h-screen w-screen flex flex-col bg-[#010102] text-[#f7f8f8] overflow-hidden select-none font-sans">
    <!-- Top Bar -->
    <TopNav />

    <!-- Main Workspace (Palette + Canvas + Inspector) -->
    <div class="flex-1 flex overflow-hidden relative">
      <ComponentPalette />
      <FlowCanvas />
      <NodeInspector />
    </div>
  </div>
</template>
