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
    console.debug('[ui] showConfirm set', { title, message });
    confirmOpen.value = true;
    return new Promise<boolean>((resolve) => {
      confirmResolver = resolve;
    });
  }

  // showConfirmWithFallback: intenta abrir el diálogo global; si no se abre
  // en `timeoutMs`, usa `window.confirm` como fallback sin bloquear.
  async function showConfirmWithFallback(message: string, title = 'Confirmar', timeoutMs = 250): Promise<boolean> {
    // Llamada primaria al diálogo
    const p = showConfirm(message, title);

    // Si el modal no abre en el tiempo especificado, preguntar por window.confirm
    const fallback = new Promise<boolean>((resolve) => {
      setTimeout(() => {
        // Si el diálogo global no está abierto, asumimos que algo falló y mostramos fallback
        if (!confirmOpen.value) {
          try {
            const r = window.confirm(message);
            console.debug('[ui] fallback window.confirm used', { message, result: r });
            // resolver la promesa de showConfirm si aún está pendiente
            if (confirmResolver) {
              try { confirmResolver(r); } catch (e) { /* ignore */ }
              confirmOpen.value = false;
              confirmResolver = null;
            }
            resolve(r);
          } catch (e) {
            console.error('[ui] error using fallback confirm', e);
            resolve(false);
          }
        } else {
          // diálogo abierto — no usar fallback
          resolve(false);
        }
      }, timeoutMs);
    });

    // Race: si p se resuelve primero, tomamos su valor; si fallback se resuelve con true/false
    const result = await Promise.race([p, fallback]);
    // si fallback resolvió with false because dialog was actually opened, await original
    if (result === false && confirmOpen.value) {
      return p;
    }
    return result as boolean;
  }

  function resolveConfirm(value: boolean) {
    console.debug('[ui] resolveConfirm called with', value);
    if (confirmResolver) {
      try {
        confirmResolver(value);
      } catch (e) {
        console.error('[ui] error resolving confirm promise', e);
      }
    }
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
    showConfirmWithFallback,
    resolveConfirm,
  };
});
