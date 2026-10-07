import { describe, it, expect, beforeEach, vi, afterEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useToastStore } from '../src/stores/toastStore'

describe('Toast Notification Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.useFakeTimers()
  })

  afterEach(() => {
    vi.restoreAllMocks()
    vi.useRealTimers()
  })

  it('adds warn, error, success, and info toasts with appropriate types', () => {
    const store = useToastStore()

    store.warn('Workflow precisa de um nó Trigger', 'Atenção')
    expect(store.toasts.length).toBe(1)
    expect(store.toasts[0].type).toBe('warn')
    expect(store.toasts[0].title).toBe('Atenção')
    expect(store.toasts[0].message).toBe('Workflow precisa de um nó Trigger')

    store.error('Falha ao processar arquivo', 'Erro')
    expect(store.toasts.length).toBe(2)
    expect(store.toasts[1].type).toBe('error')

    store.success('Fluxo salvo com sucesso')
    expect(store.toasts.length).toBe(3)
    expect(store.toasts[2].type).toBe('success')

    store.info('Ambiente alterado para QA')
    expect(store.toasts.length).toBe(4)
    expect(store.toasts[3].type).toBe('info')
  })

  it('removes a specific toast by id manually', () => {
    const store = useToastStore()
    const id = store.warn('Mensagem temporária')
    expect(store.toasts.length).toBe(1)

    store.removeToast(id)
    expect(store.toasts.length).toBe(0)
  })

  it('automatically removes toast after duration expires', () => {
    const store = useToastStore()
    store.warn('Aviso com timer', undefined, 3000)
    expect(store.toasts.length).toBe(1)

    // Fast-forward 2.9 seconds: toast still present
    vi.advanceTimersByTime(2900)
    expect(store.toasts.length).toBe(1)

    // Fast-forward past 3 seconds: toast auto-removed
    vi.advanceTimersByTime(200)
    expect(store.toasts.length).toBe(0)
  })

  it('clears all toasts at once', () => {
    const store = useToastStore()
    store.info('Info 1')
    store.warn('Warn 2')
    store.error('Error 3')
    expect(store.toasts.length).toBe(3)

    store.clearAll()
    expect(store.toasts.length).toBe(0)
  })
})
