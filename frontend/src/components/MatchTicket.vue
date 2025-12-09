<template>
  <div class="match-ticket" :class="[statusClass, { 'is-loading': loading }]">
    <!-- 티켓 상단: 헤더 (구장 정보) -->
    <div class="ticket-header">
      <TeamLogo :teamId="homeTeam.id" size="lg" class="team-logo" />
      <div class="stadium-info">
        <h2 class="stadium-name">{{ stadiumName }}</h2>
        <span class="home-team">{{ homeTeam.name }}</span>
      </div>
    </div>

    <!-- 티켓 중단: 날씨 및 예측 결과 -->
    <div class="ticket-body">
      <!-- 로딩 상태 -->
      <div v-if="loading" class="loading-state">
        <LoadingSpinner size="lg" />
        <p>AI가 분석 중입니다...</p>
      </div>

      <!-- 대기 상태 -->
      <div v-else-if="!hasResult" class="empty-state">
        <div class="empty-icon">
          <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
            <path d="M17.5 19H9a7 7 0 1 1 6.71-9h1.79a4.5 4.5 0 1 1 0 9Z"/>
          </svg>
        </div>
        <p class="empty-text">날씨를 조회하고 예측을 시작하세요</p>
      </div>

      <!-- 예측 결과 -->
      <div v-else class="result-display">
        <WeatherIcon :probability="probability" size="xl" />
        
        <div class="probability-section">
          <div class="probability-value scoreboard">
            {{ probabilityPercent }}<span class="percent">%</span>
          </div>
          <div class="probability-label">우천취소 가능성</div>
        </div>

        <div class="confidence-badge" :class="confidenceClass">
          {{ confidenceText }}
        </div>
      </div>
    </div>

    <!-- 티켓 하단: 점선 경계 + 정보 -->
    <div class="ticket-divider">
      <div class="divider-line"></div>
      <div class="divider-circle left"></div>
      <div class="divider-circle right"></div>
    </div>

    <div class="ticket-footer">
      <div class="info-row">
        <div class="info-item">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"/>
            <polyline points="12 6 12 12 16 14"/>
          </svg>
          <span>{{ gameTime }}</span>
        </div>
        <div class="info-item">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/>
            <circle cx="12" cy="10" r="3"/>
          </svg>
          <span>{{ stadiumName }}</span>
        </div>
      </div>

      <!-- AI 판정 결과 -->
      <div v-if="hasResult" class="verdict" :class="verdictClass">
        <div class="verdict-icon">
          <svg v-if="isPlayable" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3">
            <polyline points="20 6 9 17 4 12"/>
          </svg>
          <svg v-else width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3">
            <line x1="18" y1="6" x2="6" y2="18"/>
            <line x1="6" y1="6" x2="18" y2="18"/>
          </svg>
        </div>
        <span class="verdict-text">{{ verdictText }}</span>
      </div>

      <!-- 타임라인 보기 버튼 -->
      <!-- <button v-if="hasResult && showTimelineButton" class="timeline-button" @click="$emit('scrollToTimeline')">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M17.5 19H9a7 7 0 1 1 6.71-9h1.79a4.5 4.5 0 1 1 0 9Z"/>
        </svg>
        <span>시간대별 강수량 보기</span>
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polyline points="6 9 12 15 18 9"/>
        </svg>
      </button> -->
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import WeatherIcon from './WeatherIcon.vue'
import TeamLogo from './TeamLogo.vue'
import LoadingSpinner from './LoadingSpinner.vue'
import { getStatusClass, PROBABILITY_THRESHOLDS } from '@/constants/probability'

interface Team {
  id: string
  name: string
}

interface Props {
  // 팀 정보
  homeTeam?: Team
  // 경기 정보
  stadiumName?: string
  gameTime?: string
  // 예측 결과
  probability?: number
  confidence?: 'high' | 'medium' | 'low'
  predictionText?: string
  // 상태
  loading?: boolean
  showTimelineButton?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  homeTeam: () => ({ id: 'lg', name: 'LG 트윈스' }),
  stadiumName: '잠실야구장',
  gameTime: '18:30',
  probability: 0,
  confidence: 'low',
  loading: false,
  showTimelineButton: false
})

// Emits
defineEmits<{
  scrollToTimeline: []
}>()

// Computed
const hasResult = computed(() => props.probability > 0 || props.predictionText)

const probabilityPercent = computed(() => Math.round(props.probability * 100))

const isPlayable = computed(() => props.probability < PROBABILITY_THRESHOLDS.MEDIUM)

const statusClass = computed(() => {
  if (props.loading) return 'status-loading'
  if (!hasResult.value) return 'status-empty'
  return getStatusClass(props.probability)
})

const confidenceClass = computed(() => `confidence-${props.confidence}`)

const confidenceText = computed(() => {
  switch (props.confidence) {
    case 'high': return '높은 확률'
    case 'medium': return '주의 필요'
    case 'low': return '안전'
    default: return ''
  }
})

const verdictClass = computed(() => isPlayable.value ? 'verdict-play' : 'verdict-cancel')

const verdictText = computed(() => {
  return props.predictionText || (isPlayable.value ? '경기 진행 예상' : '취소 가능성 높음')
})
</script>

<style scoped>
.match-ticket {
  width: 100%;
  max-width: 360px;
  background: var(--ticket-bg);
  border-radius: var(--radius-2xl);
  box-shadow: var(--shadow-ticket);
  overflow: hidden;
  position: relative;
  margin: 0 auto;
  animation: fadeInUp var(--transition-slow);
}

