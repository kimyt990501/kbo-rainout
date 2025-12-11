"""
KBO 경기 날씨 데이터 수집기 (다중 구장 지원)
=============================================
Open-Meteo API를 사용하여 각 구장의 날씨 데이터를 수집합니다.
API 키 불필요, 무료, 과거 데이터 지원

설치: pip install requests pandas
실행: python weather_collector_openmeteo.py --stadium jamsil
      python weather_collector_openmeteo.py --stadium busan
      python weather_collector_openmeteo.py --all
"""

import argparse
import requests
import pandas as pd
import time
from datetime import datetime, timedelta
from pathlib import Path

from stadium_config import (
    STADIUMS,
    get_stadium_config,
    get_stadium_coordinates,
    get_data_paths,
    get_outdoor_stadiums,
    DEFAULT_STADIUM,
)


# Open-Meteo Historical API
HISTORICAL_URL = "https://archive-api.open-meteo.com/v1/archive"


def get_weather_for_date(date_str, lat, lon, game_hour=18):
    """
    특정 날짜의 기상 데이터 조회

    Args:
        date_str: 날짜 (YYYY-MM-DD 형식)
        lat: 위도
        lon: 경도
        game_hour: 경기 시작 시간 (기본 18시)

    Returns:
        dict: 기상 데이터
    """
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": date_str,
        "end_date": date_str,
        "hourly": [
            "temperature_2m",
            "relative_humidity_2m",
            "precipitation",
            "rain",
            "weather_code",
            "wind_speed_10m",
            "wind_gusts_10m",
        ],
        "daily": [
            "temperature_2m_max",
            "temperature_2m_min",
            "temperature_2m_mean",
            "precipitation_sum",
            "rain_sum",
            "precipitation_hours",
            "wind_speed_10m_max",
            "wind_gusts_10m_max",
        ],
        "timezone": "Asia/Seoul",
    }

    try:
        response = requests.get(HISTORICAL_URL, params=params, timeout=15)

        if response.status_code != 200:
            print(f"    HTTP 오류: {response.status_code}")
            return None

        data = response.json()

        # 일별 데이터
        daily = data.get("daily", {})

        # 시간별 데이터에서 경기 전 시간대 추출 (경기 3시간 전 ~ 경기 시작)
        hourly = data.get("hourly", {})

        # 경기 전 3시간 데이터 (예: 18시 경기면 15~18시)
        start_hour = max(0, game_hour - 3)
        end_hour = game_hour

        pre_game_rain = 0
        pre_game_temps = []
        pre_game_humidity = []
        pre_game_wind = []

        if hourly.get("precipitation"):
            for h in range(start_hour, min(end_hour + 1, 24)):
                if (
                    h < len(hourly["precipitation"])
                    and hourly["precipitation"][h] is not None
                ):
                    pre_game_rain += hourly["precipitation"][h]
                if (
                    h < len(hourly.get("temperature_2m", []))
                    and hourly["temperature_2m"][h] is not None
                ):
                    pre_game_temps.append(hourly["temperature_2m"][h])
                if (
                    h < len(hourly.get("relative_humidity_2m", []))
                    and hourly["relative_humidity_2m"][h] is not None
                ):
                    pre_game_humidity.append(hourly["relative_humidity_2m"][h])
                if (
                    h < len(hourly.get("wind_speed_10m", []))
                    and hourly["wind_speed_10m"][h] is not None
                ):
                    pre_game_wind.append(hourly["wind_speed_10m"][h])

        result = {
            "date": date_str,
            # 일별 데이터
            "daily_temp_max": daily.get("temperature_2m_max", [None])[0],
            "daily_temp_min": daily.get("temperature_2m_min", [None])[0],
            "daily_temp_mean": daily.get("temperature_2m_mean", [None])[0],
            "daily_precip_sum": daily.get("precipitation_sum", [None])[0],
            "daily_rain_sum": daily.get("rain_sum", [None])[0],
            "daily_precip_hours": daily.get("precipitation_hours", [None])[0],
            "daily_wind_max": daily.get("wind_speed_10m_max", [None])[0],
            "daily_wind_gust_max": daily.get("wind_gusts_10m_max", [None])[0],
            # 경기 전 시간대 데이터
            "pre_game_precip": round(pre_game_rain, 2),
            "pre_game_temp": (
                round(sum(pre_game_temps) / len(pre_game_temps), 1)
                if pre_game_temps
                else None
            ),
            "pre_game_humidity": (
                round(sum(pre_game_humidity) / len(pre_game_humidity), 1)
                if pre_game_humidity
                else None
            ),
            "pre_game_wind": (
                round(sum(pre_game_wind) / len(pre_game_wind), 1)
                if pre_game_wind
                else None
            ),
        }

        return result

    except Exception as e:
        print(f"    API 오류: {e}")
        return None


