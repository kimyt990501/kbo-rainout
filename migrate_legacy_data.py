#!/usr/bin/env python3
"""
기존 잠실 데이터를 새 디렉토리 구조로 마이그레이션
=================================================
기존:
  - kbo_jamsil_all_games.csv
  - kbo_jamsil_cancelled_games.csv
  - kbo_jamsil_with_weather.csv
  - kbo_rain_model.pkl

새 구조:
  - data/kbo_jamsil_all_games.csv
  - data/kbo_jamsil_cancelled_games.csv
  - data/kbo_jamsil_with_weather.csv
  - models/kbo_jamsil_model.pkl
"""

import shutil
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
DATA_DIR = PROJECT_ROOT / "data"
MODELS_DIR = PROJECT_ROOT / "models"


def migrate():
    """기존 데이터 마이그레이션"""
    print("=" * 60)
    print("기존 잠실 데이터 마이그레이션")
    print("=" * 60)

    # 디렉토리 생성
    DATA_DIR.mkdir(exist_ok=True)
    MODELS_DIR.mkdir(exist_ok=True)

    # 데이터 파일 이동
    data_files = [
        "kbo_jamsil_all_games.csv",
        "kbo_jamsil_cancelled_games.csv",
        "kbo_jamsil_with_weather.csv",
    ]

    for filename in data_files:
        src = PROJECT_ROOT / filename
        dst = DATA_DIR / filename

        if src.exists():
            if dst.exists():
                print(f"[스킵] {dst} 이미 존재")
            else:
                shutil.copy2(src, dst)
                print(f"[복사] {src} -> {dst}")
        else:
            print(f"[없음] {src}")

    # 모델 파일 이동
    old_model = PROJECT_ROOT / "kbo_rain_model.pkl"
    new_model = MODELS_DIR / "kbo_jamsil_model.pkl"

    if old_model.exists():
        if new_model.exists():
            print(f"[스킵] {new_model} 이미 존재")
        else:
            shutil.copy2(old_model, new_model)
            print(f"[복사] {old_model} -> {new_model}")
    else:
        print(f"[없음] {old_model}")

    # EDA/피처 중요도 이미지도 복사
    image_files = [
        ("eda_weather_comparison.png", "eda_jamsil_weather_comparison.png"),
        ("feature_importance.png", "feature_importance_jamsil.png"),
    ]

    for src_name, dst_name in image_files:
        src = PROJECT_ROOT / src_name
        dst = MODELS_DIR / dst_name

        if src.exists():
            if dst.exists():
                print(f"[스킵] {dst} 이미 존재")
            else:
                shutil.copy2(src, dst)
                print(f"[복사] {src} -> {dst}")
        else:
            print(f"[없음] {src}")

    print("\n" + "=" * 60)
    print("마이그레이션 완료!")
    print("=" * 60)
    print("\n기존 파일들은 삭제되지 않았습니다.")
    print("확인 후 수동으로 삭제하세요:")
    print("  rm kbo_jamsil_*.csv kbo_rain_model.pkl")


if __name__ == "__main__":
    migrate()
