import axios, { type AxiosInstance } from 'axios'
import type {
  HealthResponse,
  Stadium,
  StadiumsResponse,
  ModelInfo,
  AllModelsInfo,
  PredictionRequest,
  PredictionResponse,
  WeatherRequest,
  WeatherResponse,
  WeatherTimelineRequest,
  WeatherTimelineResponse
} from './types'

const baseURL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8600'

const apiClient: AxiosInstance = axios.create({
  baseURL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 헬스 체크
export async function getHealth(): Promise<HealthResponse> {
  const response = await apiClient.get<HealthResponse>('/api/health')
  return response.data
}

// 구장 목록 조회
export async function getStadiums(): Promise<Stadium[]> {
  const response = await apiClient.get<StadiumsResponse>('/api/stadiums')
  return response.data.stadiums
}

// 모델 정보 조회
export async function getModelInfo(stadium?: string): Promise<ModelInfo | AllModelsInfo> {
  if (stadium) {
    const response = await apiClient.get<ModelInfo>('/api/model-info', {
      params: { stadium }
    })
    return response.data
  } else {
    const response = await apiClient.get<AllModelsInfo>('/api/model-info')
    return response.data
  }
}

// 우천취소 예측
export async function predictRainCancellation(
  payload: PredictionRequest
): Promise<PredictionResponse> {
  const response = await apiClient.post<PredictionResponse>('/api/predict', payload)
  return response.data
}

// 날씨 데이터 조회
export async function getWeather(
  payload: WeatherRequest
): Promise<WeatherResponse> {
  const response = await apiClient.post<WeatherResponse>('/api/weather', payload)
  return response.data
}

// 날씨 타임라인 조회
export async function getWeatherTimeline(
  payload: WeatherTimelineRequest
): Promise<WeatherTimelineResponse> {
  const response = await apiClient.post<WeatherTimelineResponse>('/api/weather/timeline', payload)
  return response.data
}

export default apiClient
