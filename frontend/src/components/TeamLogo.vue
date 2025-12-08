<template>
  <div class="team-logo" :class="[sizeClass]" :style="{ '--team-color': teamColor }">
    <!-- LG 트윈스 -->
    <svg v-if="teamId === 'lg'" viewBox="0 0 64 64">
      <circle cx="32" cy="32" r="30" fill="#C30452"/>
      <text x="32" y="40" text-anchor="middle" fill="white" font-weight="bold" font-size="22">LG</text>
    </svg>

    <!-- 두산 베어스 -->
    <svg v-else-if="teamId === 'doosan'" viewBox="0 0 64 64">
      <circle cx="32" cy="32" r="30" fill="#131230"/>
      <text x="32" y="40" text-anchor="middle" fill="white" font-weight="bold" font-size="16">두산</text>
    </svg>

    <!-- 삼성 라이온즈 -->
    <svg v-else-if="teamId === 'samsung'" viewBox="0 0 64 64">
      <circle cx="32" cy="32" r="30" fill="#074CA1"/>
      <text x="32" y="40" text-anchor="middle" fill="white" font-weight="bold" font-size="16">삼성</text>
    </svg>

    <!-- KT 위즈 -->
    <svg v-else-if="teamId === 'kt'" viewBox="0 0 64 64">
      <circle cx="32" cy="32" r="30" fill="#000000"/>
      <text x="32" y="40" text-anchor="middle" fill="#EE2737" font-weight="bold" font-size="20">KT</text>
    </svg>

    <!-- SSG 랜더스 -->
    <svg v-else-if="teamId === 'ssg'" viewBox="0 0 64 64">
      <circle cx="32" cy="32" r="30" fill="#CE0E2D"/>
      <text x="32" y="40" text-anchor="middle" fill="#FFD100" font-weight="bold" font-size="16">SSG</text>
    </svg>

    <!-- 롯데 자이언츠 -->
    <svg v-else-if="teamId === 'lotte'" viewBox="0 0 64 64">
      <circle cx="32" cy="32" r="30" fill="#002955"/>
      <text x="32" y="40" text-anchor="middle" fill="#D00F31" font-weight="bold" font-size="16">롯데</text>
    </svg>

    <!-- 한화 이글스 -->
    <svg v-else-if="teamId === 'hanwha'" viewBox="0 0 64 64">
      <circle cx="32" cy="32" r="30" fill="#FF6600"/>
      <text x="32" y="40" text-anchor="middle" fill="white" font-weight="bold" font-size="16">한화</text>
    </svg>

    <!-- 키움 히어로즈 -->
    <svg v-else-if="teamId === 'kiwoom'" viewBox="0 0 64 64">
      <circle cx="32" cy="32" r="30" fill="#820024"/>
      <text x="32" y="40" text-anchor="middle" fill="white" font-weight="bold" font-size="16">키움</text>
    </svg>

    <!-- NC 다이노스 -->
    <svg v-else-if="teamId === 'nc'" viewBox="0 0 64 64">
      <circle cx="32" cy="32" r="30" fill="#315288"/>
      <text x="32" y="40" text-anchor="middle" fill="#C7A67A" font-weight="bold" font-size="20">NC</text>
    </svg>

    <!-- KIA 타이거즈 -->
    <svg v-else-if="teamId === 'kia'" viewBox="0 0 64 64">
      <circle cx="32" cy="32" r="30" fill="#EA0029"/>
      <text x="32" y="40" text-anchor="middle" fill="white" font-weight="bold" font-size="18">KIA</text>
    </svg>

    <!-- 기본 (알 수 없는 팀) -->
    <svg v-else viewBox="0 0 64 64">
      <circle cx="32" cy="32" r="30" fill="#7F8C8D"/>
      <text x="32" y="40" text-anchor="middle" fill="white" font-weight="bold" font-size="14">KBO</text>
    </svg>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { getTeamColor } from '@/constants/teams'

interface Props {
  teamId: string
  size?: 'sm' | 'md' | 'lg'
}

const props = withDefaults(defineProps<Props>(), {
  size: 'md'
})

const sizeClass = computed(() => `size-${props.size}`)

const teamColor = computed(() => getTeamColor(props.teamId))
</script>

<style scoped>
.team-logo {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
  transition: transform var(--transition-fast);
}

.team-logo:hover {
  transform: scale(1.05);
}

.team-logo svg {
  width: 100%;
  height: 100%;
}

/* Sizes */
.size-sm { width: 40px; height: 40px; }
.size-md { width: 56px; height: 56px; }
.size-lg { width: 72px; height: 72px; }
</style>
