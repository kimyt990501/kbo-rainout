/**
 * KBO 팀 정보 상수
 */

export interface TeamInfo {
  id: string
  name: string
  shortName: string
  color: string
  backgroundColor: string
}

export const TEAMS = {
  lg: {
    id: 'lg',
    name: 'LG 트윈스',
    shortName: 'LG',
    color: '#C30452',
    backgroundColor: '#C30452',
  },
  doosan: {
    id: 'doosan',
    name: '두산 베어스',
    shortName: '두산',
    color: '#131230',
    backgroundColor: '#131230',
  },
  samsung: {
    id: 'samsung',
    name: '삼성 라이온즈',
    shortName: '삼성',
    color: '#074CA1',
    backgroundColor: '#074CA1',
  },
  kt: {
    id: 'kt',
    name: 'KT 위즈',
    shortName: 'KT',
    color: '#000000',
    backgroundColor: '#000000',
  },
  ssg: {
    id: 'ssg',
    name: 'SSG 랜더스',
    shortName: 'SSG',
    color: '#CE0E2D',
    backgroundColor: '#CE0E2D',
  },
  kia: {
    id: 'kia',
    name: 'KIA 타이거즈',
    shortName: 'KIA',
    color: '#EA0029',
    backgroundColor: '#EA0029',
  },
  nc: {
    id: 'nc',
    name: 'NC 다이노스',
    shortName: 'NC',
    color: '#315288',
    backgroundColor: '#315288',
  },
  lotte: {
    id: 'lotte',
    name: '롯데 자이언츠',
    shortName: '롯데',
    color: '#041E42',
    backgroundColor: '#041E42',
  },
  hanwha: {
    id: 'hanwha',
    name: '한화 이글스',
    shortName: '한화',
    color: '#FF6600',
    backgroundColor: '#FF6600',
  },
  kiwoom: {
    id: 'kiwoom',
    name: '키움 히어로즈',
    shortName: '키움',
    color: '#570514',
    backgroundColor: '#570514',
  },
} as const

export type TeamId = keyof typeof TEAMS

/**
 * 팀 ID로 팀 정보 가져오기
 */
export function getTeamInfo(teamId: string): TeamInfo | undefined {
  return TEAMS[teamId as TeamId]
}

/**
 * 팀 ID로 팀 컬러 가져오기
 */
export function getTeamColor(teamId: string): string {
  return TEAMS[teamId as TeamId]?.color || '#666666'
}

/**
 * 팀 ID로 배경색 가져오기
 */
export function getTeamBackgroundColor(teamId: string): string {
  return TEAMS[teamId as TeamId]?.backgroundColor || '#666666'
}

/**
 * 구장별 홈 팀 매핑
 */
export const STADIUM_HOME_TEAMS = {
  jamsil: 'lg',
  incheon: 'ssg',
  suwon: 'kt',
  daegu: 'samsung',
  busan: 'lotte',
  gwangju: 'kia',
  daejeon: 'hanwha',
  changwon: 'nc',
  gocheok: 'kiwoom',
} as const

export type StadiumId = keyof typeof STADIUM_HOME_TEAMS

/**
 * 구장 ID로 홈 팀 정보 가져오기
 */
export function getStadiumHomeTeam(stadiumId: string) {
  const teamId = STADIUM_HOME_TEAMS[stadiumId as StadiumId]
  if (!teamId) return undefined

  const team = TEAMS[teamId]
  return team ? {
    id: team.id,
    name: team.name  // 풀네임 사용
  } : undefined
}
