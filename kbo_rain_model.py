"""
KBO 우천취소 예측 모델 (다중 구장 지원)
========================================
1. 탐색적 데이터 분석 (EDA)
2. 데이터 전처리
3. 모델 학습 (XGBoost, LightGBM, RandomForest)
4. 모델 평가 및 해석

설치: pip install pandas numpy scikit-learn xgboost lightgbm matplotlib seaborn
실행: python kbo_rain_model.py --stadium jamsil
      python kbo_rain_model.py --stadium busan
      python kbo_rain_model.py --all
"""

import argparse
import pickle
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    roc_auc_score,
    precision_recall_curve,
    f1_score,
    accuracy_score,
)
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier
import warnings

warnings.filterwarnings("ignore")

from stadium_config import (
    STADIUMS,
    get_stadium_config,
    get_data_paths,
    get_outdoor_stadiums,
    DEFAULT_STADIUM,
    MODELS_DIR,
)


# 한글 폰트 설정 (macOS)
plt.rcParams["font.family"] = "AppleGothic"
plt.rcParams["axes.unicode_minus"] = False


# ============================================
# 1. 데이터 로드 및 확인
# ============================================
def load_and_explore_data(filepath, stadium_name):
    """데이터 로드 및 기본 탐색"""
    print("=" * 60)
    print(f"1. 데이터 로드 및 탐색 ({stadium_name})")
    print("=" * 60)

    df = pd.read_csv(filepath)

    print(f"\n데이터 shape: {df.shape}")
    print(f"\n컬럼 목록:\n{df.columns.tolist()}")
    print(f"\n데이터 타입:\n{df.dtypes}")
    print(f"\n결측치:\n{df.isnull().sum()}")

    # 타겟 분포
    print(f"\n취소 여부 분포:")
    print(df["cancelled"].value_counts())
    print(f"\n취소 비율: {df['cancelled'].mean()*100:.2f}%")

    return df


# ============================================
# 2. 탐색적 데이터 분석 (EDA)
# ============================================
def perform_eda(df, stadium_id, stadium_name):
    """탐색적 데이터 분석"""
    print("\n" + "=" * 60)
    print(f"2. 탐색적 데이터 분석 - {stadium_name}")
    print("=" * 60)

    # 우천취소만 필터링 (미세먼지 제외)
    df_rain = df[df["reason"].isin(["우천취소", "정상진행"])].copy()
    df_rain["is_cancelled"] = (df_rain["reason"] == "우천취소").astype(int)

    cancelled = df_rain[df_rain["is_cancelled"] == 1]
    normal = df_rain[df_rain["is_cancelled"] == 0]

    print(f"\n분석 대상: {len(df_rain)}개 경기")
    print(f"  - 우천취소: {len(cancelled)}개")
    print(f"  - 정상진행: {len(normal)}개")

    # 취소 경기가 너무 적으면 EDA 스킵
    if len(cancelled) < 3:
        print(f"\n[경고] 우천취소 경기가 {len(cancelled)}개로 너무 적어 EDA를 스킵합니다.")
        return df_rain

    # 날씨 변수 비교
    weather_cols = [
        "daily_precip_sum",
        "daily_precip_hours",
        "daily_rain_sum",
        "pre_game_precip",
        "pre_game_humidity",
        "pre_game_temp",
        "prev_day_precip",
        "daily_wind_max",
    ]

    print("\n[날씨 변수 비교: 취소 vs 정상]")
    print("-" * 60)
    print(f"{'변수':<25} {'취소 평균':>12} {'정상 평균':>12} {'차이':>10}")
    print("-" * 60)

    for col in weather_cols:
        if col in df_rain.columns:
            c_mean = cancelled[col].mean()
            n_mean = normal[col].mean()
            diff = c_mean - n_mean
            print(f"{col:<25} {c_mean:>12.2f} {n_mean:>12.2f} {diff:>10.2f}")

    # 시각화
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    fig.suptitle(f"{stadium_name} - 우천취소 vs 정상경기 날씨 비교", fontsize=14)

    plot_cols = [
        "daily_precip_sum",
        "pre_game_precip",
        "pre_game_humidity",
        "prev_day_precip",
        "daily_precip_hours",
        "pre_game_temp",
    ]

    for ax, col in zip(axes.flatten(), plot_cols):
        if col in df_rain.columns:
            data_cancelled = cancelled[col].dropna()
            data_normal = normal[col].dropna()

            if len(data_cancelled) > 0 and len(data_normal) > 0:
                ax.boxplot([data_normal, data_cancelled], labels=["정상", "취소"])
            ax.set_title(col)
            ax.set_ylabel("값")

    plt.tight_layout()
    eda_path = MODELS_DIR / f"eda_{stadium_id}_weather_comparison.png"
    eda_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(eda_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"\n[저장] {eda_path}")

    # 월별 취소 분포
    df_rain["month"] = pd.to_datetime(df_rain["date"]).dt.month
    monthly_cancel = df_rain.groupby("month")["is_cancelled"].agg(["sum", "count"])
    monthly_cancel["rate"] = monthly_cancel["sum"] / monthly_cancel["count"] * 100

    print("\n[월별 우천취소 현황]")
    print(monthly_cancel)

    return df_rain


