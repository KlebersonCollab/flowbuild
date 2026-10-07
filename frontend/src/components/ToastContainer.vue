<script setup lang="ts">
import {
  AlertTriangle,
  CheckCircle2,
  XCircle,
  Info,
  X,
} from 'lucide-vue-next'
import { useToastStore, type ToastType } from '../stores/toastStore'

const toastStore = useToastStore()

function getIcon(type: ToastType) {
  switch (type) {
    case 'success':
      return CheckCircle2
    case 'error':
      return XCircle
    case 'warn':
      return AlertTriangle
    case 'info':
    default:
      return Info
  }
}

function getIconColorClass(type: ToastType): string {
  switch (type) {
    case 'success':
      return 'text-[#27a644]'
    case 'error':
      return 'text-rose-400'
    case 'warn':
      return 'text-amber-400'
    case 'info':
    default:
      return 'text-[#828fff]'
  }
}

function getBorderClass(type: ToastType): string {
  switch (type) {
    case 'success':
      return 'border-[#27a644]/40 bg-[#0f1011]'
    case 'error':
      return 'border-rose-500/40 bg-[#0f1011]'
    case 'warn':
      return 'border-amber-500/40 bg-[#0f1011]'
    case 'info':
    default:
      return 'border-[#5e6ad2]/40 bg-[#0f1011]'
  }
}
</script>

<template>
  <div
    class="fixed bottom-5 right-5 z-50 flex flex-col space-y-2 pointer-events-none max-w-sm w-full px-4"
    aria-live="polite"
  >
    <TransitionGroup name="toast-slide">
      <div
        v-for="toast in toastStore.toasts"
        :key="toast.id"
        class="pointer-events-auto p-3 rounded-lg border shadow-xl flex items-start space-x-3 transition-all duration-300"
        :class="getBorderClass(toast.type)"
      >
        <!-- Icon -->
        <component
          :is="getIcon(toast.type)"
          class="h-4 w-4 shrink-0 mt-0.5"
          :class="getIconColorClass(toast.type)"
        />

        <!-- Content -->
        <div class="flex-1 min-w-0 pr-1">
          <h4
            v-if="toast.title"
            class="text-xs font-semibold text-white tracking-tight"
          >
            {{ toast.title }}
          </h4>
          <p class="text-xs text-[#d0d6e0] leading-relaxed break-words">
            {{ toast.message }}
          </p>
        </div>

        <!-- Close Button -->
        <button
          @click="toastStore.removeToast(toast.id)"
          class="text-[#8a8f98] hover:text-white p-0.5 rounded hover:bg-[#23252a] transition-colors shrink-0 -mr-1 -mt-0.5"
          title="Fechar notificação"
        >
          <X class="h-3.5 w-3.5" />
        </button>
      </div>
    </TransitionGroup>
  </div>
</template>

<style scoped>
.toast-slide-enter-active,
.toast-slide-leave-active {
  transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
}

.toast-slide-enter-from {
  opacity: 0;
  transform: translateY(12px) scale(0.96);
}

.toast-slide-leave-to {
  opacity: 0;
  transform: translateX(20px) scale(0.96);
}
</style>
