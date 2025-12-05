<template>
  <div class="app">
    <LayoutHeader />
    <RouterView />
    <LayoutFooter />
  </div>
</template>

<script setup lang="ts">
import { RouterView } from 'vue-router'
import LayoutHeader from '@/components/LayoutHeader.vue'
import LayoutFooter from '@/components/LayoutFooter.vue'
</script>

<style scoped>
.app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}
</style>
