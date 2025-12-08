/**
 * 에러 처리 유틸리티 함수
 */

/**
 * Axios 에러 타입 가드
 */
export function isAxiosError(error: unknown): error is {
  response?: {
    data?: {
      detail?: string
      message?: string
    }
    status?: number
  }
  message?: string
} {
  return (
    error !== null &&
    typeof error === 'object' &&
    'response' in error
  )
}

/**
 * 에러 객체에서 사용자에게 표시할 메시지 추출
 *
 * @param error - 에러 객체 (unknown 타입)
 * @param defaultMessage - 에러 메시지를 추출할 수 없을 때 사용할 기본 메시지
 * @returns 사용자에게 표시할 에러 메시지
 */
export function extractErrorMessage(
  error: unknown,
  defaultMessage: string = '요청에 실패했습니다.'
): string {
  // Axios 에러인 경우
  if (isAxiosError(error)) {
    // 서버에서 보낸 상세 메시지가 있는 경우
    if (error.response?.data?.detail) {
      return error.response.data.detail
    }

    // 서버에서 보낸 일반 메시지가 있는 경우
    if (error.response?.data?.message) {
      return error.response.data.message
    }

    // HTTP 상태 코드별 기본 메시지
    if (error.response?.status) {
      switch (error.response.status) {
        case 400:
          return '잘못된 요청입니다.'
        case 401:
          return '인증이 필요합니다.'
        case 403:
          return '접근 권한이 없습니다.'
        case 404:
          return '요청한 리소스를 찾을 수 없습니다.'
        case 500:
          return '서버 오류가 발생했습니다.'
        case 503:
          return '서비스를 일시적으로 사용할 수 없습니다.'
        default:
          return `오류가 발생했습니다. (${error.response.status})`
      }
    }

    // Axios 에러 메시지
    if (error.message) {
      return error.message
    }
  }

  // 일반 Error 객체인 경우
  if (error instanceof Error) {
    return error.message
  }

  // 문자열인 경우
  if (typeof error === 'string') {
    return error
  }

  // 그 외의 경우 기본 메시지 반환
  return defaultMessage
}

/**
 * 네트워크 에러 여부 확인
 */
export function isNetworkError(error: unknown): boolean {
  if (isAxiosError(error)) {
    return !error.response && !!error.message
  }
  return false
}

/**
 * 타임아웃 에러 여부 확인
 */
export function isTimeoutError(error: unknown): boolean {
  if (error instanceof Error) {
    return error.message.toLowerCase().includes('timeout')
  }
  if (isAxiosError(error) && error.message) {
    return error.message.toLowerCase().includes('timeout')
  }
  return false
}

/**
 * 에러 로깅 (개발 환경에서만)
 */
export function logError(error: unknown, context?: string): void {
  if (import.meta.env.DEV) {
    console.error(`[Error${context ? ` - ${context}` : ''}]:`, error)
  }
}

/**
 * 에러 메시지 포매팅
 * 사용자 친화적인 메시지로 변환
 */
export function formatErrorMessage(error: unknown): {
  title: string
  message: string
  canRetry: boolean
} {
  if (isNetworkError(error)) {
    return {
      title: '네트워크 오류',
      message: '인터넷 연결을 확인해주세요.',
      canRetry: true,
    }
  }

  if (isTimeoutError(error)) {
    return {
      title: '시간 초과',
      message: '요청 시간이 초과되었습니다. 다시 시도해주세요.',
      canRetry: true,
    }
  }

  if (isAxiosError(error) && error.response?.status === 500) {
    return {
      title: '서버 오류',
      message: '서버에 문제가 발생했습니다. 잠시 후 다시 시도해주세요.',
      canRetry: true,
    }
  }

  return {
    title: '오류',
    message: extractErrorMessage(error),
    canRetry: false,
  }
}
