import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { PredictionRequest, PredictionResponse } from '@/api/types'
import { predictRainCancellation } from '@/api/client'

export const usePredictionStore = defineStore('prediction', () => {
  // State
  const lastPrediction = ref<PredictionResponse | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Actions
  async function predict(payload: PredictionRequest) {
    loading.value = true
    error.value = null
    lastPrediction.value = null

    try {
      lastPrediction.value = await predictRainCancellation(payload)
    } catch (e: unknown) {
      if (e && typeof e === 'object' && 'response' in e) {
        const axiosError = e as { response?: { data?: { detail?: string } } }
        error.value = axiosError.response?.data?.detail || '예측 요청에 실패했습니다.'
      } else {
        error.value = '예측 요청에 실패했습니다.'
      }
      console.error('Prediction failed:', e)
    } finally {
      loading.value = false
    }
  }

  function clearPrediction() {
    lastPrediction.value = null
    error.value = null
  }

  return {
    lastPrediction,
    loading,
    error,
    predict,
    clearPrediction
  }
})
