<template>
  <main class="home-page">
    <div class="container">
      <!-- 모바일: 티켓 카드 + 입력폼 세로 배열 -->
      <!-- 데스크탑: 지도 대시보드 + 사이드 패널 -->
      <div class="layout">
        <!-- 좌측/상단: 지도 대시보드 (데스크탑) 또는 티켓 카드 (모바일) -->
        <div class="main-panel">
          <!-- 티켓 카드 (모바일 & 결과 표시용) -->
          <div class="ticket-section">
            <MatchTicket
              :homeTeam="homeTeam"
              :awayTeam="awayTeam"
              :stadiumName="stadiumName"
              :gameTime="gameTime"
              :probability="probability"
              :confidence="confidence"
              :predictionText="predictionText"
              :loading="loading"
            />
          </div>

          <!-- 지도 대시보드 (데스크탑 전용) -->
          <div class="map-section">
            <KoreaMapDashboard @select-stadium="handleStadiumFromMap" />
          </div>
        </div>

        <!-- 우측/하단: 입력 폼 -->
        <div class="side-panel">
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

const stadiumStore = useStadiumStore()
const predictionStore = usePredictionStore()

// 팀 정보 매핑
const teamMapping: Record<string, { home: { id: string; name: string }; away: { id: string; name: string } }> = {
  jamsil: { home: { id: 'lg', name: 'LG' }, away: { id: 'doosan', name: '두산' } },
  daegu: { home: { id: 'samsung', name: '삼성' }, away: { id: 'kia', name: 'KIA' } },
  suwon: { home: { id: 'kt', name: 'KT' }, away: { id: 'nc', name: 'NC' } },
  incheon: { home: { id: 'ssg', name: 'SSG' }, away: { id: 'lotte', name: '롯데' } },
}

const homeTeam = computed(() => {
  const mapping = teamMapping[stadiumStore.currentStadium]
  return mapping?.home || { id: 'lg', name: 'LG' }
})

const awayTeam = computed(() => {
  const mapping = teamMapping[stadiumStore.currentStadium]
  return mapping?.away || { id: 'doosan', name: '두산' }
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
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 var(--space-4);
}

/* 레이아웃 */
.layout {
  display: grid;
  gap: var(--space-6);
}

/* 데스크탑: 2컬럼 레이아웃 */
@media (min-width: 1024px) {
  .layout {
    grid-template-columns: 1fr 400px;
    align-items: start;
  }
}

/* 메인 패널 */
.main-panel {
  display: flex;
  flex-direction: column;
  gap: var(--space-6);
}

/* 티켓 섹션 */
.ticket-section {
  display: block;
}

/* 지도 섹션 - 데스크탑에서만 표시 */
.map-section {
  display: none;
}

@media (min-width: 1024px) {
  .map-section {
    display: block;
  }
  
  /* 데스크탑에서는 티켓을 작게 표시 */
  .ticket-section {
    position: sticky;
    top: 100px;
  }
}

/* 사이드 패널 */
.side-panel {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.panel-card {
  padding: var(--space-6);
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

/* 모바일 최적화 */
@media (max-width: 640px) {
  .home-page {
    padding: var(--space-4) 0;
  }
  
  .panel-card {
    padding: var(--space-4);
  }
  
  .panel-title {
    font-size: var(--font-size-base);
    margin-bottom: var(--space-4);
  }
}
</style>
