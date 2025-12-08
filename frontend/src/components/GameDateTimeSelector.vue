<template>
  <div class="game-datetime-selector">
    <div class="form-section">
      <div class="form-row">
        <div class="form-group">
          <label class="label">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/>
              <line x1="16" y1="2" x2="16" y2="6"/>
              <line x1="8" y1="2" x2="8" y2="6"/>
              <line x1="3" y1="10" x2="21" y2="10"/>
            </svg>
            경기 날짜
          </label>
          <input
            :value="date"
            @input="$emit('update:date', ($event.target as HTMLInputElement).value)"
            type="date"
            class="input"
            :min="minDate"
            :max="maxDate"
          />
        </div>
        <div class="form-group">
          <label class="label">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10"/>
              <polyline points="12 6 12 12 16 14"/>
            </svg>
            경기 시간
          </label>
          <select
            :value="hour"
            @change="$emit('update:hour', Number(($event.target as HTMLSelectElement).value))"
            class="input"
          >
            <option v-for="option in GAME_TIME_OPTIONS" :key="option.value" :value="option.value">
              {{ option.label }}
            </option>
          </select>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { GAME_TIME_OPTIONS } from '@/constants/gameTime'

interface Props {
  date: string
  hour: number
  minDate: string
  maxDate: string
}

defineProps<Props>()

defineEmits<{
  (e: 'update:date', value: string): void
  (e: 'update:hour', value: number): void
}>()
</script>

<style scoped>
.game-datetime-selector {
  width: 100%;
}

.form-section {
  margin-bottom: var(--space-4);
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-4);
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.label {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  font-size: var(--font-size-sm);
  font-weight: 500;
  color: rgba(255, 255, 255, 0.9);
}

.label svg {
  color: var(--grass-green);
}

.input {
  width: 100%;
  padding: var(--space-3);
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: var(--radius-md);
  color: var(--white);
  font-size: var(--font-size-sm);
  transition: all var(--transition-base);
}

.input:hover {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(255, 255, 255, 0.2);
}

.input:focus {
  outline: none;
  background: rgba(255, 255, 255, 0.1);
  border-color: var(--grass-green);
  box-shadow: 0 0 0 3px rgba(46, 204, 113, 0.1);
}

select.input {
  cursor: pointer;
}

/* 모바일 최적화 */
@media (max-width: 640px) {
  .form-row {
    grid-template-columns: 1fr;
  }
}
</style>
