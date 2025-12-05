<template>
  <div class="korea-map-dashboard">
    <div class="map-header">
      <h2 class="map-title">🗺️ KBO 날씨 상황실</h2>
      <p class="map-subtitle">전국 구장의 실시간 날씨 상황을 확인하세요</p>
    </div>

    <div class="map-container">
      <!-- 대한민국 간소화 SVG 지도 -->
      <svg class="korea-map" viewBox="0 0 400 500" preserveAspectRatio="xMidYMid meet">
        <defs>
          <!-- 그라데이션 -->
          <linearGradient id="mapGradient" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" style="stop-color:#3498DB;stop-opacity:0.3" />
            <stop offset="100%" style="stop-color:#2ECC71;stop-opacity:0.2" />
          </linearGradient>
          <!-- 그림자 -->
          <filter id="mapShadow" x="-20%" y="-20%" width="140%" height="140%">
            <feDropShadow dx="0" dy="4" stdDeviation="8" flood-opacity="0.3"/>
          </filter>
        </defs>

        <!-- 한반도 윤곽 (간소화) -->
        <path
          class="korea-outline"
          d="M200 20 
             C230 30, 280 50, 320 80
             C350 110, 370 150, 375 200
             C380 250, 370 300, 350 350
             C330 400, 280 440, 230 470
             C200 485, 170 485, 140 470
             C90 440, 50 400, 35 350
             C20 300, 25 250, 40 200
             C55 150, 90 110, 130 80
             C170 50, 180 30, 200 20Z"
          fill="url(#mapGradient)"
          stroke="rgba(255,255,255,0.3)"
          stroke-width="2"
          filter="url(#mapShadow)"
        />

        <!-- 주요 도시/지역 표시 (반투명 원) -->
        <circle cx="200" cy="100" r="25" fill="rgba(255,255,255,0.1)" /> <!-- 서울 -->
        <circle cx="320" cy="280" r="20" fill="rgba(255,255,255,0.1)" /> <!-- 대구 -->
        <circle cx="350" cy="380" r="20" fill="rgba(255,255,255,0.1)" /> <!-- 부산 -->
        <circle cx="120" cy="350" r="18" fill="rgba(255,255,255,0.1)" /> <!-- 광주 -->
        <circle cx="200" cy="250" r="18" fill="rgba(255,255,255,0.1)" /> <!-- 대전 -->
      </svg>

      <!-- 구장 마커들 -->
      <StadiumMarker
        v-for="stadium in stadiumsWithPosition"
        :key="stadium.id"
        v-bind="stadium"
        :isActive="activeStadium === stadium.id"
        @hover="activeStadium = $event"
        @leave="activeStadium = null"
        @select="handleSelectStadium"
      />
    </div>

    <!-- 범례 -->
    <div class="map-legend">
      <div class="legend-item">
        <span class="legend-dot safe"></span>
        <span>경기 진행 예상</span>
      </div>
      <div class="legend-item">
        <span class="legend-dot warning"></span>
        <span>주의 필요</span>
      </div>
      <div class="legend-item">
        <span class="legend-dot danger"></span>
        <span>취소 가능성 높음</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import StadiumMarker from './StadiumMarker.vue'
import { useStadiumStore, usePredictionStore } from '@/store'

const stadiumStore = useStadiumStore()
const predictionStore = usePredictionStore()

const activeStadium = ref<string | null>(null)

const emit = defineEmits<{
  (e: 'select-stadium', stadiumId: string): void
}>()

// 구장별 지도 좌표 (% 기준)
const stadiumPositions: Record<string, { x: number; y: number }> = {
  jamsil: { x: 52, y: 22 },      // 서울 잠실
  incheon: { x: 38, y: 24 },     // 인천
  suwon: { x: 48, y: 30 },       // 수원
  daegu: { x: 72, y: 52 },       // 대구
  sajik: { x: 80, y: 70 },       // 부산 사직
  gwangju: { x: 32, y: 68 },     // 광주
  daejeon: { x: 48, y: 48 },     // 대전
  changwon: { x: 75, y: 65 },    // 창원
  gocheok: { x: 45, y: 22 },     // 고척
}

// 구장 목록에 좌표 및 예측 데이터 추가
const stadiumsWithPosition = computed(() => {
  return stadiumStore.stadiumList
    .filter(s => s.available)
    .map(stadium => {
      const pos = stadiumPositions[stadium.id] || { x: 50, y: 50 }
      const prediction = predictionStore.lastPrediction?.stadium === stadium.id 
        ? predictionStore.lastPrediction 
        : null
      
      return {
        stadiumId: stadium.id,
        stadiumName: stadium.name,
        teamName: stadium.team,
        x: pos.x,
        y: pos.y,
        probability: prediction?.cancellation_probability || 0,
        humidity: 0, // 실제 API에서 가져올 수 있음
        precipitation: 0,
        aiComment: prediction?.prediction || ''
      }
    })
})

function handleSelectStadium(stadiumId: string) {
  stadiumStore.setStadium(stadiumId)
  emit('select-stadium', stadiumId)
}
</script>

<style scoped>
.korea-map-dashboard {
  background: var(--glass-bg);
  backdrop-filter: var(--glass-blur);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-2xl);
  padding: var(--space-6);
  height: 100%;
  display: flex;
  flex-direction: column;
}

.map-header {
  text-align: center;
  margin-bottom: var(--space-4);
}

.map-title {
  font-size: var(--font-size-xl);
  font-weight: 700;
  color: var(--white);
  margin: 0 0 var(--space-1) 0;
}

.map-subtitle {
  font-size: var(--font-size-sm);
  color: rgba(255, 255, 255, 0.7);
  margin: 0;
}

.map-container {
  position: relative;
  flex: 1;
  min-height: 400px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.korea-map {
  width: 100%;
  max-width: 400px;
  height: auto;
}

.korea-outline {
  transition: all var(--transition-base);
}

.map-legend {
  display: flex;
  justify-content: center;
  gap: var(--space-6);
  margin-top: var(--space-4);
  padding-top: var(--space-4);
  border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.legend-item {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  font-size: var(--font-size-xs);
  color: rgba(255, 255, 255, 0.8);
}

.legend-dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
}

.legend-dot.safe {
  background: var(--grass-green);
  box-shadow: 0 0 8px rgba(46, 204, 113, 0.5);
}

.legend-dot.warning {
  background: var(--clay-brown);
  box-shadow: 0 0 8px rgba(230, 126, 34, 0.5);
}

.legend-dot.danger {
  background: var(--danger-red);
  box-shadow: 0 0 8px rgba(231, 76, 60, 0.5);
}
</style>
