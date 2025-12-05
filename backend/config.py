"""
KBO 우천취소 예측 API 설정

[새 구장 모델 추가 방법]
1. 아래 STADIUM_MODELS 딕셔너리에 새 구장 정보 추가
2. 모델 파일(.pkl)을 지정된 경로에 배치
3. 서버 재시작 시 자동으로 로딩됨
"""
import os
from pathlib import Path

# 프로젝트 경로
PROJECT_ROOT = Path(__file__).parent.parent
BACKEND_ROOT = Path(__file__).parent

# Docker 환경에서 모델 디렉토리 오버라이드 (환경 변수)
# - Docker: MODEL_DIR=/app/models_data (docker-compose.yml에서 설정)
# - 로컬: MODEL_DIR 미설정 시 PROJECT_ROOT/models 사용
MODEL_DIR = Path(os.environ.get("MODEL_DIR", str(PROJECT_ROOT / "models")))

# API 설정
API_VERSION = "1.1.0"
API_TITLE = "KBO 우천취소 예측 API"
API_DESCRIPTION = "KBO 야구장 경기 우천취소 확률을 예측하는 API (다중 구장 지원)"

# =============================================================================
# 구장별 모델 설정
# =============================================================================
# 새 구장 추가 시 아래 형식으로 추가:
# "구장_id": {
#     "path": Path("모델 파일 경로"),
#     "name": "구장 한글명",
#     "team": "홈팀명",
#     "coordinates": (위도, 경도),  # 날씨 API 호출용
# }
# =============================================================================

STADIUM_MODELS = {
    "jamsil": {
        "path": MODEL_DIR / "kbo_jamsil_model.pkl",
        "name": "잠실야구장",
        "team": "LG/두산",
        "coordinates": (37.5122, 127.0719),
    },
    "daegu": {
        "path": MODEL_DIR / "kbo_daegu_model.pkl",
        "name": "대구삼성라이온즈파크",
        "team": "삼성",
        "coordinates": (35.8411, 128.6815),
    },
    "suwon": {
        "path": MODEL_DIR / "kbo_suwon_model.pkl",
        "name": "수원KT위즈파크",
        "team": "KT",
        "coordinates": (37.2997, 127.0097),
    },
    "incheon": {
        "path": MODEL_DIR / "kbo_incheon_model.pkl",
        "name": "인천SSG랜더스필드",
        "team": "SSG",
        "coordinates": (37.4370, 126.6932),
    },
    # 향후 추가 예정:
    # "sajik": {
    #     "path": PROJECT_ROOT / "models" / "kbo_rain_model_sajik.pkl",
    #     "name": "사직야구장",
    #     "team": "롯데",
    #     "coordinates": (35.1940, 129.0616),
    # },
    # "munhak": {
    #     "path": PROJECT_ROOT / "models" / "kbo_rain_model_munhak.pkl",
    #     "name": "문학야구장",
    #     "team": "SSG",
    #     "coordinates": (37.4370, 126.6933),
    # },
    # "gwangju": {
    #     "path": PROJECT_ROOT / "models" / "kbo_rain_model_gwangju.pkl",
    #     "name": "광주챔피언스필드",
    #     "team": "KIA",
    #     "coordinates": (35.1681, 126.8891),
    # },
    # "daegu": {
    #     "path": PROJECT_ROOT / "models" / "kbo_rain_model_daegu.pkl",
    #     "name": "대구삼성라이온즈파크",
    #     "team": "삼성",
    #     "coordinates": (35.8411, 128.6816),
    # },
    # "daejeon": {
    #     "path": PROJECT_ROOT / "models" / "kbo_rain_model_daejeon.pkl",
    #     "name": "한화생명이글스파크",
    #     "team": "한화",
    #     "coordinates": (36.3170, 127.4291),
    # },
    # "suwon": {
    #     "path": PROJECT_ROOT / "models" / "kbo_rain_model_suwon.pkl",
    #     "name": "수원KT위즈파크",
    #     "team": "KT",
    #     "coordinates": (37.2997, 127.0097),
    # },
    # "changwon": {
    #     "path": PROJECT_ROOT / "models" / "kbo_rain_model_changwon.pkl",
    #     "name": "창원NC파크",
    #     "team": "NC",
    #     "coordinates": (35.2225, 128.5822),
    # },
    # "gocheok": {
    #     "path": PROJECT_ROOT / "models" / "kbo_rain_model_gocheok.pkl",
    #     "name": "고척스카이돔",
    #     "team": "키움",
    #     "coordinates": (37.4982, 126.8672),
    # },
}

# 지원 구장 목록 (자동 생성)
SUPPORTED_STADIUMS = list(STADIUM_MODELS.keys())

# 기본 구장
DEFAULT_STADIUM = "jamsil"

# CORS 설정
CORS_ORIGINS = [
    "http://localhost:8080",
    "http://localhost:5173",
    "http://127.0.0.1:8080",
    "http://127.0.0.1:5173",
]

# 예측 임계값
THRESHOLD_HIGH = 0.8  # 취소 가능성 높음
THRESHOLD_MEDIUM = 0.5  # 취소 가능성 있음

# 위험 요소 임계값
RISK_THRESHOLDS = {
    "pre_game_precip": 10.0,  # mm
    "daily_precip_sum": 20.0,  # mm
    "pre_game_humidity": 85.0,  # %
    "prev_day_precip": 15.0,  # mm
    "daily_wind_max": 15.0,  # m/s
}

# 장마철 월
RAINY_SEASON_MONTHS = [7, 8]
