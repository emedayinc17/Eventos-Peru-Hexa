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
import { watch } from 'vue';
import Modal from './Modal.vue';
import Button from './Button.vue';
import { useUiStore } from '@/stores/ui';

const ui = useUiStore();

const open = ui.confirmOpen;
const title = ui.confirmTitle;
const message = ui.confirmMessage;

function confirm() {
  ui.resolveConfirm(true);
}

function cancel() {
  ui.resolveConfirm(false);
}

function onClose() {
  ui.resolveConfirm(false);
}
</script>