# ============================================
# 3. 데이터 전처리
# ============================================
def preprocess_data(df, stadium_name):
    """모델 학습을 위한 데이터 전처리"""
    print("\n" + "=" * 60)
    print(f"3. 데이터 전처리 - {stadium_name}")
    print("=" * 60)

    # 우천취소만 대상 (미세먼지 제외)
    df_model = df[df["reason"].isin(["우천취소", "정상진행"])].copy()
    df_model["is_cancelled"] = (df_model["reason"] == "우천취소").astype(int)

    # 피처 선택
    feature_cols = [
        "daily_precip_sum",  # 일 강수량
        "daily_precip_hours",  # 강수 시간
        "pre_game_precip",  # 경기 전 강수량
        "pre_game_humidity",  # 경기 전 습도
        "pre_game_temp",  # 경기 전 기온
        "pre_game_wind",  # 경기 전 풍속
        "prev_day_precip",  # 전날 강수량
        "daily_wind_max",  # 최대 풍속
        "daily_temp_mean",  # 평균 기온
    ]

    # 월, 요일 추가
    df_model["month"] = pd.to_datetime(df_model["date"]).dt.month
    df_model["dayofweek"] = pd.to_datetime(df_model["date"]).dt.dayofweek

    feature_cols.extend(["month", "dayofweek"])

    # 결측치 처리
    X = df_model[feature_cols].copy()
    y = df_model["is_cancelled"]

    # 결측치를 0으로 채움 (강수량 관련)
    X = X.fillna(0)

    print(f"\n피처 수: {len(feature_cols)}")
    print(f"피처 목록: {feature_cols}")
    print(f"\n데이터 shape: X={X.shape}, y={y.shape}")
    print(f"클래스 분포: 정상={sum(y==0)}, 취소={sum(y==1)}")

    return X, y, feature_cols


