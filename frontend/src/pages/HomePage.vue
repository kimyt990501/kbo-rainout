<template>
  <main class="home-page">
    <div class="container">
      <!-- 3컬럼 레이아웃: 입력폼 | 지도 | 예측 결과 -->
      <div class="layout">
        <!-- 좌측: 입력 폼 -->
        <div class="input-panel">
          <div class="panel-card glass-strong">
            <h3 class="panel-title">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M6.34 17.66l-1.41 1.41M19.07 4.93l-1.41 1.41"/>
                <circle cx="12" cy="12" r="4"/>
              </svg>
              경기 정보 입력
            </h3>
            <StadiumSelector />
            <WeatherForm @prediction-complete="handlePredictionComplete" />
          </div>
        </div>

        <!-- 중앙: 지도 대시보드 -->
        <div class="map-panel">
          <KoreaMapDashboard @select-stadium="handleStadiumFromMap" />
        </div>

        <!-- 우측: 예측 결과 (티켓 카드) -->
        <div class="result-panel">
          <MatchTicket
            :homeTeam="homeTeam"
            :stadiumName="stadiumName"
            :gameTime="gameTime"
            :probability="probability"
            :confidence="confidence"
            :predictionText="predictionText"
            :loading="loading"
            :showTimelineButton="!!timelineData"
            @scroll-to-timeline="scrollToTimeline"
          />
        </div>
      </div>

      <!-- 스크롤 인디케이터 -->
      <div v-if="timelineData && showScrollIndicator" class="scroll-indicator" @click="scrollToTimeline">
        <div class="scroll-content">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
            <path d="M17.5 19H9a7 7 0 1 1 6.71-9h1.79a4.5 4.5 0 1 1 0 9Z"/>
          </svg>
          <span class="scroll-text">시간대별 강수량 보기</span>
        </div>
        <svg class="scroll-arrow" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
          <polyline points="6 9 12 15 18 9"/>
        </svg>
      </div>

      <!-- 타임라인 (전체 폭) -->
      <div v-if="timelineData" ref="timelineRef" class="timeline-wrapper">
        <RainfallTimeline
          :timeline="timelineData.timeline"
          :total-precipitation="timelineData.total_precipitation"
          :loading="timelineLoading"
        />
      </div>
    </div>
  </main>
</template>

<script setup lang="ts">
import { computed, ref, onMounted, onUnmounted } from 'vue'
import { useStadiumStore, usePredictionStore } from '@/store'
import MatchTicket from '@/components/MatchTicket.vue'
import KoreaMapDashboard from '@/components/KoreaMapDashboard.vue'
import StadiumSelector from '@/components/StadiumSelector.vue'
import WeatherForm from '@/components/WeatherForm.vue'
import RainfallTimeline from '@/components/RainfallTimeline.vue'
import { getStadiumHomeTeam } from '@/constants/teams'
import { getWeatherTimeline } from '@/api/client'
import type { WeatherTimelineResponse } from '@/api/types'

const stadiumStore = useStadiumStore()
const predictionStore = usePredictionStore()

// 타임라인 state
const timelineData = ref<WeatherTimelineResponse | null>(null)
const timelineLoading = ref(false)
const timelineRef = ref<HTMLElement | null>(null)
const showScrollIndicator = ref(true)

// 스크롤 인디케이터 표시 여부 (타임라인이 화면에 보이면 숨김)
function handleScroll() {
  if (!timelineRef.value) return

  const rect = timelineRef.value.getBoundingClientRect()
  const isVisible = rect.top < window.innerHeight && rect.bottom >= 0

  showScrollIndicator.value = !isVisible
}

// 타임라인으로 스크롤
function scrollToTimeline() {
  if (!timelineRef.value) return

  timelineRef.value.scrollIntoView({
    behavior: 'smooth',
    block: 'start'
  })
}

// 예측 완료 후 타임라인 조회
async function handlePredictionComplete(data: { gameDate: string; gameHour: number }) {
  timelineLoading.value = true
  showScrollIndicator.value = true

  try {
    const response = await getWeatherTimeline({
      stadium: stadiumStore.currentStadium,
      game_date: data.gameDate,
      game_hour: data.gameHour,
      hours_before: 3,
      hours_after: 3
    })
    timelineData.value = response
  } catch (error) {
    console.error('타임라인 조회 실패:', error)
    timelineData.value = null
  } finally {
    timelineLoading.value = false
  }
}

// 스크롤 이벤트 리스너
onMounted(() => {
  window.addEventListener('scroll', handleScroll)
})

onUnmounted(() => {
  window.removeEventListener('scroll', handleScroll)
})

const homeTeam = computed(() => {
  return getStadiumHomeTeam(stadiumStore.currentStadium) || { id: 'lg', name: 'LG 트윈스' }
})

const stadiumName = computed(() => 
  stadiumStore.currentStadiumInfo?.name || '잠실야구장'
)

const gameTime = computed(() => '18:30')

const loading = computed(() => predictionStore.loading)

const probability = computed(() => 
  predictionStore.lastPrediction?.cancellation_probability || 0
)

const confidence = computed(() => 
  predictionStore.lastPrediction?.confidence || 'low'
)

const predictionText = computed(() => 
  predictionStore.lastPrediction?.prediction || ''
)

function handleStadiumFromMap(stadiumId: string) {
  stadiumStore.setStadium(stadiumId)
}
</script>

<style scoped>
.home-page {
  flex: 1;
  padding: var(--space-6) 0;
}

.container {
  max-width: 1600px;
  margin: 0 auto;
  padding: 0 var(--space-4);
}

