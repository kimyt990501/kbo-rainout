<template>
  <div class="stadium-selector">
    <label class="label">구장 선택</label>
    <select
      v-model="selectedStadium"
      class="select"
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
  margin-bottom: 1.5rem;
}

.label {
  display: block;
  font-size: 0.9rem;
  font-weight: 600;
  color: #374151;
  margin-bottom: 0.5rem;
}

.select {
  width: 100%;
  padding: 0.75rem 1rem;
  font-size: 1rem;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  background-color: white;
  cursor: pointer;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.select:hover:not(:disabled) {
  border-color: #9ca3af;
}

.select:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.select:disabled {
  background-color: #f3f4f6;
  cursor: not-allowed;
}

.error {
  color: #dc2626;
  font-size: 0.85rem;
  margin-top: 0.5rem;
}
</style>
