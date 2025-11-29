<template>
  <Modal v-model:open="open" :title="title" @close="onClose">
    <div class="py-4">
      <p class="text-gray-700">{{ message }}</p>
    </div>
    <template #footer>
      <div class="flex justify-end gap-3">
        <Button variant="secondary" @click="cancel">Cancelar</Button>
        <Button variant="danger" @click="confirm">Confirmar</Button>
      </div>
    </template>
  </Modal>
</template>

<script setup lang="ts">
import { watch, ref, computed, onMounted } from 'vue';
import Modal from './Modal.vue';
import Button from './Button.vue';
import { useUiStore } from '@/stores/ui';

const ui = useUiStore();

const title = ui.confirmTitle;
const message = ui.confirmMessage;

// Create a computed binding with explicit setter so update:open events
// and programmatic changes keep ui.confirmOpen in sync reliably.
// Handle both cases: Pinia store may expose `confirmOpen` as a ref (with .value)
// or as a plain boolean (unwrapped). Support both to avoid runtime errors.
const open = computed({
  get: () => {
    const v: any = (ui as any).confirmOpen;
    if (v && typeof v === 'object' && 'value' in v) return v.value;
    return v as boolean;
  },
  set: (val: boolean) => {
    console.debug('[ConfirmDialog] open setter ->', val);
    const v: any = (ui as any).confirmOpen;
    try {
      if (v && typeof v === 'object' && 'value' in v) v.value = val;
      else (ui as any).confirmOpen = val;
    } catch (e) {
      console.error('[ConfirmDialog] error setting confirmOpen on store', e);
    }
  }
});

onMounted(() => {
  // Expose ui for quick debug in the browser console during development
  try {
    // @ts-ignore
    window.__ui = ui;
  } catch (e) {
    /* ignore in non-browser contexts */
  }
  console.debug('[ConfirmDialog] mounted, initial open=', open.value);
});

watch(() => open.value, (v) => {
  console.debug('[ConfirmDialog] open changed ->', v);
});

const confirming = ref(false);

function confirm() {
  if (confirming.value) return;
  confirming.value = true;
  console.debug('[ConfirmDialog] confirm clicked');
  try {
    ui.resolveConfirm(true);
  } catch (e) {
    console.error('[ConfirmDialog] error calling resolveConfirm', e);
  }
  // Ensure dialog closes: prefer setting the computed which updates the store
  try {
    open.value = false;
  } catch (e) {
    console.error('[ConfirmDialog] error forcing open=false', e);
  }
  confirming.value = false;
}


function cancel() {
  ui.resolveConfirm(false);
}

function onClose() {
  console.debug('[ConfirmDialog] onClose called');
  ui.resolveConfirm(false);
}
</script>