# ============================================
# 4. 모델 학습 및 평가
# ============================================
def train_and_evaluate(X, y, feature_cols, stadium_name):
    """여러 모델 학습 및 비교"""
    print("\n" + "=" * 60)
    print(f"4. 모델 학습 및 평가 - {stadium_name}")
    print("=" * 60)

    # 취소 경기가 너무 적으면 학습 불가
    if sum(y) < 5:
        print(f"\n[오류] 우천취소 경기가 {sum(y)}개로 너무 적어 모델 학습이 불가능합니다.")
        print("최소 5개 이상의 취소 경기가 필요합니다.")
        return None, None, None, None, None

    # 데이터 분할
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    print(f"\n학습 데이터: {len(X_train)}개 (취소: {sum(y_train)}개)")
    print(f"테스트 데이터: {len(X_test)}개 (취소: {sum(y_test)}개)")

    # 클래스 불균형 처리를 위한 가중치 계산
    n_neg = len(y_train[y_train == 0])
    n_pos = len(y_train[y_train == 1])

    if n_pos == 0:
        print("\n[오류] 학습 데이터에 취소 경기가 없습니다.")
        return None, None, None, None, None

    scale_pos_weight = n_neg / n_pos
    print(f"\n클래스 가중치 (scale_pos_weight): {scale_pos_weight:.2f}")

    # 모델 정의
    models = {
        "XGBoost": XGBClassifier(
            n_estimators=100,
            max_depth=4,
            learning_rate=0.1,
            scale_pos_weight=scale_pos_weight,
            random_state=42,
            eval_metric="logloss",
        ),
        "LightGBM": LGBMClassifier(
            n_estimators=100,
            max_depth=4,
            learning_rate=0.1,
            class_weight="balanced",
            random_state=42,
            verbose=-1,
        ),
        "RandomForest": RandomForestClassifier(
            n_estimators=100, max_depth=6, class_weight="balanced", random_state=42
        ),
    }

    results = {}
    best_model = None
    best_f1 = 0
    best_model_name = None

    for name, model in models.items():
        print(f"\n{'='*40}")
        print(f"[{name}]")
        print("=" * 40)

        # 학습
        model.fit(X_train, y_train)

        # 예측
        y_pred = model.predict(X_test)
        y_prob = model.predict_proba(X_test)[:, 1]

        # 평가
        accuracy = accuracy_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred)

        # 테스트 데이터에 양성 클래스가 있을 때만 AUC 계산
        if sum(y_test) > 0:
            roc_auc = roc_auc_score(y_test, y_prob)
        else:
            roc_auc = 0.0

        print(f"\nAccuracy: {accuracy:.4f}")
        print(f"F1 Score: {f1:.4f}")
        print(f"ROC-AUC: {roc_auc:.4f}")

        print(f"\nClassification Report:")
        print(classification_report(y_test, y_pred, target_names=["정상", "취소"]))

        print(f"Confusion Matrix:")
        cm = confusion_matrix(y_test, y_pred)
        print(cm)

        # 교차 검증
        cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
        cv_scores = cross_val_score(model, X, y, cv=cv, scoring="f1")
        print(f"\n5-Fold CV F1: {cv_scores.mean():.4f} (+/- {cv_scores.std()*2:.4f})")

        results[name] = {
            "model": model,
            "accuracy": accuracy,
            "f1": f1,
            "roc_auc": roc_auc,
            "cv_f1_mean": cv_scores.mean(),
        }

        if f1 > best_f1:
            best_f1 = f1
            best_model = model
            best_model_name = name

    print(f"\n{'='*60}")
    print(f"최고 성능 모델: {best_model_name} (F1: {best_f1:.4f})")
    print("=" * 60)

    return results, best_model, best_model_name, X_test, y_test


# ============================================
# 5. 피처 중요도 분석
# ============================================
def analyze_feature_importance(model, feature_cols, model_name, stadium_id, stadium_name):
    """피처 중요도 분석 및 시각화"""
    print("\n" + "=" * 60)
    print(f"5. 피처 중요도 분석 - {stadium_name}")
    print("=" * 60)

    # 피처 중요도 추출
    if hasattr(model, "feature_importances_"):
        importance = model.feature_importances_
    else:
        importance = model.coef_[0]

    # 데이터프레임 생성
    feat_imp = pd.DataFrame(
        {"feature": feature_cols, "importance": importance}
    ).sort_values("importance", ascending=False)

    print(f"\n[{model_name} 피처 중요도]")
    print(feat_imp.to_string(index=False))

    # 시각화
    plt.figure(figsize=(10, 6))
    sns.barplot(data=feat_imp, x="importance", y="feature", palette="viridis")
    plt.title(f"{stadium_name} - {model_name} 피처 중요도")
    plt.xlabel("중요도")
    plt.ylabel("피처")
    plt.tight_layout()

    fig_path = MODELS_DIR / f"feature_importance_{stadium_id}.png"
    fig_path.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(fig_path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"\n[저장] {fig_path}")

    return feat_imp


