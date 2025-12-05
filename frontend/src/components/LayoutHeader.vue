<template>
  <header class="header glass">
    <div class="header-content">
      <div class="brand">
        <div class="logo-icon">
          <svg width="32" height="32" viewBox="0 0 32 32" fill="none">
            <circle cx="16" cy="16" r="14" stroke="currentColor" stroke-width="2"/>
            <path d="M16 4 L16 16 L24 20" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
            <circle cx="16" cy="16" r="3" fill="currentColor"/>
          </svg>
        </div>
        <div class="brand-text">
          <h1 class="title">KBO 우천취소 예측</h1>
          <p class="subtitle">AI 기반 경기 취소 확률 분석</p>
        </div>
      </div>
      <div class="status-indicator" :class="apiStatusClass">
        <span class="status-dot"></span>
        <span class="status-text">{{ apiStatusText }}</span>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { getHealth } from '@/api/client'

const apiStatus = ref<'checking' | 'online' | 'offline'>('checking')

const apiStatusClass = computed(() => `status-${apiStatus.value}`)
const apiStatusText = computed(() => {
  switch (apiStatus.value) {
    case 'checking': return '연결 확인 중...'
    case 'online': return 'API 연결됨'
    case 'offline': return '연결 안됨'
  }
})

onMounted(async () => {
  try {
    await getHealth()
    apiStatus.value = 'online'
  } catch {
    apiStatus.value = 'offline'
  }
})
</script>

<style scoped>
.header {
  padding: var(--space-4) var(--space-6);
  position: sticky;
  top: 0;
  z-index: var(--z-sticky);
}

.header-content {
  max-width: 1400px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.brand {
  display: flex;
  align-items: center;
  gap: var(--space-4);
}

.logo-icon {
  color: var(--grass-green);
  animation: pulse 2s ease-in-out infinite;
}

.brand-text {
  display: flex;
  flex-direction: column;
}

.title {
  font-size: var(--font-size-xl);
  font-weight: 700;
  color: var(--white);
  margin: 0;
  line-height: 1.2;
}

.subtitle {
  font-size: var(--font-size-xs);
  color: rgba(255, 255, 255, 0.7);
  margin: 0;
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: var(--space-2) var(--space-3);
  background: rgba(255, 255, 255, 0.1);
  border-radius: var(--radius-full);
  font-size: var(--font-size-xs);
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  animation: pulse 2s ease-in-out infinite;
}

.status-checking .status-dot {
  background: var(--clay-brown);
}

.status-online .status-dot {
  background: var(--grass-green);
  box-shadow: 0 0 8px var(--grass-green);
}

.status-offline .status-dot {
  background: var(--danger-red);
}

.status-text {
  color: rgba(255, 255, 255, 0.8);
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.6; }
}

/* Mobile */
@media (max-width: 640px) {
  .header {
    padding: var(--space-3) var(--space-4);
  }
  
  .title {
    font-size: var(--font-size-lg);
  }
  
  .subtitle {
    display: none;
  }
  
  .status-text {
    display: none;
  }
}
</style>
