<script setup lang="ts">
import PublicNavbar from './PublicNavbar.vue';
import Footer from './Footer.vue';
</script>

<template>
  <div class="flex min-h-screen flex-col">
    <PublicNavbar />
    <main class="flex-1">
      <router-view />
    </main>
    <Footer />
  </div>
</template>