# ============================================
# 6. 예측 함수
# ============================================
def create_prediction_function(model, feature_cols):
    """실제 사용을 위한 예측 함수 생성"""

    def predict_cancellation(
        daily_precip_sum=0,
        daily_precip_hours=0,
        pre_game_precip=0,
        pre_game_humidity=50,
        pre_game_temp=20,
        pre_game_wind=10,
        prev_day_precip=0,
        daily_wind_max=15,
        daily_temp_mean=20,
        month=7,
        dayofweek=5,
    ):
        """
        우천취소 확률 예측

        Parameters:
        -----------
        daily_precip_sum: 일 총 강수량 (mm)
        daily_precip_hours: 강수 시간
        pre_game_precip: 경기 전 3시간 강수량 (mm)
        pre_game_humidity: 경기 전 습도 (%)
        pre_game_temp: 경기 전 기온 (C)
        pre_game_wind: 경기 전 풍속 (m/s)
        prev_day_precip: 전날 강수량 (mm)
        daily_wind_max: 최대 풍속 (m/s)
        daily_temp_mean: 평균 기온 (C)
        month: 월 (1-12)
        dayofweek: 요일 (0=월, 6=일)

        Returns:
        --------
        dict: 예측 결과 (확률, 판정)
        """
        input_data = pd.DataFrame(
            [
                [
                    daily_precip_sum,
                    daily_precip_hours,
                    pre_game_precip,
                    pre_game_humidity,
                    pre_game_temp,
                    pre_game_wind,
                    prev_day_precip,
                    daily_wind_max,
                    daily_temp_mean,
                    month,
                    dayofweek,
                ]
            ],
            columns=feature_cols,
        )

        prob = model.predict_proba(input_data)[0][1]
        prediction = "취소 가능성 높음" if prob >= 0.5 else "정상 진행 예상"

        return {
            "cancellation_probability": f"{prob*100:.1f}%",
            "prediction": prediction,
            "risk_level": "높음" if prob >= 0.7 else ("중간" if prob >= 0.4 else "낮음"),
        }

    return predict_cancellation


# ============================================
# 7. 모델 저장
# ============================================
def save_model(model, feature_cols, stadium_id, stadium_name):
    """학습된 모델 저장"""
    paths = get_data_paths(stadium_id)
    model_path = paths["model"]
    model_path.parent.mkdir(parents=True, exist_ok=True)

    model_data = {
        "model": model,
        "feature_cols": feature_cols,
        "stadium_id": stadium_id,
        "stadium_name": stadium_name,
    }

    with open(model_path, "wb") as f:
        pickle.dump(model_data, f)

    print(f"\n[저장] {model_path}")

    return model_path


