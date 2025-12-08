/**
 * 경기 시간 및 날짜 관련 상수
 */

export interface GameTimeOption {
  value: number
  label: string
  type: 'day' | 'early' | 'night'
}

/**
 * 경기 시간 옵션
 */
export const GAME_TIME_OPTIONS: readonly GameTimeOption[] = [
  { value: 14, label: '14:00 (주간)', type: 'day' },
  { value: 17, label: '17:00 (조기)', type: 'early' },
  { value: 18, label: '18:30 (야간)', type: 'night' },
] as const

/**
 * 기본 경기 시간
 */
export const DEFAULT_GAME_TIME = 18

/**
 * 날짜 범위 설정
 */
export const DATE_RANGE_CONFIG = {
  PAST_YEARS: 5,
  FUTURE_DAYS: 14,
} as const

/**
 * 최소 선택 가능 날짜 (5년 전)
 */
export function getMinDate(): string {
  const date = new Date()
  date.setFullYear(date.getFullYear() - DATE_RANGE_CONFIG.PAST_YEARS)
  return date.toISOString().split('T')[0]
}

/**
 * 최대 선택 가능 날짜 (14일 후)
 */
export function getMaxDate(): string {
  const date = new Date()
  date.setDate(date.getDate() + DATE_RANGE_CONFIG.FUTURE_DAYS)
  return date.toISOString().split('T')[0]
}

/**
 * 오늘 날짜
 */
export function getTodayDate(): string {
  return new Date().toISOString().split('T')[0]
}

/**
 * 경기 시간 값으로 라벨 찾기
 */
export function getGameTimeLabel(hour: number): string {
  const option = GAME_TIME_OPTIONS.find(opt => opt.value === hour)
  return option?.label || `${hour}:00`
}

/**
 * 경기 시간 타입 가져오기
 */
export function getGameTimeType(hour: number): 'day' | 'early' | 'night' {
  const option = GAME_TIME_OPTIONS.find(opt => opt.value === hour)
  return option?.type || 'night'
}
