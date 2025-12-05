#!/usr/bin/env python3
"""
KBO 우천취소 예측 파이프라인
============================
전체 데이터 수집 및 모델 학습 파이프라인을 실행합니다.

사용법:
    # 특정 구장만 처리
    python run_pipeline.py --stadium jamsil
    python run_pipeline.py --stadium busan

    # 모든 야외 구장 처리
    python run_pipeline.py --all

    # 특정 단계만 실행
    python run_pipeline.py --stadium jamsil --step crawl      # 크롤링만
    python run_pipeline.py --stadium jamsil --step weather    # 날씨 수집만
    python run_pipeline.py --stadium jamsil --step model      # 모델 학습만

    # 연도 지정
    python run_pipeline.py --stadium jamsil --years 2023 2024
"""

import argparse
import time
from datetime import datetime

from stadium_config import (
    STADIUMS,
    get_stadium_config,
    get_data_paths,
    get_outdoor_stadiums,
    DEFAULT_STADIUM,
    DEFAULT_YEARS,
    DEFAULT_MONTHS,
)


def run_crawl(stadium_id, years=None, months=None):
    """1단계: 경기 데이터 크롤링"""
    from cancel_crawler import crawl_stadium

    print("\n" + "=" * 60)
    print(f"[1단계] 경기 데이터 크롤링: {STADIUMS[stadium_id]['name']}")
    print("=" * 60)

    return crawl_stadium(stadium_id, years=years, months=months)


def run_weather(stadium_id):
    """2단계: 날씨 데이터 수집"""
    from weather_collector_openmeteo import collect_stadium_weather

    print("\n" + "=" * 60)
    print(f"[2단계] 날씨 데이터 수집: {STADIUMS[stadium_id]['name']}")
    print("=" * 60)

    return collect_stadium_weather(stadium_id)


def run_model(stadium_id):
    """3단계: 모델 학습"""
    from kbo_rain_model import train_stadium_model

    print("\n" + "=" * 60)
    print(f"[3단계] 모델 학습: {STADIUMS[stadium_id]['name']}")
    print("=" * 60)

    return train_stadium_model(stadium_id)


