// 구장 정보
export interface Stadium {
  id: string
  name: string
  team: string
  available: boolean
}

export interface StadiumsResponse {
  stadiums: Stadium[]
}

// 모델 정보
export interface ModelInfo {
  stadium: string
  stadium_name: string
  model_type: string
  feature_count: number
  features: string[]
  description: string
  version: string
}

export interface AllModelsInfo {
  models: Record<string, ModelInfo>
}

// 예측 요청
export interface PredictionRequest {
  stadium: string
  daily_precip_sum: number
  daily_precip_hours: number
  pre_game_precip: number
  pre_game_humidity: number
  pre_game_temp: number
  pre_game_wind: number
  prev_day_precip: number
  daily_wind_max: number
  daily_temp_mean: number
  month: number
  dayofweek: number
}

// 예측 응답
export interface PredictionResponse {
  stadium: string
  stadium_name: string
  cancellation_probability: number
  prediction: string
  confidence: 'high' | 'medium' | 'low'
  risk_factors: string[]
}

// 헬스 체크
export interface HealthResponse {
  status: string
}

// 날씨 폼 데이터 (UI용)
export interface WeatherFormData {
  gameDate: string
  gameTime: string
  daily_precip_sum: number
  daily_precip_hours: number
  pre_game_precip: number
  pre_game_humidity: number
  pre_game_temp: number
  pre_game_wind: number
  prev_day_precip: number
  daily_wind_max: number
  daily_temp_mean: number
  month: number
  dayofweek: number
}

// 날씨 API 요청
export interface WeatherRequest {
  stadium: string
  game_date: string
  game_hour: number
}

// 날씨 API 응답
export interface WeatherResponse {
  stadium: string
  stadium_name: string
  game_date: string
  game_hour: number
  daily_precip_sum: number
  daily_precip_hours: number
  pre_game_precip: number
  pre_game_humidity: number
  pre_game_temp: number
  pre_game_wind: number
  prev_day_precip: number
  daily_wind_max: number
  daily_temp_mean: number
  month: number
  dayofweek: number
  data_source: 'forecast' | 'historical'
}

// 타임라인 API 요청
export interface WeatherTimelineRequest {
  stadium: string
  game_date: string
  game_hour: number
  hours_before?: number
  hours_after?: number
}

// 타임라인 포인트
export interface TimelinePoint {
  hour: number
  time_label: string
  precipitation: number
  is_game_time: boolean
  relative_time: string
}

// 타임라인 API 응답
export interface WeatherTimelineResponse {
  stadium: string
  stadium_name: string
  game_date: string
  game_hour: number
  timeline: TimelinePoint[]
  total_precipitation: number
  data_source: 'forecast' | 'historical'
}
