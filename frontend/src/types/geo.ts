/**
 * GeoJSON 타입 정의
 */

/**
 * GeoJSON Geometry 타입
 */
export type GeoJSONGeometry =
  | {
      type: 'Point'
      coordinates: [number, number]
    }
  | {
      type: 'LineString'
      coordinates: Array<[number, number]>
    }
  | {
      type: 'Polygon'
      coordinates: Array<Array<[number, number]>>
    }
  | {
      type: 'MultiPoint'
      coordinates: Array<[number, number]>
    }
  | {
      type: 'MultiLineString'
      coordinates: Array<Array<[number, number]>>
    }
  | {
      type: 'MultiPolygon'
      coordinates: Array<Array<Array<[number, number]>>>
    }
  | {
      type: 'GeometryCollection'
      geometries: GeoJSONGeometry[]
    }

/**
 * GeoJSON Feature Properties
 * 한국 행정구역 데이터용
 */
export interface KoreaProvinceProperties {
  NAME_1?: string // 영문 시도명
  name?: string // 한글 시도명
  HASC_1?: string // 행정구역 코드
  TYPE_1?: string // 행정구역 유형
  ENGTYPE_1?: string // 영문 행정구역 유형
  [key: string]: unknown // 기타 속성
}

/**
 * GeoJSON Feature
 */
export interface GeoJSONFeature<P = KoreaProvinceProperties> {
  type: 'Feature'
  id?: string | number
  properties: P
  geometry: GeoJSONGeometry
}

/**
 * GeoJSON FeatureCollection
 */
export interface GeoJSONFeatureCollection<P = KoreaProvinceProperties> {
  type: 'FeatureCollection'
  features: Array<GeoJSONFeature<P>>
}

/**
 * SVG Path 데이터
 */
export interface ProvincePath {
  name: string
  path: string
}

/**
 * 지도 투영 설정
 */
export interface MapProjectionConfig {
  center: [number, number] // [경도, 위도]
  scale: number
  translate: [number, number] // [x, y]
}

/**
 * 대한민국 기본 지도 설정
 */
export const KOREA_MAP_CONFIG: MapProjectionConfig = {
  center: [127.5, 36.5], // 대한민국 중심
  scale: 8000,
  translate: [400, 450],
}
