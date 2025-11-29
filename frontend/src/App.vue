<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue';
import { useAuthStore } from '@/stores';
import ConfirmDialog from '@/components/common/ConfirmDialog.vue';
import ToastContainer from '@/components/common/ToastContainer.vue';
import GlobalSearch from '@/components/common/GlobalSearch.vue';

const authStore = useAuthStore();
const showGlobalSearch = ref(false);

onMounted(() => {
  authStore.initializeAuth();
  
  // Global keyboard shortcut for search (Ctrl+K or Cmd+K)
  const handleKeyDown = (e: KeyboardEvent) => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
      e.preventDefault();
      showGlobalSearch.value = true;
    }
  };
  
  window.addEventListener('keydown', handleKeyDown);
  
  onUnmounted(() => {
    window.removeEventListener('keydown', handleKeyDown);
  });
});
</script>

<template>
  <router-view />
  <!-- Global UI helpers -->
  <ConfirmDialog />
  <ToastContainer />
  <GlobalSearch :isOpen="showGlobalSearch" @close="showGlobalSearch = false" />
</template>
