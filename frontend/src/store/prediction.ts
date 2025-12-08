import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { PredictionRequest, PredictionResponse } from '@/api/types'
import { predictRainCancellation } from '@/api/client'
import { extractErrorMessage, logError } from '@/utils/errors'

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
      error.value = extractErrorMessage(e, '예측 요청에 실패했습니다.')
      logError(e, 'Prediction')
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
