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

          <!-- 빠른 날짜 선택 버튼 -->
          <div class="quick-select-buttons">
            <button
              v-for="option in dateQuickOptions"
              :key="option.value"
              type="button"
              class="quick-btn"
              :class="{ active: isDateActive(option.value) }"
              @click="selectQuickDate(option.value)"
            >
              {{ option.label }}
            </button>
          </div>

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

          <!-- 빠른 시간 선택 버튼 -->
          <div class="quick-select-buttons">
            <button
              v-for="option in GAME_TIME_OPTIONS"
              :key="option.value"
              type="button"
              class="quick-btn"
              :class="{ active: hour === option.value }"
              @click="selectQuickTime(option.value)"
            >
              {{ option.label.replace(' (주간)', '').replace(' (조기)', '').replace(' (야간)', '') }}
            </button>
          </div>

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
import { computed } from 'vue'
import { GAME_TIME_OPTIONS } from '@/constants/gameTime'

interface Props {
  date: string
  hour: number
  minDate: string
  maxDate: string
}

const props = defineProps<Props>()

const emit = defineEmits<{
  (e: 'update:date', value: string): void
  (e: 'update:hour', value: number): void
}>()

// 빠른 날짜 선택 옵션
const dateQuickOptions = computed(() => {
  const today = new Date()
  const tomorrow = new Date(today)
  tomorrow.setDate(tomorrow.getDate() + 1)
  const dayAfter = new Date(today)
  dayAfter.setDate(dayAfter.getDate() + 2)

  return [
    {
      label: '오늘',
      value: today.toISOString().split('T')[0]
    },
    {
      label: '내일',
      value: tomorrow.toISOString().split('T')[0]
    },
    {
      label: '모레',
      value: dayAfter.toISOString().split('T')[0]
    }
  ]
})

// 날짜가 활성화 상태인지 확인
function isDateActive(dateValue: string): boolean {
  return props.date === dateValue
}

// 빠른 날짜 선택
function selectQuickDate(dateValue: string) {
  emit('update:date', dateValue)
}

// 빠른 시간 선택
function selectQuickTime(timeValue: number) {
  emit('update:hour', timeValue)
}
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

/* 빠른 선택 버튼 */
.quick-select-buttons {
  display: flex;
  gap: var(--space-2);
  margin-bottom: var(--space-2);
}

.quick-btn {
  flex: 1;
  padding: var(--space-2) var(--space-3);
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: var(--radius-md);
  color: rgba(255, 255, 255, 0.7);
  font-size: var(--font-size-xs);
  font-weight: 500;
  cursor: pointer;
  transition: all var(--transition-base);
  white-space: nowrap;
}

.quick-btn:hover {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(255, 255, 255, 0.2);
  color: rgba(255, 255, 255, 0.9);
}

.quick-btn.active {
  background: var(--grass-green);
  border-color: var(--grass-green);
  color: var(--white);
  font-weight: 600;
  box-shadow: 0 0 8px rgba(46, 204, 113, 0.3);
}

.quick-btn:active {
  transform: scale(0.98);
}

/* 모바일 최적화 */
@media (max-width: 640px) {
  .form-row {
    grid-template-columns: 1fr;
  }

  .quick-btn {
    font-size: var(--font-size-2xs);
    padding: var(--space-1-5) var(--space-2);
  }
}
</style>
