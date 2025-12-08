/**
 * 확률 임계값 및 리스크 레벨 관련 상수
 */

export const PROBABILITY_THRESHOLDS = {
  HIGH: 0.7,
  MEDIUM: 0.5,
  LOW: 0.3,
} as const

export type RiskLevel = 'high' | 'medium' | 'low' | 'none'

/**
 * 확률 값에 따른 리스크 레벨 반환
 */
export function getRiskLevel(probability: number): RiskLevel {
  if (probability >= PROBABILITY_THRESHOLDS.HIGH) return 'high'
  if (probability >= PROBABILITY_THRESHOLDS.MEDIUM) return 'medium'
  if (probability >= PROBABILITY_THRESHOLDS.LOW) return 'low'
  return 'none'
}

/**
 * 리스크 레벨에 따른 CSS 클래스명 반환
 */
export function getRiskLevelClass(probability: number): string {
  const level = getRiskLevel(probability)
  if (level === 'none') return 'risk-safe'
  return `risk-${level}`
}

/**
 * 확률에 따른 상태 클래스 반환 (MatchTicket용)
 */
export function getStatusClass(probability: number): string {
  if (probability >= PROBABILITY_THRESHOLDS.HIGH) return 'status-danger'
  if (probability >= PROBABILITY_THRESHOLDS.MEDIUM) return 'status-warning'
  return 'status-safe'
}

/**
 * 확률에 따른 날씨 아이콘 타입 반환
 */
export function getWeatherIconType(probability: number): string {
  if (probability >= PROBABILITY_THRESHOLDS.HIGH) return 'weather-rain'
  if (probability >= PROBABILITY_THRESHOLDS.MEDIUM) return 'weather-cloudy'
  return 'weather-sunny'
}

/**
 * 확률에 따른 강우 강도 반환 (WeatherIcon용)
 */
export function getRainIntensity(probability: number): 'heavy' | 'rainy' | 'cloudy' | 'sunny' {
  if (probability >= PROBABILITY_THRESHOLDS.HIGH) return 'heavy'
  if (probability >= PROBABILITY_THRESHOLDS.MEDIUM) return 'rainy'
  if (probability >= PROBABILITY_THRESHOLDS.LOW) return 'cloudy'
  return 'sunny'
}

/**
 * 확률에 따른 마커 상태 반환 (StadiumMarker용)
 */
export function getMarkerStatus(probability: number): 'danger' | 'warning' | 'safe' {
  if (probability >= PROBABILITY_THRESHOLDS.HIGH) return 'danger'
  if (probability >= PROBABILITY_THRESHOLDS.MEDIUM) return 'warning'
  return 'safe'
}
