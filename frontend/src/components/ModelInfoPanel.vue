<template>
  <div class="model-info-panel">
    <h4 class="panel-title">모델 정보</h4>

    <div v-if="loading" class="loading">
      <div class="mini-spinner"></div>
      <span>로딩 중...</span>
    </div>

    <div v-else-if="modelInfo" class="info-content">
      <div class="info-row">
        <span class="info-label">모델 타입</span>
        <span class="info-value">{{ modelInfo.model_type }}</span>
      </div>
      <div class="info-row">
        <span class="info-label">피처 개수</span>
        <span class="info-value">{{ modelInfo.feature_count }}개</span>
      </div>
      <div class="info-row">
        <span class="info-label">버전</span>
        <span class="info-value">v{{ modelInfo.version }}</span>
      </div>
      <div class="info-description">
        {{ modelInfo.description }}
      </div>
    </div>

    <div v-else class="empty">
      모델 정보를 불러올 수 없습니다.
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useStadiumStore } from '@/store'

const stadiumStore = useStadiumStore()

const modelInfo = computed(() => stadiumStore.modelInfo)
const loading = computed(() => stadiumStore.loading)
</script>

<style scoped>
.model-info-panel {
  background-color: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 1rem;
  margin-top: 1rem;
}

.panel-title {
  font-size: 0.9rem;
  font-weight: 600;
  color: #475569;
  margin: 0 0 0.75rem 0;
}

.loading {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #64748b;
  font-size: 0.85rem;
}

.mini-spinner {
  width: 14px;
  height: 14px;
  border: 2px solid #e2e8f0;
  border-top-color: #3b82f6;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.info-content {
  font-size: 0.85rem;
}

.info-row {
  display: flex;
  justify-content: space-between;
  padding: 0.375rem 0;
  border-bottom: 1px solid #e2e8f0;
}

.info-row:last-of-type {
  border-bottom: none;
}

.info-label {
  color: #64748b;
}

.info-value {
  color: #334155;
  font-weight: 500;
}

.info-description {
  margin-top: 0.75rem;
  padding-top: 0.75rem;
  border-top: 1px solid #e2e8f0;
  color: #64748b;
  font-size: 0.8rem;
  line-height: 1.5;
}

.empty {
  color: #94a3b8;
  font-size: 0.85rem;
}
</style>
