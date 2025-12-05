<template>
  <div class="home-page">
    <div class="main-content">
      <!-- 좌측: 입력 영역 -->
      <div class="input-section">
        <div class="card">
          <StadiumSelector />
          <WeatherForm />
        </div>
      </div>

      <!-- 우측: 결과 영역 -->
      <div class="result-section">
        <div class="card">
          <PredictionResult />
        </div>
        <ModelInfoPanel />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import StadiumSelector from '@/components/StadiumSelector.vue'
import WeatherForm from '@/components/WeatherForm.vue'
import PredictionResult from '@/components/PredictionResult.vue'
import ModelInfoPanel from '@/components/ModelInfoPanel.vue'
</script>

<style scoped>
.home-page {
  flex: 1;
  padding: 2rem;
  background-color: #f1f5f9;
}

.main-content {
  max-width: 1200px;
  margin: 0 auto;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
}

.card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1), 0 1px 2px rgba(0, 0, 0, 0.06);
  padding: 1.5rem;
}

.input-section .card {
  height: fit-content;
}

.result-section .card {
  min-height: 300px;
}

@media (max-width: 900px) {
  .main-content {
    grid-template-columns: 1fr;
  }

  .home-page {
    padding: 1rem;
  }
}
</style>
