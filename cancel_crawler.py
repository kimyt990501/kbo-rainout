"""
KBO 우천취소 데이터 수집기 (다중 구장 지원)
============================================
지정된 구장의 경기 일정 및 취소 데이터를 크롤링합니다.

설치: pip install selenium webdriver-manager beautifulsoup4 pandas
실행: python cancel_crawler.py --stadium jamsil
      python cancel_crawler.py --stadium busan --years 2023 2024
      python cancel_crawler.py --all  # 모든 야외 구장
"""

import time
import re
import argparse
import pandas as pd
from datetime import datetime
import os

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup

from stadium_config import (
    STADIUMS,
    get_stadium_config,
    get_data_paths,
    get_outdoor_stadiums,
    DEFAULT_YEARS,
    DEFAULT_MONTHS,
    DEFAULT_STADIUM,
)


def crawl_kbo_schedule(years, months, stadium_id):
    """
    KBO 홈페이지에서 경기 일정 크롤링

    Args:
        years: 수집 연도 리스트 (예: [2019, 2020, ...])
        months: 수집 월 리스트 (예: [3, 4, ..., 10])
        stadium_id: 구장 ID (예: "jamsil", "busan")

    Returns:
        tuple: (전체 경기 리스트, 취소 경기 리스트)
    """
    # 구장 설정 가져오기
    stadium_config = get_stadium_config(stadium_id)
    search_keyword = stadium_config["search_keyword"]
    # 리스트로 통일 (하위 호환성)
    if isinstance(search_keyword, str):
        target_keywords = [search_keyword]
    else:
        target_keywords = search_keyword
    stadium_name = stadium_config["name"]

    print(f"\n대상 구장: {stadium_name} (검색어: {target_keywords})")

    # Chrome 옵션 설정
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--lang=ko_KR")
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (Macintosh; Apple Silicon Mac OS X) AppleWebKit/537.36"
    )

    # WebDriver 설정
    print("Chrome WebDriver 설정 중...")
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)

    all_games = []
    cancelled_games = []

    try:
        for year in years:
            for month in months:
                print(f"\n{'='*50}")
                print(f"크롤링 중: {year}년 {month}월 ({stadium_name})")
                print("=" * 50)

                url = "https://www.koreabaseball.com/Schedule/Schedule.aspx"
                driver.get(url)
                time.sleep(2)

                try:
                    # 1. 시리즈 선택 (정규시즌: "0,9,6")
                    series_dropdown = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.ID, "ddlSeries"))
                    )
                    series_select = Select(series_dropdown)
                    series_select.select_by_value("0,9,6")  # 정규시즌
                    time.sleep(1)
                    print("  시리즈: 정규시즌 선택")

                    # 2. 연도 선택
                    year_dropdown = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.ID, "ddlYear"))
                    )
                    year_select = Select(year_dropdown)
                    year_select.select_by_value(str(year))
                    time.sleep(1)
                    print(f"  연도: {year} 선택")

                    # 3. 월 선택
                    month_dropdown = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.ID, "ddlMonth"))
                    )
                    month_select = Select(month_dropdown)
                    month_select.select_by_value(str(month).zfill(2))
                    time.sleep(2)
                    print(f"  월: {month} 선택")

                except Exception as e:
                    print(f"드롭다운 선택 실패: {e}")
                    continue

                # 페이지 파싱
                page_source = driver.page_source
                soup = BeautifulSoup(page_source, "html.parser")

                # 테이블 찾기
                table = soup.find("table", id="tblScheduleList")
                if not table:
                    print("  테이블(tblScheduleList)을 찾을 수 없음")
                    continue

                tbody = table.find("tbody")
                if not tbody:
                    print("  tbody를 찾을 수 없음")
                    continue

                rows = tbody.find_all("tr")

                # "데이터가 없습니다" 체크
                if len(rows) == 1 and "데이터가 없습니다" in rows[0].get_text():
                    print("  데이터 없음")
                    continue

                print(f"  {len(rows)}개 행 발견")

                current_date = None
                current_day = ""

                for row in rows:
                    cells = row.find_all("td")
                    if len(cells) < 8:
                        continue

                    # 날짜 셀 확인 (rowspan으로 합쳐진 경우 셀 수가 다름)
                    # 9개 셀: 날짜 포함 행 (날짜, 시간, 경기, 게임센터, 하이라이트, TV, 라디오, 구장, 비고)
                    # 8개 셀: 날짜 없는 행 (시간, 경기, 게임센터, 하이라이트, TV, 라디오, 구장, 비고)
                    has_date_cell = len(cells) == 9

                    # 인덱스 오프셋 설정
                    offset = 0 if has_date_cell else -1

                    # 날짜 처리
                    if has_date_cell:
                        date_cell = cells[0]
                        date_text = date_cell.get_text(strip=True)

                        if date_text and re.search(r"\d+\.\d+", date_text):
                            match = re.search(r"(\d+)\.(\d+)", date_text)
                            if match:
                                m, d = match.groups()
                                current_date = f"{year}-{m.zfill(2)}-{d.zfill(2)}"
                                day_match = re.search(r"\((.)\)", date_text)
                                current_day = day_match.group(1) if day_match else ""

                    if not current_date:
                        continue

                    # 시간 (날짜 있으면 index 1, 없으면 index 0)
                    time_idx = 1 + offset
                    time_text = cells[time_idx].get_text(strip=True) if len(cells) > time_idx else ""

                    # 경기 정보 (날짜 있으면 index 2, 없으면 index 1)
                    game_idx = 2 + offset
                    game_cell = cells[game_idx] if len(cells) > game_idx else None
                    away_team = ""
                    home_team = ""

                    if game_cell:
                        # 팀 이미지 alt 속성에서 팀명 추출
                        team_imgs = game_cell.find_all("img")
                        if len(team_imgs) >= 2:
                            away_team = team_imgs[0].get("alt", "")
                            home_team = team_imgs[1].get("alt", "")
                        else:
                            # 텍스트에서 추출 (점수 제거: "KIA9vs5삼성" -> "KIA vs 삼성")
                            game_text = game_cell.get_text(strip=True)
                            # 점수 포함된 패턴: "팀명+점수 vs 점수+팀명" 또는 "팀명 vs 팀명"
                            teams_match = re.search(
                                r"([가-힣A-Za-z]+)\d*\s*(?:vs|VS)\s*\d*([가-힣A-Za-z]+)", game_text
                            )
                            if teams_match:
                                away_team = teams_match.group(1)
                                home_team = teams_match.group(2)

                    # 구장 (날짜 있으면 index 7, 없으면 index 6)
                    stadium_idx = 7 + offset
                    stadium = cells[stadium_idx].get_text(strip=True) if len(cells) > stadium_idx else ""

                    # 비고 (날짜 있으면 index 8, 없으면 index 7)
                    note_idx = 8 + offset
                    note = cells[note_idx].get_text(strip=True) if len(cells) > note_idx else ""

                    # 대상 구장 필터링 (여러 키워드 중 하나라도 포함되면 매칭)
                    if target_keywords and not any(kw in stadium for kw in target_keywords):
                        continue

                    # 전체 행 텍스트
                    row_text = row.get_text()

                    # 취소 여부 확인
                    cancel_keywords = ["취소", "우천", "순연", "그라운드", "노게임", "폭염"]
                    is_cancelled = any(keyword in row_text for keyword in cancel_keywords)

                    # 취소 사유 판단
                    if "우천" in row_text and "노게임" in row_text:
                        cancel_reason = "우천노게임"
                    elif "우천" in row_text:
                        cancel_reason = "우천취소"
                    elif "그라운드" in row_text:
                        cancel_reason = "그라운드사정"
                    elif "폭염" in row_text:
                        cancel_reason = "폭염취소"
                    elif "순연" in row_text:
                        cancel_reason = "순연"
                    elif is_cancelled:
                        cancel_reason = "기타취소"
                    else:
                        cancel_reason = "정상진행"

                    game_info = {
                        "date": current_date,
                        "day": current_day,
                        "time": time_text,
                        "stadium": stadium,
                        "stadium_id": stadium_id,
                        "home": home_team,
                        "away": away_team,
                        "cancelled": is_cancelled,
                        "reason": cancel_reason,
                        "note": note,
                    }

                    all_games.append(game_info)

                    if is_cancelled:
                        cancelled_games.append(game_info)
                        print(
                            f"  [취소] {current_date} | {stadium} | {away_team} vs {home_team} | {cancel_reason}"
                        )
                    else:
                        print(
                            f"  [정상] {current_date} | {stadium} | {away_team} vs {home_team}"
                        )

                time.sleep(1)

    except Exception as e:
        print(f"크롤링 중 오류 발생: {e}")
        import traceback

        traceback.print_exc()

    finally:
        driver.quit()
        print("\nWebDriver 종료")

    return all_games, cancelled_games


