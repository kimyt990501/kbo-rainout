<template>
  <div v-if="weatherData" class="weather-data-display animate-fadeIn">
    <div class="weather-header">
      <h4 class="section-title">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M17.5 19H9a7 7 0 1 1 6.71-9h1.79a4.5 4.5 0 1 1 0 9Z"/>
        </svg>
        조회된 날씨 정보
      </h4>
      <span :class="['data-badge', weatherData.data_source]">
        {{ weatherData.data_source === 'forecast' ? '예보' : '과거' }}
      </span>
    </div>

    <div class="weather-grid">
      <div class="weather-stat">
        <span class="stat-value">{{ weatherData.daily_precip_sum }}</span>
        <span class="stat-unit">mm</span>
        <span class="stat-label">일 강수량</span>
      </div>
      <div class="weather-stat">
        <span class="stat-value">{{ weatherData.daily_precip_hours }}</span>
        <span class="stat-unit">h</span>
        <span class="stat-label">강수 시간</span>
      </div>
      <div class="weather-stat">
        <span class="stat-value">{{ weatherData.pre_game_humidity }}</span>
        <span class="stat-unit">%</span>
        <span class="stat-label">습도</span>
      </div>
      <div class="weather-stat">
        <span class="stat-value">{{ weatherData.pre_game_temp }}</span>
        <span class="stat-unit">°C</span>
        <span class="stat-label">기온</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { WeatherResponse } from '@/api/types'

interface Props {
  weatherData: WeatherResponse | null
}

defineProps<Props>()
</script>

<style scoped>
.weather-data-display {
  margin-top: var(--space-4);
  padding: var(--space-4);
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: var(--radius-lg);
}

.weather-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-4);
}

.section-title {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  font-size: var(--font-size-base);
  font-weight: 600;
  color: var(--white);
  margin: 0;
}

.section-title svg {
  color: var(--sky-blue);
}

.data-badge {
  padding: var(--space-1) var(--space-3);
  border-radius: var(--radius-full);
  font-size: var(--font-size-xs);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.data-badge.forecast {
  background: rgba(52, 152, 219, 0.2);
  color: var(--sky-blue);
}

.data-badge.historical {
  background: rgba(149, 165, 166, 0.2);
  color: var(--storm-gray);
}

.weather-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: var(--space-3);
}

.weather-stat {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: var(--space-3);
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: var(--radius-md);
  transition: all var(--transition-base);
}

.weather-stat:hover {
  background: rgba(255, 255, 255, 0.05);
  border-color: rgba(255, 255, 255, 0.1);
  transform: translateY(-2px);
}

.stat-value {
  font-family: var(--font-scoreboard);
  font-size: var(--font-size-2xl);
  font-weight: 700;
  color: var(--white);
  line-height: 1;
}

.stat-unit {
  font-size: var(--font-size-sm);
  color: rgba(255, 255, 255, 0.6);
  margin-left: var(--space-1);
}

.stat-label {
  font-size: var(--font-size-xs);
  color: rgba(255, 255, 255, 0.7);
  margin-top: var(--space-2);
}

/* 애니메이션 */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-fadeIn {
  animation: fadeIn 0.3s ease-out;
}

/* 모바일 최적화 */
@media (max-width: 640px) {
  .weather-grid {
    grid-template-columns: 1fr;
  }
}
</style>
