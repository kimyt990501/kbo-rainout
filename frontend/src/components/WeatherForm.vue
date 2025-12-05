<template>
  <div class="weather-form">
    <h3 class="form-title">경기 정보</h3>

    <!-- 경기 일자/시간 -->
    <div class="form-row">
      <div class="form-group">
        <label class="label">경기 날짜</label>
        <input
          v-model="gameDate"
          type="date"
          class="input"
          :min="minDate"
          :max="maxDate"
        />
      </div>
      <div class="form-group">
        <label class="label">경기 시간</label>
        <select v-model="gameHour" class="input">
          <option :value="14">14:00 (주간)</option>
          <option :value="17">17:00 (조기)</option>
          <option :value="18">18:30 (야간)</option>
        </select>
      </div>
    </div>

    <!-- 날씨 불러오기 버튼 -->
    <button
      @click="fetchWeather"
      :disabled="weatherLoading"
      class="fetch-btn"
    >
      <span v-if="weatherLoading" class="spinner"></span>
      {{ weatherLoading ? '날씨 조회 중...' : '날씨 데이터 불러오기' }}
    </button>

    <!-- 날씨 데이터 표시 영역 -->
    <div v-if="weatherData" class="weather-data">
      <div class="weather-header">
        <h4 class="section-title">조회된 날씨 정보</h4>
        <span :class="['data-source', weatherData.data_source]">
          {{ weatherData.data_source === 'forecast' ? '예보' : '과거 데이터' }}
        </span>
      </div>

      <div class="weather-grid">
        <div class="weather-item">
          <span class="weather-label">일 강수량</span>
          <span class="weather-value">{{ weatherData.daily_precip_sum }} mm</span>
        </div>
        <div class="weather-item">
          <span class="weather-label">강수 시간</span>
          <span class="weather-value">{{ weatherData.daily_precip_hours }} 시간</span>
        </div>
        <div class="weather-item">
          <span class="weather-label">경기 전 3시간 강수</span>
          <span class="weather-value">{{ weatherData.pre_game_precip }} mm</span>
        </div>
        <div class="weather-item">
          <span class="weather-label">전날 강수량</span>
          <span class="weather-value">{{ weatherData.prev_day_precip }} mm</span>
        </div>
        <div class="weather-item">
          <span class="weather-label">습도</span>
          <span class="weather-value">{{ weatherData.pre_game_humidity }}%</span>
        </div>
        <div class="weather-item">
          <span class="weather-label">기온</span>
          <span class="weather-value">{{ weatherData.pre_game_temp }}°C</span>
        </div>
        <div class="weather-item">
          <span class="weather-label">풍속</span>
          <span class="weather-value">{{ weatherData.pre_game_wind }} m/s</span>
        </div>
        <div class="weather-item">
          <span class="weather-label">최대 풍속</span>
          <span class="weather-value">{{ weatherData.daily_wind_max }} m/s</span>
        </div>
      </div>
    </div>

    <!-- 수동 입력 토글 -->
    <div class="manual-toggle">
      <label class="toggle-label">
        <input type="checkbox" v-model="showManualInput" />
        <span>수동으로 날씨 데이터 입력하기</span>
      </label>
    </div>

    <!-- 수동 입력 폼 (숨김 가능) -->
    <div v-if="showManualInput" class="manual-form">
      <h4 class="section-title">날씨 정보 직접 입력</h4>

      <div class="form-row">
        <div class="form-group">
          <label class="label">일 강수량 (mm)</label>
          <input
            v-model.number="formData.daily_precip_sum"
            type="number"
            min="0"
            step="0.1"
            class="input"
          />
        </div>
        <div class="form-group">
          <label class="label">강수 시간</label>
          <input
            v-model.number="formData.daily_precip_hours"
            type="number"
            min="0"
            max="24"
            step="0.1"
            class="input"
          />
        </div>
      </div>

      <div class="form-row">
        <div class="form-group">
          <label class="label">경기 전 3시간 강수량 (mm)</label>
          <input
            v-model.number="formData.pre_game_precip"
            type="number"
            min="0"
            step="0.1"
            class="input"
          />
        </div>
        <div class="form-group">
          <label class="label">전날 강수량 (mm)</label>
          <input
            v-model.number="formData.prev_day_precip"
            type="number"
            min="0"
            step="0.1"
            class="input"
          />
        </div>
      </div>

      <div class="form-row">
        <div class="form-group">
          <label class="label">습도 (%)</label>
          <input
            v-model.number="formData.pre_game_humidity"
            type="number"
            min="0"
            max="100"
            step="1"
            class="input"
          />
        </div>
        <div class="form-group">
          <label class="label">기온 (°C)</label>
          <input
            v-model.number="formData.pre_game_temp"
            type="number"
            step="0.1"
            class="input"
          />
        </div>
      </div>

      <div class="form-row">
        <div class="form-group">
          <label class="label">풍속 (m/s)</label>
          <input
            v-model.number="formData.pre_game_wind"
            type="number"
            min="0"
            step="0.1"
            class="input"
          />
        </div>
        <div class="form-group">
          <label class="label">최대 풍속 (m/s)</label>
          <input
            v-model.number="formData.daily_wind_max"
            type="number"
            min="0"
            step="0.1"
            class="input"
          />
        </div>
      </div>

      <div class="form-row">
        <div class="form-group full-width">
          <label class="label">평균 기온 (°C)</label>
          <input
            v-model.number="formData.daily_temp_mean"
            type="number"
            step="0.1"
            class="input"
          />
        </div>
      </div>
    </div>

    <!-- 에러 메시지 -->
    <p v-if="weatherError" class="error">{{ weatherError }}</p>
    <p v-if="validationError" class="error">{{ validationError }}</p>
    <p v-if="predictionError" class="error">{{ predictionError }}</p>

    <!-- 예측 버튼 -->
    <button
      @click="handlePredict"
      :disabled="predictionLoading || !canPredict"
      class="predict-btn"
    >
      <span v-if="predictionLoading" class="spinner"></span>
      {{ predictionLoading ? '예측 중...' : '우천취소 예측하기' }}
    </button>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, reactive, watch } from 'vue'