/* Ticket Header */
.ticket-header {
  display: flex;
  align-items: center;
  gap: var(--space-4);
  padding: var(--space-6) var(--space-5);
  background: linear-gradient(135deg, var(--night-black) 0%, var(--night-black-light) 100%);
}

.team-logo {
  flex-shrink: 0;
}

.stadium-info {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
  flex: 1;
}

.stadium-name {
  font-size: var(--font-size-2xl);
  font-weight: 700;
  color: var(--white);
  margin: 0;
  line-height: 1.2;
}

.home-team {
  font-size: var(--font-size-sm);
  font-weight: 500;
  color: rgba(255, 255, 255, 0.7);
}

/* Ticket Body */
.ticket-body {
  padding: var(--space-8) var(--space-4);
  min-height: 200px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: var(--ticket-bg);
}

/* Loading State */
.loading-state {
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-4);
}

.loading-state p {
  color: var(--storm-gray);
  font-size: var(--font-size-sm);
}

/* Empty State */
.empty-state {
  text-align: center;
}

.empty-icon {
  color: var(--storm-gray-light);
  margin-bottom: var(--space-4);
  opacity: 0.5;
}

.empty-text {
  color: var(--storm-gray);
  font-size: var(--font-size-base);
}

/* Result Display */
.result-display {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-4);
  width: 100%;
}

.probability-section {
  text-align: center;
}

.probability-value {
  font-size: var(--font-size-5xl);
  font-weight: 700;
  line-height: 1;
  color: var(--night-black);
}

.status-safe .probability-value { color: var(--grass-green); }
.status-warning .probability-value { color: var(--clay-brown); }
.status-danger .probability-value { color: var(--danger-red); }

.percent {
  font-size: var(--font-size-2xl);
}

.probability-label {
  font-size: var(--font-size-sm);
  color: var(--storm-gray);
  margin-top: var(--space-1);
}

/* Confidence Badge */
.confidence-badge {
  display: inline-block;
  padding: var(--space-2) var(--space-4);
  font-size: var(--font-size-xs);
  font-weight: 600;
  border-radius: var(--radius-full);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.confidence-low {
  background: rgba(46, 204, 113, 0.15);
  color: var(--grass-green-dark);
}

.confidence-medium {
  background: rgba(230, 126, 34, 0.15);
  color: var(--clay-brown-dark);
}

.confidence-high {
  background: rgba(231, 76, 60, 0.15);
  color: var(--danger-red);
}

/* Ticket Divider */
.ticket-divider {
  position: relative;
  height: 24px;
}

.divider-line {
  position: absolute;
  top: 50%;
  left: 20px;
  right: 20px;
  height: 0;
  border-top: 2px dashed var(--storm-gray-light);
  transform: translateY(-50%);
}

.divider-circle {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  width: 24px;
  height: 24px;
  background: var(--night-black);
  border-radius: 50%;
}

.divider-circle.left { left: -12px; }
.divider-circle.right { right: -12px; }

/* Ticket Footer */
.ticket-footer {
  padding: var(--space-4);
  background: var(--paper-white);
}

.info-row {
  display: flex;
  justify-content: space-around;
  margin-bottom: var(--space-4);
}

.info-item {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  font-size: var(--font-size-sm);
  color: var(--night-black-light);
}

.info-item svg {
  opacity: 0.7;
}

/* Verdict */
.verdict {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-2);
  padding: var(--space-3) var(--space-4);
  border-radius: var(--radius-lg);
  font-weight: 700;
  font-size: var(--font-size-base);
}

.verdict-play {
  background: linear-gradient(135deg, var(--grass-green), var(--grass-green-dark));
  color: var(--white);
  box-shadow: var(--shadow-glow-green);
}

.verdict-cancel {
  background: linear-gradient(135deg, var(--danger-red), #C0392B);
  color: var(--white);
  box-shadow: var(--shadow-glow-red);
}

.verdict-icon {
  display: flex;
}

/* Timeline Button */
.timeline-button {
  margin-top: var(--space-3);
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-2);
  padding: var(--space-3) var(--space-4);
  background: linear-gradient(135deg, rgba(52, 152, 219, 0.1), rgba(41, 128, 185, 0.1));
  border: 1px solid rgba(52, 152, 219, 0.3);
  border-radius: var(--radius-lg);
  color: #3498db;
  font-size: var(--font-size-sm);
  font-weight: 600;
  cursor: pointer;
  transition: all var(--transition-base);
}

.timeline-button:hover {
  background: linear-gradient(135deg, rgba(52, 152, 219, 0.2), rgba(41, 128, 185, 0.2));
  border-color: rgba(52, 152, 219, 0.5);
  transform: translateY(-2px);
}

.timeline-button:active {
  transform: translateY(0);
}

.timeline-button svg:last-child {
  animation: bounce 2s infinite;
}

@keyframes bounce {
  0%, 20%, 50%, 80%, 100% {
    transform: translateY(0);
  }
  40% {
    transform: translateY(-4px);
  }
  60% {
    transform: translateY(-2px);
  }
}

/* Status-based borders */
.status-safe {
  border: 3px solid var(--grass-green);
}

.status-warning {
  border: 3px solid var(--clay-brown);
}

.status-danger {
  border: 3px solid var(--danger-red);
}

/* Animations */
@keyframes spin {
  to { transform: rotate(360deg); }
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