def save_results(all_games, cancelled_games, stadium_id, append=False):
    """
    결과를 CSV 파일로 저장

    Args:
        all_games: 전체 경기 리스트
        cancelled_games: 취소 경기 리스트
        stadium_id: 구장 ID
        append: True면 기존 데이터에 추가, False면 덮어쓰기
    """
    paths = get_data_paths(stadium_id)
    stadium_config = get_stadium_config(stadium_id)
    stadium_name = stadium_config["name"]

    if all_games:
        df_new = pd.DataFrame(all_games)
        all_path = paths["all_games"]
        all_path.parent.mkdir(parents=True, exist_ok=True)
        
        if append and all_path.exists():
            # 기존 데이터 로드 후 병합
            df_existing = pd.read_csv(all_path)
            df_all = pd.concat([df_existing, df_new], ignore_index=True)
            # 중복 제거 (날짜 + 홈팀 + 원정팀 기준)
            df_all = df_all.drop_duplicates(subset=["date", "home", "away"], keep="last")
            df_all = df_all.sort_values("date").reset_index(drop=True)
            print(f"\n[APPEND 모드] 기존 {len(df_existing)}개 + 신규 {len(df_new)}개 = 총 {len(df_all)}개")
        else:
            df_all = df_new
        
        df_all.to_csv(all_path, index=False, encoding="utf-8-sig")
        print(f"전체 경기 저장: {all_path} ({len(df_all)}개)")

    if cancelled_games:
        df_cancelled_new = pd.DataFrame(cancelled_games)
        cancelled_path = paths["cancelled"]
        
        if append and cancelled_path.exists():
            df_existing = pd.read_csv(cancelled_path)
            df_cancelled = pd.concat([df_existing, df_cancelled_new], ignore_index=True)
            df_cancelled = df_cancelled.drop_duplicates(subset=["date", "home", "away"], keep="last")
            df_cancelled = df_cancelled.sort_values("date").reset_index(drop=True)
        else:
            df_cancelled = df_cancelled_new
        
        df_cancelled.to_csv(cancelled_path, index=False, encoding="utf-8-sig")
        print(f"취소 경기 저장: {cancelled_path} ({len(df_cancelled)}개)")

        print("\n" + "=" * 60)
        print(f"{stadium_name} 취소 경기 요약")
        print("=" * 60)
        print(f"총 취소 경기: {len(df_cancelled)}개")

        df_cancelled["year"] = pd.to_datetime(df_cancelled["date"]).dt.year
        print("\n연도별:")
        print(df_cancelled.groupby("year").size())
        print("\n취소 사유별:")
        print(df_cancelled["reason"].value_counts())
    else:
        print(f"\n{stadium_name}: 취소된 경기가 없습니다.")