import { useStadiumStore, usePredictionStore } from '@/store'
import { getWeather } from '@/api/client'
import type { WeatherResponse } from '@/api/types'

const stadiumStore = useStadiumStore()
const predictionStore = usePredictionStore()

const predictionLoading = computed(() => predictionStore.loading)
const predictionError = computed(() => predictionStore.error)

const weatherLoading = ref(false)
const weatherError = ref<string | null>(null)
const weatherData = ref<WeatherResponse | null>(null)
const validationError = ref<string | null>(null)
const showManualInput = ref(false)

// 날짜 범위 계산
const today = new Date()
const todayStr = today.toISOString().split('T')[0]
const minDate = computed(() => {
  const d = new Date()
  d.setFullYear(d.getFullYear() - 5)
  return d.toISOString().split('T')[0]
})
const maxDate = computed(() => {
  const d = new Date()
  d.setDate(d.getDate() + 14) // 예보는 최대 14일
  return d.toISOString().split('T')[0]
})

// 경기 정보
const gameDate = ref(todayStr)
const gameHour = ref(18)

// 수동 입력 폼 데이터
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

// 날씨 데이터가 있거나 수동 입력 모드일 때 예측 가능
const canPredict = computed(() => {
  return weatherData.value !== null || showManualInput.value
})

// 날씨 데이터 불러오기
async function fetchWeather() {
  weatherLoading.value = true
  weatherError.value = null

  try {
    weatherData.value = await getWeather({
      stadium: stadiumStore.currentStadium,
      game_date: gameDate.value,
      game_hour: gameHour.value
    })

    // 수동 입력 폼에도 데이터 동기화
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
    if (e && typeof e === 'object' && 'response' in e) {
      const axiosError = e as { response?: { data?: { detail?: string } } }
      weatherError.value = axiosError.response?.data?.detail || '날씨 데이터를 불러오는데 실패했습니다.'
    } else {
      weatherError.value = '날씨 데이터를 불러오는데 실패했습니다.'
    }
    console.error('Weather fetch failed:', e)
  } finally {
    weatherLoading.value = false
  }
}

// 날짜 변경 시 month, dayofweek 업데이트
watch(gameDate, (newDate) => {
  if (newDate) {
    const date = new Date(newDate)
    formData.month = date.getMonth() + 1
    const jsDay = date.getDay()
    formData.dayofweek = jsDay === 0 ? 6 : jsDay - 1
  }
})

// 구장 변경 시 날씨 데이터 초기화
watch(() => stadiumStore.currentStadium, () => {
  weatherData.value = null
})

