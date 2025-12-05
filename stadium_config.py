"""
KBO 구장 설정
=============
각 구장의 이름, 좌표, 홈팀 정보 등을 관리합니다.

사용법:
    from stadium_config import STADIUMS, get_stadium_config

    # 전체 구장 목록
    for stadium_id, config in STADIUMS.items():
        print(f"{config['name']}: {config['team']}")

    # 특정 구장 설정 가져오기
    config = get_stadium_config('jamsil')
"""

from pathlib import Path

# 프로젝트 루트 디렉토리
PROJECT_ROOT = Path(__file__).parent

# 데이터 디렉토리 (구장별 데이터 저장)
DATA_DIR = PROJECT_ROOT / "data"

# 모델 디렉토리
MODELS_DIR = PROJECT_ROOT / "models"


# ============================================
# 구장 설정
# ============================================
STADIUMS = {
    "jamsil": {
        "id": "jamsil",
        "name": "잠실야구장",
        "search_keyword": "잠실",  # 크롤링 시 검색어
        "team": "LG/두산",
        "lat": 37.5122,
        "lon": 127.0719,
        "capacity": 25553,
    },
    "gocheok": {
        "id": "gocheok",
        "name": "고척스카이돔",
        "search_keyword": "고척",
        "team": "키움",
        "lat": 37.4982,
        "lon": 126.8672,
        "capacity": 16813,
        "dome": True,  # 돔구장 (우천취소 거의 없음)
    },
    "suwon": {
        "id": "suwon",
        "name": "수원KT위즈파크",
        "search_keyword": "수원",
        "team": "KT",
        "lat": 37.2997,
        "lon": 127.0097,
        "capacity": 20000,
    },
    "incheon": {
        "id": "incheon",
        "name": "인천SSG랜더스필드",
        "search_keyword": "문학",  # KBO 홈페이지에서는 "문학"으로 표시
        "team": "SSG",
        "lat": 37.4370,
        "lon": 126.6932,
        "capacity": 23000,
    },
    "daejeon": {
        "id": "daejeon",
        "name": "대전한화생명이글스파크",
        "search_keyword": "대전",
        "team": "한화",
        "lat": 36.3170,
        "lon": 127.4291,
        "capacity": 13000,
    },
    "daegu": {
        "id": "daegu",
        "name": "대구삼성라이온즈파크",
        "search_keyword": "대구",
        "team": "삼성",
        "lat": 35.8411,
        "lon": 128.6815,
        "capacity": 24000,
    },
    "gwangju": {
        "id": "gwangju",
        "name": "광주기아챔피언스필드",
        "search_keyword": "광주",
        "team": "KIA",
        "lat": 35.1681,
        "lon": 126.8891,
        "capacity": 20500,
    },
    "busan": {
        "id": "busan",
        "name": "사직야구장",
        "search_keyword": "사직",
        "team": "롯데",
        "lat": 35.1940,
        "lon": 129.0616,
        "capacity": 24500,
    },
    "changwon": {
        "id": "changwon",
        "name": "창원NC파크",
        "search_keyword": "창원",
        "team": "NC",
        "lat": 35.2225,
        "lon": 128.5822,
        "capacity": 22000,
    },
}


# ============================================
# 기본값
# ============================================
DEFAULT_STADIUM = "jamsil"

# 수집 대상 연도 (기본값)
DEFAULT_YEARS = [2019, 2020, 2021, 2022, 2023, 2024]

# 수집 대상 월 (정규시즌: 3~10월)
DEFAULT_MONTHS = list(range(3, 11))


# ============================================
# 헬퍼 함수
# ============================================
def get_stadium_config(stadium_id: str) -> dict:
    """
    구장 ID로 설정 가져오기

    Args:
        stadium_id: 구장 ID (예: "jamsil", "busan")

    Returns:
        dict: 구장 설정

    Raises:
        ValueError: 지원하지 않는 구장 ID
    """
    if stadium_id not in STADIUMS:
        available = ", ".join(STADIUMS.keys())
        raise ValueError(f"지원하지 않는 구장: {stadium_id}. 가능한 구장: {available}")
    return STADIUMS[stadium_id]


def get_stadium_coordinates(stadium_id: str) -> tuple:
    """구장 좌표 반환 (lat, lon)"""
    config = get_stadium_config(stadium_id)
    return config["lat"], config["lon"]


def get_all_stadium_ids() -> list:
    """모든 구장 ID 목록 반환"""
    return list(STADIUMS.keys())


def get_outdoor_stadiums() -> list:
    """야외 구장만 반환 (돔 구장 제외)"""
    return [
        stadium_id
        for stadium_id, config in STADIUMS.items()
        if not config.get("dome", False)
    ]


def get_data_paths(stadium_id: str) -> dict:
    """
    구장별 데이터 파일 경로 반환

    Returns:
        dict: {
            "dir": 구장 데이터 디렉토리,
            "all_games": 전체 경기 CSV 경로,
            "cancelled": 취소 경기 CSV 경로,
            "with_weather": 날씨 포함 CSV 경로,
            "model": 모델 파일 경로
        }
    """
    # 구장별 데이터 디렉토리 (data/jamsil/, data/daegu/ 등)
    stadium_data_dir = DATA_DIR / stadium_id
    stadium_data_dir.mkdir(parents=True, exist_ok=True)
    MODELS_DIR.mkdir(exist_ok=True)

    return {
        "dir": stadium_data_dir,
        "all_games": stadium_data_dir / "all_games.csv",
        "cancelled": stadium_data_dir / "cancelled_games.csv",
        "with_weather": stadium_data_dir / "with_weather.csv",
        "model": MODELS_DIR / f"kbo_{stadium_id}_model.pkl",
    }


def print_stadium_info():
    """모든 구장 정보 출력"""
    print("=" * 70)
    print("KBO 구장 목록")
    print("=" * 70)
    print(f"{'ID':<12} {'구장명':<25} {'홈팀':<10} {'좌표'}")
    print("-" * 70)
    for stadium_id, config in STADIUMS.items():
        dome = " [돔]" if config.get("dome", False) else ""
        print(
            f"{stadium_id:<12} {config['name']:<25} {config['team']:<10} "
            f"({config['lat']}, {config['lon']}){dome}"
        )
    print("=" * 70)


if __name__ == "__main__":
    print_stadium_info()

    print("\n야외 구장만:")
    for sid in get_outdoor_stadiums():
        print(f"  - {sid}: {STADIUMS[sid]['name']}")