def get_previous_day_rain(date_str, lat, lon):
    """전날 강수량 조회"""
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        prev_date = (date_obj - timedelta(days=1)).strftime("%Y-%m-%d")

        params = {
            "latitude": lat,
            "longitude": lon,
            "start_date": prev_date,
            "end_date": prev_date,
            "daily": ["precipitation_sum"],
            "timezone": "Asia/Seoul",
        }

        response = requests.get(HISTORICAL_URL, params=params, timeout=10)
        data = response.json()

        daily = data.get("daily", {})
        return daily.get("precipitation_sum", [None])[0]

    except:
        return None


def parse_game_time(time_str):
    """경기 시간 파싱"""
    try:
        return int(time_str.split(":")[0])
    except:
        return 18


def collect_weather_data(games_df, lat, lon):
    """
    모든 경기에 대해 날씨 데이터 수집

    Args:
        games_df: 경기 데이터프레임
        lat: 구장 위도
        lon: 구장 경도

    Returns:
        DataFrame: 날씨 데이터
    """
    results = []
    total = len(games_df)

    print(f"\n총 {total}개 경기 날씨 데이터 수집 시작...\n")

    for i, (idx, row) in enumerate(games_df.iterrows()):
        date = row["date"]
        game_hour = parse_game_time(row.get("time", "18:00"))

        print(f"[{i+1}/{total}] {date} ({row.get('time', '')}) ", end="")

        weather = get_weather_for_date(date, lat, lon, game_hour)

        if weather:
            # 전날 강수량 추가
            prev_rain = get_previous_day_rain(date, lat, lon)
            weather["prev_day_precip"] = prev_rain

            results.append(weather)
            print(
                f"✓ 강수={weather.get('daily_precip_sum', 0)}mm, 습도={weather.get('pre_game_humidity', 'N/A')}%"
            )
        else:
            results.append({"date": date})
            print("✗ 데이터 없음")

        # API 호출 제한 방지
        time.sleep(0.3)

    return pd.DataFrame(results)


def collect_stadium_weather(stadium_id, append=False):
    """
    특정 구장의 날씨 데이터 수집

    Args:
        stadium_id: 구장 ID
        append: True면 기존 데이터에 신규 데이터만 추가

    Returns:
        DataFrame: 날씨 포함 경기 데이터
    """
    stadium_config = get_stadium_config(stadium_id)
    stadium_name = stadium_config["name"]
    lat, lon = get_stadium_coordinates(stadium_id)
    paths = get_data_paths(stadium_id)

    print("=" * 60)
    print(f"KBO {stadium_name} 날씨 데이터 수집기 (Open-Meteo)")
    if append:
        print("[APPEND 모드] 신규 경기만 날씨 수집 후 병합합니다.")
    print("=" * 60)
    print("\n• API 키 불필요")
    print(f"• {stadium_name} 좌표 기준")
    print(f"• 위치: {lat}, {lon}")

    # 경기 데이터 로드
    games_file = paths["all_games"]
    if not games_file.exists():
        print(f"\n[오류] {games_file} 파일이 없습니다!")
        print(f"먼저 cancel_crawler.py --stadium {stadium_id} 를 실행하세요.")
        return None

    print(f"\n경기 데이터 로드: {games_file}")
    games_df = pd.read_csv(games_file)
    print(f"총 {len(games_df)}개 경기")

    output_file = paths["with_weather"]
    
    if append and output_file.exists():
        # 기존 with_weather 데이터 로드
        existing_df = pd.read_csv(output_file)
        existing_dates = set(existing_df["date"].unique())
        
        # 신규 경기만 필터링 (날씨 데이터가 없는 경기)
        new_games_df = games_df[~games_df["date"].isin(existing_dates)]
        
        if len(new_games_df) == 0:
            print(f"\n[스킵] 신규 경기가 없습니다. 기존 데이터 유지.")
            return existing_df
        
        print(f"\n[APPEND 모드] 기존 {len(existing_df)}개, 신규 {len(new_games_df)}개 경기 날씨 수집")
        
        # 신규 경기만 날씨 수집
        print("\n" + "=" * 60)
        weather_df = collect_weather_data(new_games_df, lat, lon)
        new_result_df = new_games_df.merge(weather_df, on="date", how="left")
        
        # 기존 데이터와 병합
        result_df = pd.concat([existing_df, new_result_df], ignore_index=True)
        result_df = result_df.drop_duplicates(subset=["date", "home", "away"], keep="last")
        result_df = result_df.sort_values("date").reset_index(drop=True)
    else:
        # 전체 날씨 수집
        print("\n" + "=" * 60)
        weather_df = collect_weather_data(games_df, lat, lon)
        result_df = games_df.merge(weather_df, on="date", how="left")

    # 결과 저장
    output_file.parent.mkdir(parents=True, exist_ok=True)
    result_df.to_csv(output_file, index=False, encoding="utf-8-sig")
    print(f"\n저장 완료: {output_file} ({len(result_df)}개)")

    # 요약 통계
    print_weather_summary(result_df, stadium_name)

    return result_df


