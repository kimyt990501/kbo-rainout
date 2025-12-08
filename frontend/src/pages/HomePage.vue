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
            <WeatherForm />
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
          />
        </div>
      </div>
    </div>
  </main>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useStadiumStore, usePredictionStore } from '@/store'
import MatchTicket from '@/components/MatchTicket.vue'
import KoreaMapDashboard from '@/components/KoreaMapDashboard.vue'
import StadiumSelector from '@/components/StadiumSelector.vue'
import WeatherForm from '@/components/WeatherForm.vue'
import { getStadiumHomeTeam } from '@/constants/teams'

const stadiumStore = useStadiumStore()
const predictionStore = usePredictionStore()

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
}
</style>