def crawl_stadium(stadium_id, years=None, months=None, append=False):
    """
    특정 구장의 데이터 수집

    Args:
        stadium_id: 구장 ID
        years: 연도 리스트 (기본값: DEFAULT_YEARS)
        months: 월 리스트 (기본값: DEFAULT_MONTHS)
        append: True면 기존 데이터에 추가

    Returns:
        tuple: (전체 경기 리스트, 취소 경기 리스트)
    """
    years = years or DEFAULT_YEARS
    months = months or DEFAULT_MONTHS

    stadium_config = get_stadium_config(stadium_id)
    stadium_name = stadium_config["name"]

    print("=" * 60)
    print(f"KBO {stadium_name} 경기 데이터 수집기")
    if append:
        print("[APPEND 모드] 기존 데이터에 추가합니다.")
    print("=" * 60)

    print(f"\n수집 대상: {years[0]}~{years[-1]}년")
    print(f"대상 구장: {stadium_name} ({stadium_config['team']})")
    print("크롤링을 시작합니다...\n")

    all_games, cancelled_games = crawl_kbo_schedule(
        years=years, months=months, stadium_id=stadium_id
    )

    save_results(all_games, cancelled_games, stadium_id, append=append)

    print("\n" + "=" * 60)
    print(f"{stadium_name} 수집 완료!")
    print("=" * 60)

    return all_games, cancelled_games


