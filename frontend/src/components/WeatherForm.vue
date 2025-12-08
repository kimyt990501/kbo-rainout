<template>
  <div class="weather-form">
    <!-- 경기 일자/시간 선택 -->
    <GameDateTimeSelector
      :date="gameDate"
      :hour="gameHour"
      :minDate="minDate"
      :maxDate="maxDate"
      @update:date="gameDate = $event"
      @update:hour="gameHour = $event"
    />

    <!-- 날씨 불러오기 버튼 -->
    <button
      @click="fetchWeather"
      :disabled="weatherLoading"
      class="btn btn-secondary fetch-btn"
    >
      <LoadingSpinner v-if="weatherLoading" size="sm" />
      <svg v-else width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M17.5 19H9a7 7 0 1 1 6.71-9h1.79a4.5 4.5 0 1 1 0 9Z"/>
      </svg>
      {{ weatherLoading ? '조회 중...' : '날씨 데이터 불러오기' }}
    </button>

    <!-- 날씨 데이터 표시 -->
    <WeatherDataDisplay :weatherData="weatherData" />

    <!-- 수동 입력 토글 -->
    <div class="manual-toggle">
      <label class="toggle-label">
        <input type="checkbox" v-model="showManualInput" class="toggle-input" />
        <span class="toggle-switch"></span>
        <span class="toggle-text">수동 입력 모드</span>
      </label>
    </div>

    <!-- 수동 입력 폼 -->
    <ManualWeatherInputs
      :show="showManualInput"
      :formData="formData"
      @update:formData="handleFormDataUpdate"
    />

    <!-- 에러 메시지 -->
    <p v-if="weatherError" class="error-msg">{{ weatherError }}</p>
    <p v-if="validationError" class="error-msg">{{ validationError }}</p>
    <p v-if="predictionError" class="error-msg">{{ predictionError }}</p>

    <!-- 예측 버튼 -->
    <button
      @click="handlePredict"
      :disabled="predictionLoading || !canPredict"
      class="btn btn-primary predict-btn"
    >
      <LoadingSpinner v-if="predictionLoading" size="sm" />
      <svg v-else width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/>
      </svg>
      {{ predictionLoading ? '분석 중...' : 'AI 우천취소 예측' }}
    </button>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, reactive, watch } from 'vue'
import { useStadiumStore, usePredictionStore } from '@/store'
import { getWeather } from '@/api/client'
import type { WeatherResponse } from '@/api/types'
import { DEFAULT_GAME_TIME, getTodayDate, getMinDate, getMaxDate } from '@/constants/gameTime'
import { extractErrorMessage, logError } from '@/utils/errors'
import LoadingSpinner from './LoadingSpinner.vue'
import GameDateTimeSelector from './GameDateTimeSelector.vue'
import WeatherDataDisplay from './WeatherDataDisplay.vue'
import ManualWeatherInputs from './ManualWeatherInputs.vue'

const stadiumStore = useStadiumStore()
const predictionStore = usePredictionStore()

const predictionLoading = computed(() => predictionStore.loading)
const predictionError = computed(() => predictionStore.error)

const weatherLoading = ref(false)
const weatherError = ref<string | null>(null)
const weatherData = ref<WeatherResponse | null>(null)
const validationError = ref<string | null>(null)
const showManualInput = ref(false)

// 날짜 범위
const today = new Date()
const todayStr = getTodayDate()
const minDate = computed(() => getMinDate())
const maxDate = computed(() => getMaxDate())

const gameDate = ref(todayStr)
const gameHour = ref(DEFAULT_GAME_TIME)

const formData = reactive({
  daily_precip_sum: 0,
  daily_precip_hours: 0,
  pre_game_precip: 0,
  pre_game_humidity: 60,
  pre_game_temp: 25,
  pre_game_wind: 3,
  prev_day_precip: 0,
  daily_wind_max: 10,
  daily_temp_mean: 24,
  month: today.getMonth() + 1,
  dayofweek: today.getDay() === 0 ? 6 : today.getDay() - 1
})

const canPredict = computed(() => weatherData.value !== null || showManualInput.value)

