<template>
  <div class="stadium-selector">
    <label class="label">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/>
        <circle cx="12" cy="10" r="3"/>
      </svg>
      구장 선택
    </label>
    <div class="select-wrapper">
      <select
        v-model="selectedStadium"
        class="select input"
        :disabled="loading"
      >
        <option
          v-for="stadium in stadiumList"
          :key="stadium.id"
          :value="stadium.id"
          :disabled="!stadium.available"
        >
          {{ stadium.name }} ({{ stadium.team }})
          {{ !stadium.available ? '- 준비 중' : '' }}
        </option>
      </select>
    </div>
    <p v-if="error" class="error">{{ error }}</p>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useStadiumStore } from '@/store'

const stadiumStore = useStadiumStore()

const stadiumList = computed(() => stadiumStore.stadiumList)
const loading = computed(() => stadiumStore.loading)
const error = computed(() => stadiumStore.error)

const selectedStadium = computed({
  get: () => stadiumStore.currentStadium,
  set: (value: string) => stadiumStore.setStadium(value)
})

onMounted(() => {
  stadiumStore.fetchStadiums()
  stadiumStore.fetchModelInfo()
})
</script>

<style scoped>
.stadium-selector {
  margin-bottom: var(--space-6);
}

.label {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  font-size: var(--font-size-sm);
  font-weight: 600;
  color: rgba(255, 255, 255, 0.9);
  margin-bottom: var(--space-2);
}

.label svg {
  color: var(--clay-brown);
}

.select-wrapper {
  position: relative;
}

.select {
  width: 100%;
  padding: var(--space-3) var(--space-4);
  padding-right: var(--space-10);
  font-size: var(--font-size-base);
  color: var(--white);
  background: rgba(255, 255, 255, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: var(--radius-lg);
  cursor: pointer;
  transition: all var(--transition-fast);
  appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='white' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='6 9 12 15 18 9'%3E%3C/polyline%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right var(--space-3) center;
}

.select:hover:not(:disabled) {
  border-color: rgba(255, 255, 255, 0.4);
  background-color: rgba(255, 255, 255, 0.15);
}

.select:focus {
  outline: none;
  border-color: var(--grass-green);
  box-shadow: 0 0 0 3px rgba(46, 204, 113, 0.2);
}

.select:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.select option {
  background: var(--night-black);
  color: var(--white);
  padding: var(--space-2);
}

.error {
  color: var(--danger-red);
  font-size: var(--font-size-sm);
  margin-top: var(--space-2);
  padding: var(--space-2) var(--space-3);
  background: rgba(231, 76, 60, 0.1);
  border-radius: var(--radius-md);
}
</style>
