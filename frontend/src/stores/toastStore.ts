import { defineStore } from 'pinia'
import { ref } from 'vue'

export type ToastType = 'success' | 'warn' | 'error' | 'info'

export interface ToastMessage {
  id: string
  type: ToastType
  message: string
  title?: string
  duration?: number
}

export const useToastStore = defineStore('toast', () => {
  const toasts = ref<ToastMessage[]>([])

  function addToast(
    type: ToastType,
    message: string,
    title?: string,
    durationMs: number = 4500
  ): string {
    const id = `toast-${Date.now()}-${Math.random().toString(36).substring(2, 7)}`
    const toast: ToastMessage = {
      id,
      type,
      message,
      title,
      duration: durationMs,
    }

    toasts.value.push(toast)

    if (durationMs > 0) {
      setTimeout(() => {
        removeToast(id)
      }, durationMs)
    }

    return id
  }

  function removeToast(id: string): void {
    const index = toasts.value.findIndex((t) => t.id === id)
    if (index !== -1) {
      toasts.value.splice(index, 1)
    }
  }

  function clearAll(): void {
    toasts.value = []
  }

  function success(message: string, title?: string, duration?: number): string {
    return addToast('success', message, title, duration)
  }

  function warn(message: string, title?: string, duration?: number): string {
    return addToast('warn', message, title, duration)
  }

  function error(message: string, title?: string, duration?: number): string {
    return addToast('error', message, title, duration)
  }

  function info(message: string, title?: string, duration?: number): string {
    return addToast('info', message, title, duration)
  }

  return {
    toasts,
    addToast,
    removeToast,
    clearAll,
    success,
    warn,
    error,
    info,
  }
})
