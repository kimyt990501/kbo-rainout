<template>
  <div class="rainfall-timeline">
    <div class="timeline-header">
      <h3 class="timeline-title">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M17.5 19H9a7 7 0 1 1 6.71-9h1.79a4.5 4.5 0 1 1 0 9Z"/>
        </svg>
        시간대별 강수량 예측
      </h3>
      <span class="total-precipitation">
        총 누적: <strong>{{ totalPrecipitation }}mm</strong>
      </span>
    </div>

    <div v-if="loading" class="loading-container">
      <LoadingSpinner size="md" />
      <p>타임라인 로딩 중...</p>
    </div>

    <div v-else-if="timeline.length > 0" class="timeline-container">
      <div
        v-for="point in timeline"
        :key="point.hour"
        class="timeline-point"
        :class="{ 'is-game-time': point.is_game_time, 'has-rain': point.precipitation > 0 }"
      >
        <div class="point-time">
          <span class="time-label">{{ point.time_label }}</span>
          <span class="relative-time">{{ point.relative_time }}</span>
        </div>
        <div class="point-bar-container">
          <div
            class="point-bar"
            :style="{ width: getBarWidth(point.precipitation) + '%' }"
          ></div>
          <span class="precipitation-value">{{ point.precipitation }}mm</span>
        </div>
      </div>
    </div>

    <div v-else class="empty-state">
      <p>타임라인 데이터가 없습니다.</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { TimelinePoint } from '@/api/types'
import LoadingSpinner from './LoadingSpinner.vue'

interface Props {
  timeline: TimelinePoint[]
  totalPrecipitation: number
  loading?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  timeline: () => [],
  totalPrecipitation: 0,
  loading: false
})

// 최대 강수량 계산 (바 너비 계산용)
const maxPrecipitation = computed(() => {
  const max = Math.max(...props.timeline.map(p => p.precipitation), 1)
  return max
})

// 바 너비 계산 (백분율)
function getBarWidth(precipitation: number): number {
  if (maxPrecipitation.value === 0) return 0
  return (precipitation / maxPrecipitation.value) * 100
}
</script>

<style scoped>
.rainfall-timeline {
  background: var(--glass-bg);
  backdrop-filter: var(--glass-blur);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-xl);
  padding: var(--space-5);
}

.timeline-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-4);
  padding-bottom: var(--space-3);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.timeline-title {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  font-size: var(--font-size-lg);
  font-weight: 600;
  color: var(--white);
  margin: 0;
}

.timeline-title svg {
  color: var(--grass-green);
}

.total-precipitation {
  font-size: var(--font-size-sm);
  color: rgba(255, 255, 255, 0.7);
}

.total-precipitation strong {
  color: var(--white);
  font-weight: 700;
}

/* Loading State */
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-8) 0;
}

.loading-container p {
  color: var(--storm-gray);
  font-size: var(--font-size-sm);
}

/* Timeline Container */
.timeline-container {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

/* Timeline Point */
.timeline-point {
  display: flex;
  gap: var(--space-3);
  padding: var(--space-3);
  background: rgba(255, 255, 255, 0.03);
  border-radius: var(--radius-md);
  transition: all var(--transition-base);
}

.timeline-point:hover {
  background: rgba(255, 255, 255, 0.05);
}

.timeline-point.is-game-time {
  background: rgba(46, 204, 113, 0.1);
  border: 1px solid var(--grass-green);
}

.timeline-point.has-rain {
  background: rgba(52, 152, 219, 0.05);
}

.point-time {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
  min-width: 120px;
}

.time-label {
  font-size: var(--font-size-base);
  font-weight: 600;
  color: var(--white);
}

.is-game-time .time-label {
  color: var(--grass-green);
}

.relative-time {
  font-size: var(--font-size-xs);
  color: rgba(255, 255, 255, 0.6);
}

/* Bar Container */
.point-bar-container {
  flex: 1;
  display: flex;
  align-items: center;
  gap: var(--space-3);
  position: relative;
}

.point-bar {
  height: 24px;
  background: linear-gradient(90deg, var(--grass-green), var(--clay-brown));
  border-radius: var(--radius-sm);
  transition: width var(--transition-base);
  min-width: 2px;
}

.has-rain .point-bar {
  background: linear-gradient(90deg, #3498db, #2980b9);
  box-shadow: 0 0 8px rgba(52, 152, 219, 0.3);
}

.is-game-time .point-bar {
  background: linear-gradient(90deg, var(--grass-green), var(--grass-green-dark));
  box-shadow: 0 0 12px rgba(46, 204, 113, 0.4);
}

.precipitation-value {
  font-size: var(--font-size-sm);
  font-weight: 600;
  color: var(--white);
  min-width: 50px;
  text-align: right;
}

/* Empty State */
.empty-state {
  text-align: center;
  padding: var(--space-8) 0;
  color: var(--storm-gray);
  font-size: var(--font-size-sm);
}

/* 모바일 최적화 */
@media (max-width: 640px) {
  .timeline-header {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--space-2);
  }

  .timeline-title {
    font-size: var(--font-size-base);
  }

  .point-time {
    min-width: 100px;
  }

  .time-label {
    font-size: var(--font-size-sm);
  }

  .precipitation-value {
    font-size: var(--font-size-xs);
    min-width: 40px;
  }
}
</style>
