<template>
  <div class="loading-spinner" :class="sizeClass">
    <div class="spinner"></div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  size?: 'sm' | 'md' | 'lg'
}

const props = withDefaults(defineProps<Props>(), {
  size: 'md'
})

const sizeClass = computed(() => `size-${props.size}`)
</script>

<style scoped>
.loading-spinner {
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.spinner {
  border: 3px solid rgba(255, 255, 255, 0.3);
  border-top-color: var(--white);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

/* 크기 변형 */
.size-sm .spinner {
  width: 16px;
  height: 16px;
  border-width: 2px;
}

.size-md .spinner {
  width: 24px;
  height: 24px;
  border-width: 3px;
}

.size-lg .spinner {
  width: 40px;
  height: 40px;
  border-width: 4px;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}
</style>
