"""
KBO 페이지 구조 확인용 디버그 스크립트
"""

import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup


def debug_kbo_page():
    chrome_options = Options()
    # chrome_options.add_argument("--headless")  # 디버그용으로 브라우저 보이게
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    try:
        url = "https://www.koreabaseball.com/Schedule/Schedule.aspx"
        print(f"접속 중: {url}")
        driver.get(url)
        time.sleep(3)
        
        # 2024년 5월로 이동 (우천취소 많았던 달)
        print("\n2024년 5월로 이동...")
        
        year_dropdown = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "ddlYear"))
        )
        Select(year_dropdown).select_by_value("2024")
        time.sleep(1)
        
        month_dropdown = driver.find_element(By.ID, "ddlMonth")
        Select(month_dropdown).select_by_value("05")
        time.sleep(2)
        
        # 페이지 소스 저장
        page_source = driver.page_source
        with open("kbo_page_debug.html", "w", encoding="utf-8") as f:
            f.write(page_source)
        print("페이지 소스 저장: kbo_page_debug.html")
        
        # BeautifulSoup으로 파싱
        soup = BeautifulSoup(page_source, 'html.parser')
        
        # 테이블 찾기
        print("\n=== 테이블 구조 확인 ===")
        tables = soup.find_all('table')
        print(f"테이블 개수: {len(tables)}")
        
        for i, table in enumerate(tables):
            classes = table.get('class', [])
            print(f"  테이블 {i}: class={classes}")
        
        # tbl 클래스 테이블 확인
        tbl = soup.find('table', class_='tbl')
        if tbl:
            print("\n=== tbl 클래스 테이블 발견 ===")
            tbody = tbl.find('tbody')
            if tbody:
                rows = tbody.find_all('tr')
                print(f"행 개수: {len(rows)}")
                
                # 처음 5개 행 출력
                print("\n처음 5개 행:")
                for i, row in enumerate(rows[:5]):
                    print(f"\n--- Row {i} ---")
                    cells = row.find_all('td')
                    for j, cell in enumerate(cells):
                        cell_class = cell.get('class', [])
                        cell_text = cell.get_text(strip=True)[:50]
                        print(f"  TD {j}: class={cell_class}, text='{cell_text}'")
            else:
                print("tbody 없음")
        else:
            print("\ntbl 클래스 테이블 없음")
            
            # 다른 테이블 구조 확인
            print("\n=== 모든 테이블 내용 확인 ===")
            for i, table in enumerate(tables[:3]):
                print(f"\n테이블 {i} 내용:")
                print(table.get_text()[:500])
        
        # 스케줄 관련 div 찾기
        print("\n=== 스케줄 관련 요소 확인 ===")
        schedule_divs = soup.find_all('div', class_=lambda x: x and 'schedule' in x.lower() if x else False)
        print(f"schedule 관련 div: {len(schedule_divs)}")
        
        # 취소 관련 텍스트 검색
        print("\n=== '취소' 텍스트 검색 ===")
        page_text = soup.get_text()
        if '취소' in page_text:
            print("'취소' 텍스트 발견!")
            # 취소가 포함된 부분 찾기
            for elem in soup.find_all(string=lambda t: t and '취소' in t):
                parent = elem.parent
                print(f"  태그: {parent.name}, 클래스: {parent.get('class')}")
                print(f"  내용: {elem.strip()[:100]}")
        else:
            print("'취소' 텍스트 없음")
        
        input("\n브라우저 확인 후 Enter 누르세요...")
        
    finally:
        driver.quit()


if __name__ == "__main__":
    debug_kbo_page()