def print_weather_summary(result_df, stadium_name):
    """날씨 데이터 요약 출력"""
    print("\n" + "=" * 60)
    print(f"{stadium_name} 수집 완료 - 요약 통계")
    print("=" * 60)

    cancelled = result_df[result_df["cancelled"] == True]
    normal = result_df[result_df["cancelled"] == False]

    print(f"\n전체 경기: {len(result_df)}개")
    print(f"취소 경기: {len(cancelled)}개")
    print(f"정상 경기: {len(normal)}개")

    # 날씨 비교
    if len(cancelled) > 0:
        print("\n[날씨 비교: 취소 vs 정상]")
        print("-" * 50)

        compare_cols = [
            ("daily_precip_sum", "일 강수량(mm)"),
            ("daily_precip_hours", "강수 시간"),
            ("pre_game_precip", "경기전 강수량(mm)"),
            ("pre_game_humidity", "경기전 습도(%)"),
            ("prev_day_precip", "전날 강수량(mm)"),
        ]

        for col, label in compare_cols:
            if col in result_df.columns:
                c_mean = cancelled[col].mean()
                n_mean = normal[col].mean()
                print(f"{label:20} | 취소: {c_mean:8.2f} | 정상: {n_mean:8.2f}")


def collect_all_stadiums_weather(outdoor_only=True):
    """
    모든 구장 날씨 데이터 수집

    Args:
        outdoor_only: 야외 구장만 수집 (돔 제외)

    Returns:
        dict: {stadium_id: DataFrame}
    """
    if outdoor_only:
        stadium_ids = get_outdoor_stadiums()
        print(f"야외 구장 {len(stadium_ids)}개 날씨 데이터 수집 시작...")
    else:
        stadium_ids = list(STADIUMS.keys())
        print(f"전체 구장 {len(stadium_ids)}개 날씨 데이터 수집 시작...")

    results = {}
    for i, stadium_id in enumerate(stadium_ids, 1):
        print(f"\n{'#'*60}")
        print(f"# [{i}/{len(stadium_ids)}] {STADIUMS[stadium_id]['name']}")
        print("#" * 60)

        try:
            result_df = collect_stadium_weather(stadium_id)
            results[stadium_id] = result_df
        except Exception as e:
            print(f"[오류] {stadium_id} 날씨 수집 실패: {e}")
            results[stadium_id] = None

    # 전체 요약
    print("\n" + "=" * 60)
    print("전체 날씨 데이터 수집 결과")
    print("=" * 60)
    print(f"{'구장':<20} {'전체 경기':>10} {'취소 경기':>10} {'상태'}")
    print("-" * 60)

    for stadium_id, df in results.items():
        name = STADIUMS[stadium_id]["name"]
        if df is not None:
            cancelled = len(df[df["cancelled"] == True])
            print(f"{name:<20} {len(df):>10} {cancelled:>10} {'✓'}")
        else:
            print(f"{name:<20} {'N/A':>10} {'N/A':>10} {'✗ 실패'}")

    return results


def main():
    parser = argparse.ArgumentParser(
        description="KBO 경기 날씨 데이터 수집기 (Open-Meteo)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예시:
  python weather_collector_openmeteo.py --stadium jamsil
  python weather_collector_openmeteo.py --stadium busan
  python weather_collector_openmeteo.py --all
  python weather_collector_openmeteo.py --list

참고:
  - 먼저 cancel_crawler.py로 경기 데이터를 수집해야 합니다.
  - API 키 불필요, 무료 사용 가능
        """,
    )

    parser.add_argument(
        "--stadium",
        "-s",
        type=str,
        default=None,
        help="구장 ID (예: jamsil, busan)",
    )
    parser.add_argument(
        "--all",
        "-a",
        action="store_true",
        help="모든 야외 구장 날씨 수집",
    )
    parser.add_argument(
        "--list",
        "-l",
        action="store_true",
        help="지원 구장 목록 출력",
    )
    parser.add_argument(
        "--append",
        action="store_true",
        help="기존 데이터에 신규 경기만 추가 (들어쓰기 대신 병합)",
    )

    args = parser.parse_args()

    # 구장 목록 출력
    if args.list:
        from stadium_config import print_stadium_info

        print_stadium_info()
        return

    # 모든 구장 수집
    if args.all:
        collect_all_stadiums_weather()
        return

    # 특정 구장 수집
    stadium_id = args.stadium or DEFAULT_STADIUM
    collect_stadium_weather(stadium_id, append=args.append)


if __name__ == "__main__":
    main()
