<template>
  <div class="fixed right-4 top-4 z-50 flex flex-col gap-2">
    <div v-for="t in toasts" :key="t.id" :class="['rounded p-3 shadow', toastClass(t.type)]">
      <div class="text-sm">{{ t.message }}</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useUiStore } from '@/stores/ui';

const ui = useUiStore();
const toasts = computed(() => ui.toasts);

function toastClass(type: string | undefined) {
  if (type === 'success') return 'bg-green-50 text-green-800';
  if (type === 'error') return 'bg-red-50 text-red-800';
  return 'bg-gray-50 text-gray-800';
}
</script>
