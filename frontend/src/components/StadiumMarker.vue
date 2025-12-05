<template>
  <div 
    class="stadium-marker"
    :class="[statusClass, { 'is-active': isActive, 'is-raining': isRaining }]"
    @mouseenter="$emit('hover', stadiumId)"
    @mouseleave="$emit('leave')"
    @click="$emit('select', stadiumId)"
    :style="{ left: `${x}%`, top: `${y}%` }"
  >
    <!-- 비 내리는 애니메이션 -->
    <div v-if="isRaining" class="rain-animation">
      <div class="rain-drop" v-for="i in 6" :key="i"></div>
    </div>

    <!-- 마커 핀 -->
    <div class="marker-pin">
      <WeatherIcon :probability="probability" size="sm" />
    </div>

    <!-- 툴팁 -->
    <div class="marker-tooltip" v-show="isActive">
      <div class="tooltip-header">
        <span class="stadium-name">{{ stadiumName }}</span>
        <span class="team-name">{{ teamName }}</span>
      </div>
      <div class="tooltip-body">
        <div class="stat-row">
          <span class="stat-label">취소 가능성</span>
          <span class="stat-value scoreboard" :class="statusClass">{{ probabilityPercent }}%</span>
        </div>
        <div class="stat-row">
          <span class="stat-label">습도</span>
          <span class="stat-value">{{ humidity }}%</span>
        </div>
        <div class="stat-row">
          <span class="stat-label">강수량</span>
          <span class="stat-value">{{ precipitation }}mm</span>
        </div>
      </div>
      <div class="tooltip-footer">
        <span v-if="aiComment" class="ai-comment">{{ aiComment }}</span>
        <span v-else class="ai-comment">클릭하여 상세 예측 보기</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import WeatherIcon from './WeatherIcon.vue'

interface Props {
  stadiumId: string
  stadiumName: string
  teamName: string
  x: number // 지도상 X 좌표 (0-100%)
  y: number // 지도상 Y 좌표 (0-100%)
  probability?: number
  humidity?: number
  precipitation?: number
  aiComment?: string
  isActive?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  probability: 0,
  humidity: 0,
  precipitation: 0,
  isActive: false
})

defineEmits<{
  (e: 'hover', stadiumId: string): void
  (e: 'leave'): void
  (e: 'select', stadiumId: string): void
}>()

const probabilityPercent = computed(() => Math.round(props.probability * 100))

const isRaining = computed(() => props.probability >= 0.5)

const statusClass = computed(() => {
  if (props.probability >= 0.7) return 'status-danger'
  if (props.probability >= 0.5) return 'status-warning'
  return 'status-safe'
})
</script>

<style scoped>
.stadium-marker {
  position: absolute;
  transform: translate(-50%, -100%);
  cursor: pointer;
  z-index: var(--z-base);
  transition: z-index 0s;
}

.stadium-marker:hover,
.stadium-marker.is-active {
  z-index: var(--z-tooltip);
}

/* Marker Pin */
.marker-pin {
  width: 48px;
  height: 48px;
  background: var(--glass-bg-strong);
  backdrop-filter: var(--glass-blur);
  border: 2px solid var(--glass-border);
  border-radius: 50% 50% 50% 0;
  transform: rotate(-45deg);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all var(--transition-base);
  box-shadow: var(--shadow-md);
}

.marker-pin :deep(.weather-icon) {
  transform: rotate(45deg);
}

.stadium-marker:hover .marker-pin,
.is-active .marker-pin {
  transform: rotate(-45deg) scale(1.1);
  box-shadow: var(--shadow-lg);
}

.status-safe .marker-pin {
  border-color: var(--grass-green);
  background: rgba(46, 204, 113, 0.2);
}

.status-warning .marker-pin {
  border-color: var(--clay-brown);
  background: rgba(230, 126, 34, 0.2);
}

.status-danger .marker-pin {
  border-color: var(--danger-red);
  background: rgba(231, 76, 60, 0.2);
}

/* Rain Animation */
.rain-animation {
  position: absolute;
  top: -30px;
  left: 50%;
  transform: translateX(-50%);
  width: 40px;
  height: 40px;
  pointer-events: none;
}

.rain-drop {
  position: absolute;
  width: 2px;
  height: 10px;
  background: var(--sky-blue);
  border-radius: 2px;
  animation: rainFall 0.6s linear infinite;
  opacity: 0.7;
}

.rain-drop:nth-child(1) { left: 5px; animation-delay: 0s; }
.rain-drop:nth-child(2) { left: 12px; animation-delay: 0.1s; }
.rain-drop:nth-child(3) { left: 19px; animation-delay: 0.2s; }
.rain-drop:nth-child(4) { left: 26px; animation-delay: 0.3s; }
.rain-drop:nth-child(5) { left: 33px; animation-delay: 0.15s; }
.rain-drop:nth-child(6) { left: 40px; animation-delay: 0.25s; }

@keyframes rainFall {
  0% {
    transform: translateY(-10px);
    opacity: 0;
  }
  50% {
    opacity: 0.7;
  }
  100% {
    transform: translateY(50px);
    opacity: 0;
  }
}

/* Tooltip */
.marker-tooltip {
  position: absolute;
  bottom: calc(100% + 16px);
  left: 50%;
  transform: translateX(-50%);
  width: 200px;
  background: var(--glass-bg-strong);
  backdrop-filter: var(--glass-blur-strong);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-lg);
  padding: var(--space-3);
  color: var(--white);
  animation: fadeIn var(--transition-fast);
}

.marker-tooltip::after {
  content: '';
  position: absolute;
  top: 100%;
  left: 50%;
  transform: translateX(-50%);
  border: 8px solid transparent;
  border-top-color: var(--glass-border);
}

.tooltip-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-2);
  padding-bottom: var(--space-2);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.stadium-name {
  font-weight: 600;
  font-size: var(--font-size-sm);
}

.team-name {
  font-size: var(--font-size-xs);
  opacity: 0.7;
}

.tooltip-body {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}

.stat-row {
  display: flex;
  justify-content: space-between;
  font-size: var(--font-size-xs);
}

.stat-label {
  opacity: 0.7;
}

.stat-value {
  font-weight: 600;
}

.stat-value.status-safe { color: var(--grass-green); }
.stat-value.status-warning { color: var(--clay-brown); }
.stat-value.status-danger { color: var(--danger-red); }

.tooltip-footer {
  margin-top: var(--space-2);
  padding-top: var(--space-2);
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.ai-comment {
  font-size: var(--font-size-xs);
  font-style: italic;
  opacity: 0.8;
  line-height: 1.4;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateX(-50%) translateY(5px); }
  to { opacity: 1; transform: translateX(-50%) translateY(0); }
}
</style>