def crawl_all_stadiums(years=None, months=None, outdoor_only=True):
    """
    모든 구장 데이터 수집

    Args:
        years: 연도 리스트
        months: 월 리스트
        outdoor_only: 야외 구장만 수집 (돔 제외)

    Returns:
        dict: {stadium_id: (all_games, cancelled_games)}
    """
    if outdoor_only:
        stadium_ids = get_outdoor_stadiums()
        print(f"야외 구장 {len(stadium_ids)}개 수집 시작...")
    else:
        stadium_ids = list(STADIUMS.keys())
        print(f"전체 구장 {len(stadium_ids)}개 수집 시작...")

    results = {}
    for i, stadium_id in enumerate(stadium_ids, 1):
        print(f"\n{'#'*60}")
        print(f"# [{i}/{len(stadium_ids)}] {STADIUMS[stadium_id]['name']}")
        print("#" * 60)

        try:
            all_games, cancelled_games = crawl_stadium(stadium_id, years, months)
            results[stadium_id] = (all_games, cancelled_games)
        except Exception as e:
            print(f"[오류] {stadium_id} 수집 실패: {e}")
            results[stadium_id] = ([], [])

    # 전체 요약
    print("\n" + "=" * 60)
    print("전체 수집 결과 요약")
    print("=" * 60)
    print(f"{'구장':<20} {'전체 경기':>10} {'취소 경기':>10}")
    print("-" * 60)

    total_all = 0
    total_cancelled = 0
    for stadium_id, (all_games, cancelled_games) in results.items():
        name = STADIUMS[stadium_id]["name"]
        print(f"{name:<20} {len(all_games):>10} {len(cancelled_games):>10}")
        total_all += len(all_games)
        total_cancelled += len(cancelled_games)

    print("-" * 60)
    print(f"{'합계':<20} {total_all:>10} {total_cancelled:>10}")

    return results


def main():
    parser = argparse.ArgumentParser(
        description="KBO 우천취소 데이터 수집기",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예시:
  python cancel_crawler.py --stadium jamsil
  python cancel_crawler.py --stadium busan --years 2023 2024
  python cancel_crawler.py --all
  python cancel_crawler.py --list

지원 구장:
  jamsil   - 잠실야구장 (LG/두산)
  gocheok  - 고척스카이돔 (키움) [돔]
  suwon    - 수원KT위즈파크 (KT)
  incheon  - 인천SSG랜더스필드 (SSG)
  daejeon  - 대전한화생명이글스파크 (한화)
  daegu    - 대구삼성라이온즈파크 (삼성)
  gwangju  - 광주기아챔피언스필드 (KIA)
  busan    - 사직야구장 (롯데)
  changwon - 창원NC파크 (NC)
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
        help="모든 야외 구장 수집",
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
        help="기존 데이터에 추가 (덮어쓰기 대신 병합)",
    )

    args = parser.parse_args()

    # 구장 목록 출력
    if args.list:
        from stadium_config import print_stadium_info

        print_stadium_info()
        return

    # 모든 구장 수집
    if args.all:
        crawl_all_stadiums(years=args.years, months=args.months)
        return

    # 특정 구장 수집
    stadium_id = args.stadium or DEFAULT_STADIUM
    crawl_stadium(stadium_id, years=args.years, months=args.months, append=args.append)


if __name__ == "__main__":
    main()