def run_full_pipeline(stadium_id, years=None, months=None):
    """전체 파이프라인 실행"""
    stadium_name = STADIUMS[stadium_id]["name"]
    start_time = datetime.now()

    print("\n" + "#" * 60)
    print(f"# {stadium_name} 전체 파이프라인 시작")
    print(f"# 시작 시간: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print("#" * 60)

    results = {
        "stadium_id": stadium_id,
        "stadium_name": stadium_name,
        "crawl": None,
        "weather": None,
        "model": None,
    }

    try:
        # 1단계: 크롤링
        all_games, cancelled_games = run_crawl(stadium_id, years, months)
        results["crawl"] = {
            "total": len(all_games),
            "cancelled": len(cancelled_games),
            "success": len(all_games) > 0,
        }

        if len(all_games) == 0:
            print(f"\n[중단] 수집된 경기가 없어 파이프라인을 중단합니다.")
            return results

        # 2단계: 날씨 수집
        weather_df = run_weather(stadium_id)
        results["weather"] = {
            "total": len(weather_df) if weather_df is not None else 0,
            "success": weather_df is not None,
        }

        if weather_df is None:
            print(f"\n[중단] 날씨 데이터 수집 실패로 파이프라인을 중단합니다.")
            return results

        # 3단계: 모델 학습
        model_result = run_model(stadium_id)
        if model_result is not None:
            results["model"] = {
                "success": True,
                "model_path": str(model_result["model_path"]),
            }
        else:
            results["model"] = {"success": False, "reason": "학습 실패 또는 데이터 부족"}

    except Exception as e:
        print(f"\n[오류] 파이프라인 실행 중 오류 발생: {e}")
        import traceback

        traceback.print_exc()

    end_time = datetime.now()
    duration = end_time - start_time

    print("\n" + "#" * 60)
    print(f"# {stadium_name} 파이프라인 완료")
    print(f"# 종료 시간: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"# 소요 시간: {duration}")
    print("#" * 60)

    return results


def run_all_stadiums(years=None, months=None, outdoor_only=True):
    """모든 구장 파이프라인 실행"""
    if outdoor_only:
        stadium_ids = get_outdoor_stadiums()
        print(f"\n야외 구장 {len(stadium_ids)}개 파이프라인 시작...")
    else:
        stadium_ids = list(STADIUMS.keys())
        print(f"\n전체 구장 {len(stadium_ids)}개 파이프라인 시작...")

    total_start = datetime.now()
    all_results = {}

    for i, stadium_id in enumerate(stadium_ids, 1):
        print(f"\n{'='*60}")
        print(f"[{i}/{len(stadium_ids)}] {STADIUMS[stadium_id]['name']} 처리 중...")
        print("=" * 60)

        results = run_full_pipeline(stadium_id, years, months)
        all_results[stadium_id] = results

        # 다음 구장 처리 전 잠시 대기 (API 부하 방지)
        if i < len(stadium_ids):
            print("\n다음 구장 처리 전 10초 대기...")
            time.sleep(10)

    total_end = datetime.now()
    total_duration = total_end - total_start

    # 전체 결과 요약
    print("\n" + "=" * 70)
    print("전체 파이프라인 결과 요약")
    print("=" * 70)
    print(f"{'구장':<20} {'크롤링':>12} {'날씨':>10} {'모델':>10}")
    print("-" * 70)

    for stadium_id, results in all_results.items():
        name = STADIUMS[stadium_id]["name"]
        crawl_status = f"{results['crawl']['total']}개" if results["crawl"] else "실패"
        weather_status = "성공" if results.get("weather", {}).get("success") else "실패"
        model_status = "성공" if results.get("model", {}).get("success") else "실패"
        print(f"{name:<20} {crawl_status:>12} {weather_status:>10} {model_status:>10}")

    print("-" * 70)
    print(f"총 소요 시간: {total_duration}")
    print("=" * 70)

    return all_results


def main():
    parser = argparse.ArgumentParser(
        description="KBO 우천취소 예측 파이프라인",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예시:
  # 특정 구장 전체 파이프라인
  python run_pipeline.py --stadium jamsil
  python run_pipeline.py --stadium busan --years 2023 2024

  # 모든 야외 구장
  python run_pipeline.py --all

  # 특정 단계만
  python run_pipeline.py --stadium jamsil --step crawl
  python run_pipeline.py --stadium jamsil --step weather
  python run_pipeline.py --stadium jamsil --step model

지원 구장:
  jamsil, suwon, incheon, daejeon, daegu, gwangju, busan, changwon
  (gocheok 고척돔은 돔구장이라 제외)
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
        "--years",
        "-y",
        type=int,
        nargs="+",
        default=None,
        help="수집 연도 (예: 2023 2024)",
    )
    parser.add_argument(
        "--months",
        "-m",
        type=int,
        nargs="+",
        default=None,
        help="수집 월 (예: 3 4 5 6 7 8 9 10)",
    )
    parser.add_argument(
        "--all",
        "-a",
        action="store_true",
        help="모든 야외 구장 처리",
    )
    parser.add_argument(
        "--step",
        type=str,
        choices=["crawl", "weather", "model"],
        default=None,
        help="특정 단계만 실행 (crawl/weather/model)",
    )
    parser.add_argument(
        "--list",
        "-l",
        action="store_true",
        help="지원 구장 목록 출력",
    )

    args = parser.parse_args()

    # 구장 목록 출력
    if args.list:
        from stadium_config import print_stadium_info

        print_stadium_info()
        return

    # 모든 구장 처리
    if args.all:
        run_all_stadiums(years=args.years, months=args.months)
        return

    # 특정 구장 처리
    stadium_id = args.stadium or DEFAULT_STADIUM

    # 구장 유효성 검사
    if stadium_id not in STADIUMS:
        print(f"[오류] 지원하지 않는 구장: {stadium_id}")
        print(f"지원 구장: {', '.join(STADIUMS.keys())}")
        return

    # 특정 단계만 실행
    if args.step == "crawl":
        run_crawl(stadium_id, years=args.years, months=args.months)
    elif args.step == "weather":
        run_weather(stadium_id)
    elif args.step == "model":
        run_model(stadium_id)
    else:
        # 전체 파이프라인
        run_full_pipeline(stadium_id, years=args.years, months=args.months)


if __name__ == "__main__":
    main()
