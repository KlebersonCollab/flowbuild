<script setup lang="ts">
import { onMounted, onUnmounted } from 'vue'
import TopNav from './components/TopNav.vue'
import ComponentPalette from './components/ComponentPalette.vue'
import FlowCanvas from './components/FlowCanvas.vue'
import NodeInspector from './components/NodeInspector.vue'
import ExecutionDrawer from './components/ExecutionDrawer.vue'
import { useRegistryStore } from './stores/registryStore'
import { useFlowStore } from './stores/flowStore'
import { useExecutionStore } from './stores/executionStore'

const registryStore = useRegistryStore()
const flowStore = useFlowStore()
const executionStore = useExecutionStore()

function handleKeyDown(event: KeyboardEvent) {
  // Ctrl+Enter or Cmd+Enter to run flow
  if ((event.ctrlKey || event.metaKey) && event.key === 'Enter') {
    event.preventDefault()
    if (!executionStore.isRunning) {
      executionStore.runFlowStream(flowStore.toFlowPayload())
    }
  }
}

onMounted(async () => {
  window.addEventListener('keydown', handleKeyDown)
  await registryStore.fetchComponents()

  // Restore persisted flow from backend database (or local cache)
  await flowStore.loadPersistedFlow()
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeyDown)
})
</script>

<template>
  <div class="h-screen w-screen flex flex-col bg-[#010102] text-[#f7f8f8] overflow-hidden select-none font-sans antialiased">
    <!-- Top Navigation & Action Bar -->
    <TopNav />

    <!-- Main Workspace (Palette + Canvas Workspace + Inspector) -->
    <div class="flex-1 flex overflow-hidden relative">
      <!-- Left Sidebar: Component Palette -->
      <ComponentPalette />

      <!-- Center: Canvas + Bottom Console Drawer -->
      <div class="flex-1 flex flex-col h-full overflow-hidden relative">
        <FlowCanvas />
        <ExecutionDrawer />
      </div>

      <!-- Right Sidebar: Selected Node Inspector -->
      <NodeInspector />
    </div>
  </div>
</template>
