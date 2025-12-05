<template>
  <header class="header">
    <div class="header-content">
      <h1 class="title">KBO 우천취소 예측</h1>
      <p class="subtitle">경기 시작 전, 우천취소 가능성을 미리 확인하세요</p>
    </div>
  </header>
</template>

<script setup lang="ts">
</script>

<style scoped>
.header {
  background: linear-gradient(135deg, #1a365d 0%, #2d4a7c 100%);
  color: white;
  padding: 1.5rem 2rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.header-content {
  max-width: 1200px;
  margin: 0 auto;
}

.title {
  font-size: 1.75rem;
  font-weight: 700;
  margin: 0 0 0.25rem 0;
}

.subtitle {
  font-size: 0.95rem;
  opacity: 0.9;
  margin: 0;
}
</style>