/* 기본 레이아웃 (모바일: 세로 배치) */
.layout {
  display: grid;
  gap: var(--space-4);
  grid-template-columns: 1fr;
  grid-template-areas:
    "input"
    "result"
    "map";
}

.input-panel {
  grid-area: input;
}

.map-panel {
  grid-area: map;
}

.result-panel {
  grid-area: result;
}

/* 태블릿: 2컬럼 레이아웃 (입력+결과 / 지도) */
@media (min-width: 768px) {
  .layout {
    gap: var(--space-5);
    grid-template-columns: 1fr 1fr;
    grid-template-areas:
      "input result"
      "map map";
  }
}

/* 데스크탑: 3컬럼 레이아웃 (입력 | 지도 | 결과) */
@media (min-width: 1200px) {
  .layout {
    gap: var(--space-6);
    grid-template-columns: 380px 1fr 380px;
    grid-template-areas: "input map result";
    align-items: start;
  }

  /* 스크롤 시 입력폼과 결과 고정 */
  .input-panel,
  .result-panel {
    position: sticky;
    top: calc(var(--header-height, 80px) + var(--space-4));
    max-height: calc(100vh - var(--header-height, 80px) - var(--space-8));
    overflow-y: auto;
  }

  /* 스크롤바 스타일링 */
  .input-panel::-webkit-scrollbar,
  .result-panel::-webkit-scrollbar {
    width: 6px;
  }

  .input-panel::-webkit-scrollbar-track,
  .result-panel::-webkit-scrollbar-track {
    background: rgba(255, 255, 255, 0.05);
    border-radius: 3px;
  }

  .input-panel::-webkit-scrollbar-thumb,
  .result-panel::-webkit-scrollbar-thumb {
    background: rgba(255, 255, 255, 0.2);
    border-radius: 3px;
  }

  .input-panel::-webkit-scrollbar-thumb:hover,
  .result-panel::-webkit-scrollbar-thumb:hover {
    background: rgba(255, 255, 255, 0.3);
  }
}

/* 초대형 화면: 컬럼 너비 증가 */
@media (min-width: 1600px) {
  .layout {
    grid-template-columns: 420px 1fr 420px;
  }
}

/* 패널 카드 스타일 */
.panel-card {
  padding: var(--space-6);
  height: 100%;
}

.panel-title {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  font-size: var(--font-size-lg);
  font-weight: 600;
  color: var(--white);
  margin: 0 0 var(--space-6) 0;
}

.panel-title svg {
  color: var(--grass-green);
}

/* 지도 패널 */
.map-panel {
  min-height: 500px;
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

@media (min-width: 1200px) {
  .map-panel {
    min-height: 700px;
  }
}

/* 결과 패널 */
.result-panel {
  display: flex;
  flex-direction: column;
}

/* 스크롤 인디케이터 */
.scroll-indicator {
  position: fixed;
  bottom: var(--space-8);
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-3);
  padding: var(--space-3) var(--space-4);
  min-width: 220px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(12px);
  border-radius: var(--radius-xl);
  border: 1px solid rgba(255, 255, 255, 0.3);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12),
              0 2px 8px rgba(0, 0, 0, 0.08);
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  z-index: 100;
  animation: slideUpFade 0.5s ease-out;
}

.scroll-indicator:hover {
  transform: translateX(-50%) translateY(-6px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.16),
              0 4px 12px rgba(0, 0, 0, 0.12);
  background: rgba(255, 255, 255, 1);
}

.scroll-indicator:active {
  transform: translateX(-50%) translateY(-2px);
}

.scroll-content {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  flex: 1;
}

.scroll-content svg {
  color: #3498db;
  flex-shrink: 0;
}

.scroll-text {
  font-size: var(--font-size-sm);
  font-weight: 600;
  color: var(--night-black);
  white-space: nowrap;
  letter-spacing: -0.01em;
}

.scroll-arrow {
  color: #3498db;
  flex-shrink: 0;
  animation: bounceArrow 2s ease-in-out infinite;
}

@keyframes slideUpFade {
  0% {
    opacity: 0;
    transform: translateX(-50%) translateY(30px);
  }
  100% {
    opacity: 1;
    transform: translateX(-50%) translateY(0);
  }
}

@keyframes bounceArrow {
  0%, 20%, 50%, 80%, 100% {
    transform: translateY(0);
  }
  40% {
    transform: translateY(-4px);
  }
  60% {
    transform: translateY(-2px);
  }
}

/* 타임라인 래퍼 (전체 폭) */
.timeline-wrapper {
  margin-top: var(--space-6);
  animation: slideInUp 0.5s ease-out;
  scroll-margin-top: var(--space-6);
}

@keyframes slideInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 데스크탑에서 타임라인 여백 조정 */
@media (min-width: 1200px) {
  .timeline-wrapper {
    margin-top: var(--space-8);
    scroll-margin-top: var(--space-8);
  }
}

/* 모바일 최적화 */
@media (max-width: 640px) {
  .home-page {
    padding: var(--space-4) 0;
  }

  .layout {
    gap: var(--space-3);
  }

  .panel-card {
    padding: var(--space-4);
  }

  .panel-title {
    font-size: var(--font-size-base);
    margin-bottom: var(--space-4);
  }

  .map-panel {
    min-height: 400px;
  }

  .timeline-wrapper {
    margin-top: var(--space-4);
  }

  .scroll-indicator {
    bottom: var(--space-5);
    padding: var(--space-2) var(--space-3);
    min-width: 200px;
    gap: var(--space-2);
  }

  .scroll-text {
    font-size: var(--font-size-xs);
  }

  .scroll-content svg {
    width: 16px;
    height: 16px;
  }

  .scroll-arrow {
    width: 14px;
    height: 14px;
  }
}
</style>
