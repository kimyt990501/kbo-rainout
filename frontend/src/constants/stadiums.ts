/**
 * KBO 경기장 정보 상수
 */

export interface StadiumInfo {
  id: string
  name: string
  team: string
  city: string
  coordinates: {
    lat: number
    lng: number
  }
  mapPosition: {
    x: number
    y: number
  }
}

export const STADIUMS = {
  jamsil: {
    id: 'jamsil',
    name: '잠실야구장',
    team: 'LG 트윈스 / 두산 베어스',
    city: '서울',
    coordinates: { lat: 37.5121, lng: 127.0718 },
    mapPosition: { x: 52, y: 22 },
  },
  incheon: {
    id: 'incheon',
    name: 'SSG 랜더스필드',
    team: 'SSG 랜더스',
    city: '인천',
    coordinates: { lat: 37.4369, lng: 126.6933 },
    mapPosition: { x: 38, y: 24 },
  },
  suwon: {
    id: 'suwon',
    name: 'KT 위즈 파크',
    team: 'KT 위즈',
    city: '수원',
    coordinates: { lat: 37.2997, lng: 127.0096 },
    mapPosition: { x: 48, y: 30 },
  },
  daegu: {
    id: 'daegu',
    name: '삼성 라이온즈 파크',
    team: '삼성 라이온즈',
    city: '대구',
    coordinates: { lat: 35.8411, lng: 128.6818 },
    mapPosition: { x: 72, y: 52 },
  },
  sajik: {
    id: 'sajik',
    name: '사직 야구장',
    team: '롯데 자이언츠',
    city: '부산',
    coordinates: { lat: 35.1940, lng: 129.0614 },
    mapPosition: { x: 80, y: 70 },
  },
  gwangju: {
    id: 'gwangju',
    name: '광주-기아 챔피언스 필드',
    team: 'KIA 타이거즈',
    city: '광주',
    coordinates: { lat: 35.1681, lng: 126.8890 },
    mapPosition: { x: 32, y: 68 },
  },
  daejeon: {
    id: 'daejeon',
    name: '한화생명 이글스파크',
    team: '한화 이글스',
    city: '대전',
    coordinates: { lat: 36.3171, lng: 127.4289 },
    mapPosition: { x: 48, y: 48 },
  },
  changwon: {
    id: 'changwon',
    name: 'NC 파크',
    team: 'NC 다이노스',
    city: '창원',
    coordinates: { lat: 35.2225, lng: 128.5825 },
    mapPosition: { x: 75, y: 65 },
  },
  gocheok: {
    id: 'gocheok',
    name: '고척 스카이돔',
    team: '키움 히어로즈',
    city: '서울',
    coordinates: { lat: 37.4982, lng: 126.8670 },
    mapPosition: { x: 45, y: 22 },
  },
} as const

export type StadiumId = keyof typeof STADIUMS

/**
 * 경기장 ID로 경기장 정보 가져오기
 */
export function getStadiumInfo(stadiumId: string): StadiumInfo | undefined {
  return STADIUMS[stadiumId as StadiumId]
}

/**
 * 경기장 ID로 지도상 위치 가져오기
 */
export function getStadiumMapPosition(stadiumId: string): { x: number; y: number } {
  return STADIUMS[stadiumId as StadiumId]?.mapPosition || { x: 50, y: 50 }
}

/**
 * 경기장 ID로 실제 좌표 가져오기
 */
export function getStadiumCoordinates(stadiumId: string): { lat: number; lng: number } {
  return STADIUMS[stadiumId as StadiumId]?.coordinates || { lat: 37.5, lng: 127.0 }
}

/**
 * 경기장별 배경 그라데이션 (App.vue용)
 * 각 구장의 홈 팀 시그니처 색상 기반
 */
export const STADIUM_BACKGROUNDS = {
  // 잠실: LG/두산 공용 구장 - 중립 색상
  jamsil: 'linear-gradient(135deg, #1a365d 0%, #2d4a7c 50%, #1e3a5f 100%)',

  // 대구: 삼성 라이온즈 - 블루 계열
  daegu: 'linear-gradient(135deg, #074CA1 0%, #0a5dc2 50%, #063d81 100%)',

  // 수원: KT 위즈 - 블랙 계열
  suwon: 'linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%)',

  // 인천: SSG 랜더스 - 레드 계열
  incheon: 'linear-gradient(135deg, #8B0000 0%, #a52a2a 50%, #6b0000 100%)',

  // 사직: 롯데 자이언츠 - 네이비 계열
  sajik: 'linear-gradient(135deg, #002955 0%, #003d7a 50%, #001f3f 100%)',

  // 광주: KIA 타이거즈 - 레드 계열
  gwangju: 'linear-gradient(135deg, #EA0029 0%, #ff1a47 50%, #c30024 100%)',

  // 대전: 한화 이글스 - 오렌지 계열
  daejeon: 'linear-gradient(135deg, #FF6600 0%, #ff8533 50%, #cc5200 100%)',

  // 창원: NC 다이노스 - 블루/골드 계열
  changwon: 'linear-gradient(135deg, #315288 0%, #4a6fa5 50%, #1e3a5f 100%)',

  // 고척: 키움 히어로즈 - 버건디 계열
  gocheok: 'linear-gradient(135deg, #820024 0%, #a50030 50%, #5d001a 100%)',

  // 기본값 (중립)
  default: 'linear-gradient(135deg, #1a365d 0%, #2d4a7c 50%, #1e3a5f 100%)',
} as const

/**
 * 경기장 ID로 배경 그라데이션 가져오기
 */
export function getStadiumBackground(stadiumId: string): string {
  return STADIUM_BACKGROUNDS[stadiumId as keyof typeof STADIUM_BACKGROUNDS] || STADIUM_BACKGROUNDS.default
}
