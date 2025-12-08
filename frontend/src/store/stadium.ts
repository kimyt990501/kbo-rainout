import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Stadium, ModelInfo } from '@/api/types'
import { getStadiums, getModelInfo } from '@/api/client'

export const useStadiumStore = defineStore('stadium', () => {
  // State
  const stadiumList = ref<Stadium[]>([])
  const currentStadium = ref<string>('jamsil')
  const modelInfo = ref<ModelInfo | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Getters
  const availableStadiums = computed(() =>
    stadiumList.value.filter(s => s.available)
  )

  const currentStadiumInfo = computed(() =>
    stadiumList.value.find(s => s.id === currentStadium.value)
  )

  // Actions
  async function fetchStadiums() {
    loading.value = true
    error.value = null
    try {
      stadiumList.value = await getStadiums()
      // 기본값이 없거나 사용 불가능하면 첫 번째 가용 구장 선택
      if (!stadiumList.value.find(s => s.id === currentStadium.value && s.available)) {
        const firstAvailable = stadiumList.value.find(s => s.available)
        if (firstAvailable) {
          currentStadium.value = firstAvailable.id
        }
      }
    } catch (e) {
      error.value = '구장 목록을 불러오는데 실패했습니다.'
      console.error('Failed to fetch stadiums:', e)
    } finally {
      loading.value = false
    }
  }

  async function fetchModelInfo() {
    if (!currentStadium.value) return

    loading.value = true
    error.value = null
    try {
      modelInfo.value = await getModelInfo(currentStadium.value) as ModelInfo
    } catch (e) {
      error.value = '모델 정보를 불러오는데 실패했습니다.'
      console.error('Failed to fetch model info:', e)
    } finally {
      loading.value = false
    }
  }

  function setStadium(stadiumId: string) {
    currentStadium.value = stadiumId
    fetchModelInfo()
  }

  return {
    // State
    stadiumList,
    currentStadium,
    modelInfo,
    loading,
    error,
    // Getters
    availableStadiums,
    currentStadiumInfo,
    // Actions
    fetchStadiums,
    fetchModelInfo,
    setStadium
  }
})
