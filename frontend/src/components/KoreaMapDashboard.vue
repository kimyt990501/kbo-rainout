<template>
  <div class="korea-map-dashboard">
    <div class="map-header">
      <h2 class="map-title">🗺️ KBO 날씨 상황실</h2>
      <p class="map-subtitle">전국 구장의 실시간 날씨 상황을 확인하세요</p>
    </div>

    <div class="map-container">
      <!-- 대한민국 상세 지도 (GeoJSON 기반) -->
      <svg class="korea-map" viewBox="0 0 800 900" preserveAspectRatio="xMidYMid meet">
        <defs>
          <filter id="mapShadow" x="-20%" y="-20%" width="140%" height="140%">
            <feDropShadow dx="0" dy="4" stdDeviation="8" flood-opacity="0.25"/>
          </filter>
        </defs>

        <!-- 시도별 경계 -->
        <g v-if="provincesPaths.length > 0">
          <path
            v-for="(province, index) in provincesPaths"
            :key="index"
            :d="province.path"
            class="province-outline"
            :class="getProvinceClass(province.name)"
            :filter="'url(#mapShadow)'"
          />
        </g>

        <!-- 로딩 중 표시 -->
        <text v-else x="400" y="450" text-anchor="middle" fill="rgba(255,255,255,0.5)" font-size="16">
          지도 로딩 중...
        </text>
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
import { ref, computed, onMounted } from 'vue'
import { geoPath, geoMercator } from 'd3-geo'
import StadiumMarker from './StadiumMarker.vue'
import { useStadiumStore, usePredictionStore } from '@/store'

const stadiumStore = useStadiumStore()
const predictionStore = usePredictionStore()

const activeStadium = ref<string | null>(null)
const provincesPaths = ref<Array<{ name: string; path: string }>>([])

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

// GeoJSON 로드 및 SVG path 생성
onMounted(async () => {
  try {
    const response = await fetch('/skorea-provinces.json')
    const geojson = await response.json()

    // Mercator 투영 설정 (대한민국 중심)
    const projection = geoMercator()
      .center([127.5, 36.5])  // 대한민국 중심 경도, 위도
      .scale(8000)            // 스케일 조정
      .translate([400, 450])  // SVG 중심으로 이동

    const pathGenerator = geoPath().projection(projection)

    // 각 시도를 SVG path로 변환
    provincesPaths.value = geojson.features.map((feature: any) => ({
      name: feature.properties.NAME_1 || feature.properties.name || 'Unknown',
      path: pathGenerator(feature) || ''
    }))

    console.log('지도 로딩 완료:', provincesPaths.value.length, '개 시도')
  } catch (error) {
    console.error('지도 로딩 실패:', error)
  }
})

// 시도별 스타일 클래스
function getProvinceClass(name: string): string {
  // 주요 도시는 강조
  const majorCities = ['Seoul', 'Busan', 'Daegu', 'Incheon', 'Gwangju', 'Daejeon', 'Ulsan']
  return majorCities.includes(name) ? 'province-major' : ''
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
  max-width: 600px;
  height: auto;
}

.province-outline {
  fill: rgba(52, 152, 219, 0.2);
  stroke: rgba(255, 255, 255, 0.4);
  stroke-width: 1;
  transition: all var(--transition-base);
  cursor: pointer;
}

.province-outline:hover {
  fill: rgba(46, 204, 113, 0.3);
  stroke: rgba(255, 255, 255, 0.7);
  stroke-width: 1.5;
}

.province-outline.province-major {
  fill: rgba(52, 152, 219, 0.25);
  stroke: rgba(255, 255, 255, 0.5);
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
