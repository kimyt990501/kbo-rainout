<template>
  <div class="prediction-result">
    <h3 class="result-title">예측 결과</h3>

    <!-- 결과가 없을 때 -->
    <div v-if="!prediction && !loading" class="empty-state">
      <div class="empty-icon">
        <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
          <path d="M17.5 19H9a7 7 0 1 1 6.71-9h1.79a4.5 4.5 0 1 1 0 9Z"/>
        </svg>
      </div>
      <p class="empty-text">
        예측 결과가 없습니다.<br />
        좌측에서 정보를 입력하고 예측하기를 눌러주세요.
      </p>
    </div>

    <!-- 로딩 중 -->
    <div v-else-if="loading" class="loading-state">
      <div class="loading-spinner"></div>
      <p class="loading-text">예측 중입니다...</p>
    </div>

    <!-- 결과 표시 -->
    <div v-else-if="prediction" class="result-content">
      <!-- 메인 확률 -->
      <div :class="['probability-card', confidenceClass]">
        <div class="probability-value">
          {{ probabilityPercent }}%
        </div>
        <div class="probability-label">
          우천취소 가능성
        </div>
        <div class="prediction-text">
          {{ prediction.prediction }}
        </div>
      </div>

      <!-- 구장 정보 -->
      <div class="stadium-info">
        <span class="stadium-badge">{{ prediction.stadium_name }}</span>
      </div>

      <!-- 위험 요소 -->
      <div v-if="prediction.risk_factors.length > 0" class="risk-factors">
        <h4 class="risk-title">위험 요소</h4>
        <ul class="risk-list">
          <li
            v-for="(factor, index) in prediction.risk_factors"
            :key="index"
            class="risk-item"
          >
            {{ factor }}
          </li>
        </ul>
      </div>

      <!-- 위험 요소 없음 -->
      <div v-else class="no-risk">
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
          <polyline points="22 4 12 14.01 9 11.01"/>
        </svg>
        <span>특별한 위험 요소가 감지되지 않았습니다.</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { usePredictionStore } from '@/store'

const predictionStore = usePredictionStore()

const prediction = computed(() => predictionStore.lastPrediction)
const loading = computed(() => predictionStore.loading)

const probabilityPercent = computed(() => {
  if (!prediction.value) return 0
  return Math.round(prediction.value.cancellation_probability * 100)
})

const confidenceClass = computed(() => {
  if (!prediction.value) return ''
  return `confidence-${prediction.value.confidence}`
})
</script>

<style scoped>
.prediction-result {
  padding: 0.5rem 0;
}

.result-title {
  font-size: 1.1rem;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 1rem 0;
}

/* Empty State */
.empty-state {
  text-align: center;
  padding: 2rem 1rem;
}

.empty-icon {
  color: #9ca3af;
  margin-bottom: 1rem;
}

.empty-text {
  color: #6b7280;
  font-size: 0.95rem;
  line-height: 1.6;
}

/* Loading State */
.loading-state {
  text-align: center;
  padding: 2rem 1rem;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #e5e7eb;
  border-top-color: #3b82f6;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin: 0 auto 1rem;
}

.loading-text {
  color: #6b7280;
  font-size: 0.95rem;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* Result Content */
.result-content {
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Probability Card */
.probability-card {
  text-align: center;
  padding: 1.5rem;
  border-radius: 12px;
  margin-bottom: 1rem;
}

.probability-card.confidence-high {
  background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
  border: 1px solid #fecaca;
}

.probability-card.confidence-medium {
  background: linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%);
  border: 1px solid #fde68a;
}

.probability-card.confidence-low {
  background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
  border: 1px solid #bbf7d0;
}

.probability-value {
  font-size: 3rem;
  font-weight: 700;
  line-height: 1;
  margin-bottom: 0.25rem;
}

.confidence-high .probability-value {
  color: #dc2626;
}

.confidence-medium .probability-value {
  color: #d97706;
}

.confidence-low .probability-value {
  color: #16a34a;
}

.probability-label {
  font-size: 0.9rem;
  color: #6b7280;
  margin-bottom: 0.5rem;
}

.prediction-text {
  font-size: 1.1rem;
  font-weight: 600;
}

.confidence-high .prediction-text {
  color: #b91c1c;
}

.confidence-medium .prediction-text {
  color: #b45309;
}

.confidence-low .prediction-text {
  color: #15803d;
}

/* Stadium Info */
.stadium-info {
  text-align: center;
  margin-bottom: 1rem;
}

.stadium-badge {
  display: inline-block;
  padding: 0.375rem 0.75rem;
  font-size: 0.85rem;
  font-weight: 500;
  color: #4b5563;
  background-color: #f3f4f6;
  border-radius: 9999px;
}

/* Risk Factors */
.risk-factors {
  background-color: #f9fafb;
  border-radius: 8px;
  padding: 1rem;
}

.risk-title {
  font-size: 0.9rem;
  font-weight: 600;
  color: #374151;
  margin: 0 0 0.75rem 0;
}

.risk-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.risk-item {
  font-size: 0.9rem;
  color: #4b5563;
  padding: 0.375rem 0;
  padding-left: 1.25rem;
  position: relative;
}

.risk-item::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0.75rem;
  width: 6px;
  height: 6px;
  background-color: #f59e0b;
  border-radius: 50%;
}

/* No Risk */
.no-risk {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  background-color: #f0fdf4;
  border-radius: 8px;
  color: #16a34a;
  font-size: 0.9rem;
}
</style>
