<template>
  <div class="weather-icon" :class="[weatherClass, sizeClass]">
    <!-- 맑음 (해) -->
    <svg v-if="weatherType === 'sunny'" viewBox="0 0 64 64" fill="none">
      <circle cx="32" cy="32" r="12" fill="#F1C40F"/>
      <g stroke="#F1C40F" stroke-width="3" stroke-linecap="round">
        <line x1="32" y1="6" x2="32" y2="14"/>
        <line x1="32" y1="50" x2="32" y2="58"/>
        <line x1="6" y1="32" x2="14" y2="32"/>
        <line x1="50" y1="32" x2="58" y2="32"/>
        <line x1="13.6" y1="13.6" x2="19.3" y2="19.3"/>
        <line x1="44.7" y1="44.7" x2="50.4" y2="50.4"/>
        <line x1="13.6" y1="50.4" x2="19.3" y2="44.7"/>
        <line x1="44.7" y1="19.3" x2="50.4" y2="13.6"/>
      </g>
    </svg>

    <!-- 흐림 (구름) -->
    <svg v-else-if="weatherType === 'cloudy'" viewBox="0 0 64 64" fill="none">
      <circle cx="24" cy="24" r="8" fill="#F1C40F" opacity="0.6"/>
      <path d="M48 42c5.5 0 10-4.5 10-10s-4.5-10-10-10c-1 0-2 .1-3 .4C43.5 17.5 38.5 14 32.5 14 24.5 14 18 20 17 27.5 11 28 6 33 6 39c0 6.6 5.4 12 12 12h30z" fill="#95A5A6"/>
    </svg>

    <!-- 비 -->
    <svg v-else-if="weatherType === 'rainy'" viewBox="0 0 64 64" fill="none">
      <path d="M48 32c5.5 0 10-4.5 10-10s-4.5-10-10-10c-1 0-2 .1-3 .4C43.5 7.5 38.5 4 32.5 4 24.5 4 18 10 17 17.5 11 18 6 23 6 29c0 6.6 5.4 12 12 12h30z" fill="#7F8C8D"/>
      <g class="rain-drops">
        <line x1="18" y1="44" x2="14" y2="54" stroke="#3498DB" stroke-width="2" stroke-linecap="round"/>
        <line x1="28" y1="44" x2="24" y2="54" stroke="#3498DB" stroke-width="2" stroke-linecap="round"/>
        <line x1="38" y1="44" x2="34" y2="54" stroke="#3498DB" stroke-width="2" stroke-linecap="round"/>
        <line x1="48" y1="44" x2="44" y2="54" stroke="#3498DB" stroke-width="2" stroke-linecap="round"/>
        <line x1="23" y1="52" x2="19" y2="62" stroke="#3498DB" stroke-width="2" stroke-linecap="round"/>
        <line x1="33" y1="52" x2="29" y2="62" stroke="#3498DB" stroke-width="2" stroke-linecap="round"/>
        <line x1="43" y1="52" x2="39" y2="62" stroke="#3498DB" stroke-width="2" stroke-linecap="round"/>
      </g>
    </svg>

    <!-- 폭우 -->
    <svg v-else viewBox="0 0 64 64" fill="none">
      <path d="M48 28c5.5 0 10-4.5 10-10s-4.5-10-10-10c-1 0-2 .1-3 .4C43.5 3.5 38.5 0 32.5 0 24.5 0 18 6 17 13.5 11 14 6 19 6 25c0 6.6 5.4 12 12 12h30z" fill="#5D6D7E"/>
      <g class="rain-drops heavy">
        <line x1="14" y1="40" x2="8" y2="56" stroke="#3498DB" stroke-width="3" stroke-linecap="round"/>
        <line x1="24" y1="40" x2="18" y2="56" stroke="#3498DB" stroke-width="3" stroke-linecap="round"/>
        <line x1="34" y1="40" x2="28" y2="56" stroke="#3498DB" stroke-width="3" stroke-linecap="round"/>
        <line x1="44" y1="40" x2="38" y2="56" stroke="#3498DB" stroke-width="3" stroke-linecap="round"/>
        <line x1="54" y1="40" x2="48" y2="56" stroke="#3498DB" stroke-width="3" stroke-linecap="round"/>
        <line x1="19" y1="50" x2="13" y2="66" stroke="#3498DB" stroke-width="3" stroke-linecap="round"/>
        <line x1="29" y1="50" x2="23" y2="66" stroke="#3498DB" stroke-width="3" stroke-linecap="round"/>
        <line x1="39" y1="50" x2="33" y2="66" stroke="#3498DB" stroke-width="3" stroke-linecap="round"/>
        <line x1="49" y1="50" x2="43" y2="66" stroke="#3498DB" stroke-width="3" stroke-linecap="round"/>
      </g>
    </svg>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { getRainIntensity } from '@/constants/probability'

interface Props {
  probability: number // 취소 확률 (0-1)
  size?: 'sm' | 'md' | 'lg' | 'xl'
}

const props = withDefaults(defineProps<Props>(), {
  size: 'md'
})

const weatherType = computed(() => getRainIntensity(props.probability))

const weatherClass = computed(() => `weather-${weatherType.value}`)
const sizeClass = computed(() => `size-${props.size}`)
</script>

<style scoped>
.weather-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.weather-icon svg {
  width: 100%;
  height: 100%;
}

/* Sizes */
.size-sm { width: 32px; height: 32px; }
.size-md { width: 48px; height: 48px; }
.size-lg { width: 64px; height: 64px; }
.size-xl { width: 96px; height: 96px; }

/* Rain animation */
.rain-drops line {
  animation: rainDrop 0.8s linear infinite;
}

.rain-drops line:nth-child(2) { animation-delay: 0.1s; }
.rain-drops line:nth-child(3) { animation-delay: 0.2s; }
.rain-drops line:nth-child(4) { animation-delay: 0.3s; }
.rain-drops line:nth-child(5) { animation-delay: 0.15s; }
.rain-drops line:nth-child(6) { animation-delay: 0.25s; }
.rain-drops line:nth-child(7) { animation-delay: 0.35s; }
.rain-drops line:nth-child(8) { animation-delay: 0.05s; }
.rain-drops line:nth-child(9) { animation-delay: 0.4s; }

.rain-drops.heavy line {
  animation-duration: 0.5s;
}

@keyframes rainDrop {
  0% {
    opacity: 0;
    transform: translateY(-5px);
  }
  50% {
    opacity: 1;
  }
  100% {
    opacity: 0;
    transform: translateY(5px);
  }
}

/* Weather type colors for glow effects */
.weather-sunny {
  filter: drop-shadow(0 0 10px rgba(241, 196, 15, 0.5));
}

.weather-cloudy {
  filter: drop-shadow(0 0 8px rgba(149, 165, 166, 0.4));
}

.weather-rainy {
  filter: drop-shadow(0 0 8px rgba(52, 152, 219, 0.4));
}

.weather-heavy {
  filter: drop-shadow(0 0 12px rgba(52, 152, 219, 0.6));
}
</style>
