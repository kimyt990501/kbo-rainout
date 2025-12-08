<template>
  <div class="weather-form">
    <!-- 경기 일자/시간 -->
    <div class="form-section">
      <div class="form-row">
        <div class="form-group">
          <label class="label">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/>
              <line x1="16" y1="2" x2="16" y2="6"/>
              <line x1="8" y1="2" x2="8" y2="6"/>
              <line x1="3" y1="10" x2="21" y2="10"/>
            </svg>
            경기 날짜
          </label>
          <input
            v-model="gameDate"
            type="date"
            class="input"
            :min="minDate"
            :max="maxDate"
          />
        </div>
        <div class="form-group">
          <label class="label">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10"/>
              <polyline points="12 6 12 12 16 14"/>
            </svg>
            경기 시간
          </label>
          <select v-model="gameHour" class="input">
            <option v-for="option in GAME_TIME_OPTIONS" :key="option.value" :value="option.value">
              {{ option.label }}
            </option>
          </select>
        </div>
      </div>
    </div>

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
    <div v-if="weatherData" class="weather-display animate-fadeIn">
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

    <!-- 수동 입력 토글 -->
    <div class="manual-toggle">
      <label class="toggle-label">
        <input type="checkbox" v-model="showManualInput" class="toggle-input" />
        <span class="toggle-switch"></span>
        <span class="toggle-text">수동 입력 모드</span>
      </label>
    </div>

    <!-- 수동 입력 폼 -->
    <div v-if="showManualInput" class="manual-form animate-fadeIn">
      <div class="form-row">
        <div class="form-group">
          <label class="label">일 강수량 (mm)</label>
          <input v-model.number="formData.daily_precip_sum" type="number" min="0" step="0.1" class="input" />
        </div>
        <div class="form-group">
          <label class="label">강수 시간</label>
          <input v-model.number="formData.daily_precip_hours" type="number" min="0" max="24" step="0.1" class="input" />
        </div>
      </div>
      <div class="form-row">
        <div class="form-group">
          <label class="label">경기 전 3시간 강수 (mm)</label>
          <input v-model.number="formData.pre_game_precip" type="number" min="0" step="0.1" class="input" />
        </div>
        <div class="form-group">
          <label class="label">전날 강수량 (mm)</label>
          <input v-model.number="formData.prev_day_precip" type="number" min="0" step="0.1" class="input" />
        </div>
      </div>
      <div class="form-row">
        <div class="form-group">
          <label class="label">습도 (%)</label>
          <input v-model.number="formData.pre_game_humidity" type="number" min="0" max="100" class="input" />
        </div>
        <div class="form-group">
          <label class="label">기온 (°C)</label>
          <input v-model.number="formData.pre_game_temp" type="number" step="0.1" class="input" />
        </div>
      </div>
      <div class="form-row">
        <div class="form-group">
          <label class="label">풍속 (m/s)</label>
          <input v-model.number="formData.pre_game_wind" type="number" min="0" step="0.1" class="input" />
        </div>
        <div class="form-group">
          <label class="label">최대 풍속 (m/s)</label>
          <input v-model.number="formData.daily_wind_max" type="number" min="0" step="0.1" class="input" />
        </div>
      </div>
    </div>

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
import { GAME_TIME_OPTIONS, DEFAULT_GAME_TIME, getTodayDate, getMinDate, getMaxDate } from '@/constants/gameTime'
import { extractErrorMessage, logError } from '@/utils/errors'
import LoadingSpinner from './LoadingSpinner.vue'

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

/* Form Layout */
.form-section {
  margin-bottom: var(--space-2);
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-3);
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}

.label {
  display: flex;
  align-items: center;
  gap: var(--space-1);
  font-size: var(--font-size-xs);
  font-weight: 500;
  color: rgba(255, 255, 255, 0.8);
}

.label svg {
  opacity: 0.7;
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

/* Spinner */
.spinner {
  width: 18px;
  height: 18px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: currentColor;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Weather Display */
.weather-display {
  background: rgba(46, 204, 113, 0.1);
  border: 1px solid rgba(46, 204, 113, 0.3);
  border-radius: var(--radius-lg);
  padding: var(--space-4);
}

.weather-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-3);
}

.section-title {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  font-size: var(--font-size-sm);
  font-weight: 600;
  color: var(--grass-green);
  margin: 0;
}

.data-badge {
  font-size: var(--font-size-xs);
  font-weight: 500;
  padding: var(--space-1) var(--space-2);
  border-radius: var(--radius-full);
}

.data-badge.forecast {
  background: rgba(52, 152, 219, 0.2);
  color: var(--sky-blue);
}

.data-badge.historical {
  background: rgba(127, 140, 141, 0.2);
  color: var(--storm-gray-light);
}

.weather-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--space-2);
}

.weather-stat {
  text-align: center;
  padding: var(--space-2);
  background: rgba(255, 255, 255, 0.05);
  border-radius: var(--radius-md);
}

.stat-value {
  font-family: var(--font-scoreboard);
  font-size: var(--font-size-xl);
  color: var(--white);
}

.stat-unit {
  font-size: var(--font-size-xs);
  color: rgba(255, 255, 255, 0.6);
  margin-left: 2px;
}

.stat-label {
  display: block;
  font-size: var(--font-size-xs);
  color: rgba(255, 255, 255, 0.5);
  margin-top: var(--space-1);
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

/* Manual Form */
.manual-form {
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: var(--radius-lg);
  padding: var(--space-4);
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
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

/* Mobile */
@media (max-width: 480px) {
  .form-row {
    grid-template-columns: 1fr;
  }
  
  .weather-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