async function fetchWeather() {
  weatherLoading.value = true
  weatherError.value = null
  try {
    weatherData.value = await getWeather({
      stadium: stadiumStore.currentStadium,
      game_date: gameDate.value,
      game_hour: gameHour.value
    })
    Object.assign(formData, {
      daily_precip_sum: weatherData.value.daily_precip_sum,
      daily_precip_hours: weatherData.value.daily_precip_hours,
      pre_game_precip: weatherData.value.pre_game_precip,
      pre_game_humidity: weatherData.value.pre_game_humidity,
      pre_game_temp: weatherData.value.pre_game_temp,
      pre_game_wind: weatherData.value.pre_game_wind,
      prev_day_precip: weatherData.value.prev_day_precip,
      daily_wind_max: weatherData.value.daily_wind_max,
      daily_temp_mean: weatherData.value.daily_temp_mean,
      month: weatherData.value.month,
      dayofweek: weatherData.value.dayofweek
    })
  } catch (e: unknown) {
    weatherError.value = extractErrorMessage(e, '날씨 데이터를 불러오는데 실패했습니다.')
    logError(e, 'Weather Fetch')
  } finally {
    weatherLoading.value = false
  }
}

function handleFormDataUpdate(field: keyof typeof formData, value: number) {
  formData[field] = value
}

watch(gameDate, (newDate) => {
  if (newDate) {
    const date = new Date(newDate)
    formData.month = date.getMonth() + 1
    const jsDay = date.getDay()
    formData.dayofweek = jsDay === 0 ? 6 : jsDay - 1
  }
})

watch(() => stadiumStore.currentStadium, () => {
  weatherData.value = null
})

function validate(): boolean {
  validationError.value = null
  const data = showManualInput.value ? formData : weatherData.value
  if (!data) {
    validationError.value = '날씨 데이터를 먼저 불러오거나 수동으로 입력해주세요.'
    return false
  }
  if (data.daily_precip_sum < 0) {
    validationError.value = '강수량은 0 이상이어야 합니다.'
    return false
  }
  return true
}

async function handlePredict() {
  if (!validate()) return
  const data = showManualInput.value ? formData : weatherData.value!
  await predictionStore.predict({
    stadium: stadiumStore.currentStadium,
    daily_precip_sum: data.daily_precip_sum,
    daily_precip_hours: data.daily_precip_hours,
    pre_game_precip: data.pre_game_precip,
    pre_game_humidity: data.pre_game_humidity,
    pre_game_temp: data.pre_game_temp,
    pre_game_wind: data.pre_game_wind,
    prev_day_precip: data.prev_day_precip,
    daily_wind_max: data.daily_wind_max,
    daily_temp_mean: data.daily_temp_mean,
    month: data.month,
    dayofweek: data.dayofweek
  })
}
</script>

<style scoped>
.weather-form {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

/* Buttons */
.fetch-btn {
  width: 100%;
  padding: var(--space-3) var(--space-4);
}

.predict-btn {
  width: 100%;
  padding: var(--space-4) var(--space-6);
  font-size: var(--font-size-lg);
  margin-top: var(--space-2);
}

/* Toggle */
.manual-toggle {
  display: flex;
  align-items: center;
}

.toggle-label {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  cursor: pointer;
}

.toggle-input {
  display: none;
}

.toggle-switch {
  width: 40px;
  height: 22px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: var(--radius-full);
  position: relative;
  transition: background var(--transition-fast);
}

.toggle-switch::after {
  content: '';
  position: absolute;
  top: 3px;
  left: 3px;
  width: 16px;
  height: 16px;
  background: var(--white);
  border-radius: 50%;
  transition: transform var(--transition-fast);
}

.toggle-input:checked + .toggle-switch {
  background: var(--grass-green);
}

.toggle-input:checked + .toggle-switch::after {
  transform: translateX(18px);
}

.toggle-text {
  font-size: var(--font-size-sm);
  color: rgba(255, 255, 255, 0.7);
}

/* Error */
.error-msg {
  color: var(--danger-red);
  font-size: var(--font-size-sm);
  margin: 0;
  padding: var(--space-2) var(--space-3);
  background: rgba(231, 76, 60, 0.1);
  border-radius: var(--radius-md);
}
</style>