// 폼 검증
function validate(): boolean {
  validationError.value = null

  const data = showManualInput.value ? formData : weatherData.value

  if (!data) {
    validationError.value = '날씨 데이터를 먼저 불러오거나 수동으로 입력해주세요.'
    return false
  }

  if (data.daily_precip_sum < 0) {
    validationError.value = '일 강수량은 0 이상이어야 합니다.'
    return false
  }
  if (data.pre_game_humidity < 0 || data.pre_game_humidity > 100) {
    validationError.value = '습도는 0~100 사이여야 합니다.'
    return false
  }

  return true
}

// 예측 요청
async function handlePredict() {
  if (!validate()) return

  // 날씨 데이터 소스 결정 (수동 입력 vs API)
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
  padding: 0.5rem 0;
}

.form-title {
  font-size: 1.1rem;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 1rem 0;
}

.section-title {
  font-size: 0.9rem;
  font-weight: 600;
  color: #4b5563;
  margin: 0;
}

.form-row {
  display: flex;
  gap: 1rem;
  margin-bottom: 0.75rem;
}

.form-group {
  flex: 1;
}

.form-group.full-width {
  flex: 1;
}

.label {
  display: block;
  font-size: 0.85rem;
  font-weight: 500;
  color: #374151;
  margin-bottom: 0.375rem;
}

.input {
  width: 100%;
  padding: 0.625rem 0.75rem;
  font-size: 0.95rem;
  border: 1px solid #d1d5db;
  border-radius: 6px;
  background-color: white;
  transition: border-color 0.2s, box-shadow 0.2s;
  box-sizing: border-box;
}

.input:hover {
  border-color: #9ca3af;
}

.input:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

.fetch-btn {
  width: 100%;
  padding: 0.75rem 1rem;
  font-size: 0.95rem;
  font-weight: 500;
  color: #374151;
  background: white;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  margin: 1rem 0;
}

.fetch-btn:hover:not(:disabled) {
  background: #f9fafb;
  border-color: #9ca3af;
}

.fetch-btn:disabled {
  background: #f3f4f6;
  cursor: not-allowed;
}

/* Weather Data Display */
.weather-data {
  background: linear-gradient(135deg, #eff6ff 0%, #f0fdf4 100%);
  border: 1px solid #bfdbfe;
  border-radius: 8px;
  padding: 1rem;
  margin: 1rem 0;
}

.weather-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.75rem;
}

.data-source {
  font-size: 0.75rem;
  font-weight: 500;
  padding: 0.25rem 0.5rem;
  border-radius: 9999px;
}

.data-source.forecast {
  background: #dbeafe;
  color: #1d4ed8;
}

.data-source.historical {
  background: #e5e7eb;
  color: #4b5563;
}

.weather-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.5rem;
}

.weather-item {
  display: flex;
  justify-content: space-between;
  padding: 0.375rem 0;
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
}

.weather-label {
  font-size: 0.8rem;
  color: #6b7280;
}

.weather-value {
  font-size: 0.85rem;
  font-weight: 500;
  color: #1f2937;
}

/* Manual Toggle */
.manual-toggle {
  margin: 1rem 0;
}

.toggle-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.85rem;
  color: #6b7280;
  cursor: pointer;
}

.toggle-label input[type="checkbox"] {
  width: 16px;
  height: 16px;
}

/* Manual Form */
.manual-form {
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 1rem;
  margin: 1rem 0;
}

.manual-form .section-title {
  margin-bottom: 0.75rem;
}

.error {
  color: #dc2626;
  font-size: 0.85rem;
  margin: 0.75rem 0;
  padding: 0.5rem 0.75rem;
  background-color: #fef2f2;
  border-radius: 6px;
}

.predict-btn {
  width: 100%;
  padding: 0.875rem 1.5rem;
  font-size: 1rem;
  font-weight: 600;
  color: white;
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: transform 0.1s, box-shadow 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  margin-top: 1rem;
}

.predict-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
}

.predict-btn:active:not(:disabled) {
  transform: translateY(0);
}

.predict-btn:disabled {
  background: #9ca3af;
  cursor: not-allowed;
}

.spinner {
  width: 18px;
  height: 18px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

@media (max-width: 600px) {
  .form-row {
    flex-direction: column;
    gap: 0.75rem;
  }

  .weather-grid {
    grid-template-columns: 1fr;
  }
}
</style>
