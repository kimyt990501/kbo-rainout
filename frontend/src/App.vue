<template>
  <div class="app" :class="weatherClass">
    <!-- 구장 배경 이미지 -->
    <div class="stadium-background" :style="backgroundStyle"></div>
    <div class="background-overlay"></div>

    <!-- 메인 컨텐츠 -->
    <LayoutHeader />
    <RouterView />
    <LayoutFooter />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { RouterView } from 'vue-router'
import LayoutHeader from '@/components/LayoutHeader.vue'
import LayoutFooter from '@/components/LayoutFooter.vue'
import { usePredictionStore, useStadiumStore } from '@/store'

const predictionStore = usePredictionStore()
const stadiumStore = useStadiumStore()

// 구장별 배경 이미지 (실제로는 이미지 URL 사용)
const stadiumBackgrounds: Record<string, string> = {
  jamsil: 'linear-gradient(135deg, #1a365d 0%, #2d4a7c 50%, #1e3a5f 100%)',
  daegu: 'linear-gradient(135deg, #074CA1 0%, #0a5dc2 50%, #063d81 100%)',
  suwon: 'linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%)',
  incheon: 'linear-gradient(135deg, #8B0000 0%, #a52a2a 50%, #6b0000 100%)',
}

const backgroundStyle = computed(() => {
  const stadium = stadiumStore.currentStadium
  const bg = stadiumBackgrounds[stadium] || stadiumBackgrounds.jamsil
  return { background: bg }
})

// 날씨 상태에 따른 클래스
const weatherClass = computed(() => {
  const prediction = predictionStore.lastPrediction
  if (!prediction) return 'weather-default'
  
  if (prediction.cancellation_probability >= 0.7) return 'weather-rain'
  if (prediction.cancellation_probability >= 0.5) return 'weather-cloudy'
  return 'weather-sunny'
})
</script>

<style scoped>
.app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  position: relative;
  overflow-x: hidden;
}

/* Stadium Background */
.stadium-background {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: -2;
  transition: background var(--transition-slow);
}

.background-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: -1;
  background: radial-gradient(ellipse at center, transparent 0%, rgba(0, 0, 0, 0.3) 100%);
  pointer-events: none;
}

/* Weather-based background effects */
.weather-sunny .stadium-background {
  filter: brightness(1.1) saturate(1.2);
}

.weather-cloudy .stadium-background {
  filter: brightness(0.8) saturate(0.9);
}

.weather-rain .stadium-background {
  filter: brightness(0.6) saturate(0.7);
}

/* Rain overlay for rainy weather */
.weather-rain .background-overlay::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: 
    linear-gradient(to bottom, transparent 40%, rgba(52, 152, 219, 0.1) 100%),
    repeating-linear-gradient(
      100deg,
      transparent,
      transparent 10px,
      rgba(52, 152, 219, 0.03) 10px,
      rgba(52, 152, 219, 0.03) 11px
    );
  animation: rainMove 0.3s linear infinite;
}

@keyframes rainMove {
  0% {
    background-position: 0 0;
  }
  100% {
    background-position: 10px 20px;
  }
}
</style>