# ============================================
# 구장별 모델 학습
# ============================================
def train_stadium_model(stadium_id):
    """특정 구장의 모델 학습"""
    stadium_config = get_stadium_config(stadium_id)
    stadium_name = stadium_config["name"]
    paths = get_data_paths(stadium_id)

    print("\n" + "=" * 60)
    print(f"KBO {stadium_name} 우천취소 예측 모델")
    print("=" * 60)

    # 데이터 파일 확인
    data_file = paths["with_weather"]
    if not data_file.exists():
        print(f"\n[오류] {data_file} 파일이 없습니다!")
        print(f"먼저 다음 명령을 실행하세요:")
        print(f"  1. python cancel_crawler.py --stadium {stadium_id}")
        print(f"  2. python weather_collector_openmeteo.py --stadium {stadium_id}")
        return None

    # 1. 데이터 로드
    df = load_and_explore_data(data_file, stadium_name)

    # 2. EDA
    df_rain = perform_eda(df, stadium_id, stadium_name)

    # 3. 전처리
    X, y, feature_cols = preprocess_data(df, stadium_name)

    # 취소 경기 수 확인
    if sum(y) < 5:
        print(f"\n[스킵] {stadium_name}: 우천취소 경기가 {sum(y)}개로 너무 적습니다.")
        return None

    # 4. 모델 학습
    results, best_model, best_model_name, X_test, y_test = train_and_evaluate(
        X, y, feature_cols, stadium_name
    )

    if best_model is None:
        return None

    # 5. 피처 중요도
    feat_imp = analyze_feature_importance(
        best_model, feature_cols, best_model_name, stadium_id, stadium_name
    )

    # 6. 예측 함수 생성
    predict_fn = create_prediction_function(best_model, feature_cols)

    # 7. 모델 저장
    model_path = save_model(best_model, feature_cols, stadium_id, stadium_name)

    # 예측 테스트
    print("\n" + "=" * 60)
    print(f"{stadium_name} 예측 테스트")
    print("=" * 60)

    # 시나리오 1: 장마철 폭우
    print("\n[시나리오 1] 장마철 폭우 (7월, 강수량 50mm, 습도 95%)")
    result1 = predict_fn(
        daily_precip_sum=50, pre_game_precip=15, pre_game_humidity=95, prev_day_precip=30, month=7
    )
    print(result1)

    # 시나리오 2: 맑은 날
    print("\n[시나리오 2] 맑은 날 (5월, 강수량 0mm, 습도 50%)")
    result2 = predict_fn(
        daily_precip_sum=0, pre_game_precip=0, pre_game_humidity=50, prev_day_precip=0, month=5
    )
    print(result2)

    print(f"\n{stadium_name} 모델 학습 완료!")

    return {
        "model": best_model,
        "feature_cols": feature_cols,
        "predict_fn": predict_fn,
        "model_path": model_path,
        "results": results,
    }


def train_all_stadiums(outdoor_only=True):
    """모든 구장 모델 학습"""
    if outdoor_only:
        stadium_ids = get_outdoor_stadiums()
        print(f"야외 구장 {len(stadium_ids)}개 모델 학습 시작...")
    else:
        stadium_ids = list(STADIUMS.keys())
        print(f"전체 구장 {len(stadium_ids)}개 모델 학습 시작...")

    results = {}
    for i, stadium_id in enumerate(stadium_ids, 1):
        print(f"\n{'#'*60}")
        print(f"# [{i}/{len(stadium_ids)}] {STADIUMS[stadium_id]['name']}")
        print("#" * 60)

        try:
            result = train_stadium_model(stadium_id)
            results[stadium_id] = result
        except Exception as e:
            print(f"[오류] {stadium_id} 모델 학습 실패: {e}")
            import traceback

            traceback.print_exc()
            results[stadium_id] = None

    # 전체 요약
    print("\n" + "=" * 60)
    print("전체 모델 학습 결과")
    print("=" * 60)
    print(f"{'구장':<25} {'상태':<10} {'Best Model':<15} {'F1 Score'}")
    print("-" * 60)

    for stadium_id, result in results.items():
        name = STADIUMS[stadium_id]["name"]
        if result is not None:
            best_name = None
            best_f1 = 0
            for model_name, model_result in result["results"].items():
                if model_result["f1"] > best_f1:
                    best_f1 = model_result["f1"]
                    best_name = model_name
            print(f"{name:<25} {'✓ 성공':<10} {best_name:<15} {best_f1:.4f}")
        else:
            print(f"{name:<25} {'✗ 실패':<10} {'-':<15} {'-'}")

    return results


def main():
    parser = argparse.ArgumentParser(
        description="KBO 우천취소 예측 모델 학습",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
예시:
  python kbo_rain_model.py --stadium jamsil
  python kbo_rain_model.py --stadium busan
  python kbo_rain_model.py --all
  python kbo_rain_model.py --list

참고:
  - 먼저 cancel_crawler.py와 weather_collector_openmeteo.py를 실행해야 합니다.
  - 취소 경기가 5개 미만인 구장은 모델 학습이 불가능합니다.
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
        help="모든 야외 구장 모델 학습",
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

    # 모든 구장 학습
    if args.all:
        train_all_stadiums()
        return

    # 특정 구장 학습
    stadium_id = args.stadium or DEFAULT_STADIUM
    train_stadium_model(stadium_id)


if __name__ == "__main__":
    main()
