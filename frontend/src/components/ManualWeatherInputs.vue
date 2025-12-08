<template>
  <div v-if="show" class="manual-weather-inputs animate-fadeIn">
    <div class="form-row">
      <div class="form-group">
        <label class="label">일 강수량 (mm)</label>
        <input
          :value="formData.daily_precip_sum"
          @input="updateField('daily_precip_sum', Number(($event.target as HTMLInputElement).value))"
          type="number"
          min="0"
          step="0.1"
          class="input"
        />
      </div>
      <div class="form-group">
        <label class="label">강수 시간</label>
        <input
          :value="formData.daily_precip_hours"
          @input="updateField('daily_precip_hours', Number(($event.target as HTMLInputElement).value))"
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
        <label class="label">경기 전 3시간 강수 (mm)</label>
        <input
          :value="formData.pre_game_precip"
          @input="updateField('pre_game_precip', Number(($event.target as HTMLInputElement).value))"
          type="number"
          min="0"
          step="0.1"
          class="input"
        />
      </div>
      <div class="form-group">
        <label class="label">전날 강수량 (mm)</label>
        <input
          :value="formData.prev_day_precip"
          @input="updateField('prev_day_precip', Number(($event.target as HTMLInputElement).value))"
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
          :value="formData.pre_game_humidity"
          @input="updateField('pre_game_humidity', Number(($event.target as HTMLInputElement).value))"
          type="number"
          min="0"
          max="100"
          class="input"
        />
      </div>
      <div class="form-group">
        <label class="label">기온 (°C)</label>
        <input
          :value="formData.pre_game_temp"
          @input="updateField('pre_game_temp', Number(($event.target as HTMLInputElement).value))"
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
          :value="formData.pre_game_wind"
          @input="updateField('pre_game_wind', Number(($event.target as HTMLInputElement).value))"
          type="number"
          min="0"
          step="0.1"
          class="input"
        />
      </div>
      <div class="form-group">
        <label class="label">최대 풍속 (m/s)</label>
        <input
          :value="formData.daily_wind_max"
          @input="updateField('daily_wind_max', Number(($event.target as HTMLInputElement).value))"
          type="number"
          min="0"
          step="0.1"
          class="input"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
interface WeatherFormData {
  daily_precip_sum: number
  daily_precip_hours: number
  pre_game_precip: number
  pre_game_humidity: number
  pre_game_temp: number
  pre_game_wind: number
  prev_day_precip: number
  daily_wind_max: number
  daily_temp_mean: number
  month: number
  dayofweek: number
}

interface Props {
  show: boolean
  formData: WeatherFormData
}

defineProps<Props>()

const emit = defineEmits<{
  (e: 'update:formData', field: keyof WeatherFormData, value: number): void
}>()

function updateField(field: keyof WeatherFormData, value: number) {
  emit('update:formData', field, value)
}
</script>

<style scoped>
.manual-weather-inputs {
  margin-top: var(--space-4);
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-4);
  margin-bottom: var(--space-3);
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.label {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  font-size: var(--font-size-sm);
  font-weight: 500;
  color: rgba(255, 255, 255, 0.9);
}

.input {
  width: 100%;
  padding: var(--space-3);
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: var(--radius-md);
  color: var(--white);
  font-size: var(--font-size-sm);
  transition: all var(--transition-base);
}

.input:hover {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(255, 255, 255, 0.2);
}

.input:focus {
  outline: none;
  background: rgba(255, 255, 255, 0.1);
  border-color: var(--grass-green);
  box-shadow: 0 0 0 3px rgba(46, 204, 113, 0.1);
}

/* 애니메이션 */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-fadeIn {
  animation: fadeIn 0.3s ease-out;
}

/* 모바일 최적화 */
@media (max-width: 640px) {
  .form-row {
    grid-template-columns: 1fr;
  }
}
</style>
