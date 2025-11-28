import { defineStore } from 'pinia';
import { ref } from 'vue';

type Toast = { id: number; message: string; type?: 'success' | 'error' | 'info'; timeout?: number };

export const useUiStore = defineStore('ui', () => {
  const toasts = ref<Toast[]>([]);
  const nextToastId = ref(1);

  // Confirm dialog state
  const confirmOpen = ref(false);
  const confirmTitle = ref('Confirmar');
  const confirmMessage = ref('¿Estás seguro?');
  let confirmResolver: ((v: boolean) => void) | null = null;

  function showToast(message: string, type: Toast['type'] = 'info', timeout = 4000) {
    const id = nextToastId.value++;
    toasts.value.push({ id, message, type, timeout });
    // Auto remove
    setTimeout(() => {
      const idx = toasts.value.findIndex(t => t.id === id);
      if (idx !== -1) toasts.value.splice(idx, 1);
    }, timeout + 100);
  }

  function showConfirm(message: string, title = 'Confirmar'): Promise<boolean> {
    confirmTitle.value = title;
    confirmMessage.value = message;
    confirmOpen.value = true;
    return new Promise<boolean>((resolve) => {
      confirmResolver = resolve;
    });
  }

  function resolveConfirm(value: boolean) {
    if (confirmResolver) confirmResolver(value);
    confirmOpen.value = false;
    confirmResolver = null;
  }

  function removeToast(id: number) {
    const idx = toasts.value.findIndex(t => t.id === id);
    if (idx !== -1) toasts.value.splice(idx, 1);
  }

  return {
    toasts,
    showToast,
    removeToast,
    // Confirm
    confirmOpen,
    confirmTitle,
    confirmMessage,
    showConfirm,
    resolveConfirm,
  };
});
