<template>
  <footer class="footer">
    <div class="footer-content">
      <p class="data-info">
        데이터 기준: 2019~2024 잠실 경기 + Open-Meteo 날씨
      </p>
      <p class="disclaimer">
        본 예측은 참고용이며, 실제 경기 취소 여부는 KBO 공식 발표를 확인하세요.
      </p>
    </div>
  </footer>
</template>

<script setup lang="ts">
</script>

<style scoped>
.footer {
  background: #f8fafc;
  border-top: 1px solid #e2e8f0;
  padding: 1rem 2rem;
  margin-top: auto;
}

.footer-content {
  max-width: 1200px;
  margin: 0 auto;
  text-align: center;
}

.data-info {
  font-size: 0.85rem;
  color: #64748b;
  margin: 0 0 0.25rem 0;
}

.disclaimer {
  font-size: 0.75rem;
  color: #94a3b8;
  margin: 0;
}
</style>
