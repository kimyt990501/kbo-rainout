"""
모델 로딩 및 예측 로직 (다중 구장 지원)
"""
import pickle
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional

import pandas as pd
import numpy as np

from config import (
    STADIUM_MODELS,
    SUPPORTED_STADIUMS,
    THRESHOLD_HIGH,
    THRESHOLD_MEDIUM,
    RISK_THRESHOLDS,
    RAINY_SEASON_MONTHS,
    API_VERSION,
)
from schemas.prediction import PredictionRequest, PredictionResponse

logger = logging.getLogger(__name__)


class StadiumModel:
    """단일 구장 모델 클래스"""

    def __init__(self, stadium_id: str, model: Any, feature_cols: List[str], metadata: Dict[str, Any]):
        self.stadium_id = stadium_id
        self.model = model
        self.feature_cols = feature_cols
        self.metadata = metadata

    def get_model_info(self) -> Dict[str, Any]:
        """모델 메타데이터 반환"""
        model_type = type(self.model).__name__
        return {
            "stadium": self.stadium_id,
            "stadium_name": self.metadata.get("name", ""),
            "model_type": model_type,
            "feature_count": len(self.feature_cols),
            "features": self.feature_cols,
            "description": f"KBO {self.metadata.get('name', self.stadium_id)} 우천취소 예측 모델",
            "version": API_VERSION,
        }


class MultiStadiumPredictor:
    """다중 구장 우천취소 예측 클래스"""

    def __init__(self):
        """예측기 초기화"""
        self.models: Dict[str, StadiumModel] = {}
        self._loaded_stadiums: List[str] = []

    def load_all_models(self) -> None:
        """
        모든 구장 모델을 로드

        설정된 모든 구장의 모델을 로드하고, 실패한 경우 해당 구장만 스킵합니다.
        모든 모델 로딩 실패 시 예외를 발생시킵니다.
        """
        logger.info("=== 다중 구장 모델 로딩 시작 ===")
        logger.info(f"설정된 구장: {list(STADIUM_MODELS.keys())}")

        for stadium_id, stadium_config in STADIUM_MODELS.items():
            try:
                self._load_single_model(stadium_id, stadium_config)
                self._loaded_stadiums.append(stadium_id)
            except Exception as e:
                logger.warning(f"[{stadium_id}] 모델 로딩 실패: {e}")
                continue

        if not self._loaded_stadiums:
            raise RuntimeError("모든 구장 모델 로딩에 실패했습니다. 최소 하나의 모델이 필요합니다.")

        logger.info(f"=== 모델 로딩 완료 ===")
        logger.info(f"로딩된 구장: {self._loaded_stadiums}")
        logger.info(f"로딩 실패 구장: {[s for s in STADIUM_MODELS.keys() if s not in self._loaded_stadiums]}")

    def _load_single_model(self, stadium_id: str, config: Dict[str, Any]) -> None:
        """
        단일 구장 모델 로드

        Args:
            stadium_id: 구장 ID
            config: 구장 설정 딕셔너리
        """
        model_path = config["path"]
        logger.info(f"[{stadium_id}] 모델 로딩: {model_path}")

        if not model_path.exists():
            raise FileNotFoundError(f"모델 파일을 찾을 수 없습니다: {model_path}")

        with open(model_path, "rb") as f:
            model_data = pickle.load(f)

        model = model_data["model"]
        feature_cols = model_data["feature_cols"]

        self.models[stadium_id] = StadiumModel(
            stadium_id=stadium_id,
            model=model,
            feature_cols=feature_cols,
            metadata={
                "name": config.get("name", stadium_id),
                "team": config.get("team", ""),
                "coordinates": config.get("coordinates", (0, 0)),
            }
        )

        logger.info(f"[{stadium_id}] 로딩 완료 - 피처 수: {len(feature_cols)}")

    def get_loaded_stadiums(self) -> List[str]:
        """로딩된 구장 목록 반환"""
        return self._loaded_stadiums.copy()

    def is_stadium_available(self, stadium_id: str) -> bool:
        """구장 모델 사용 가능 여부 확인"""
        return stadium_id in self.models

    def get_stadium_model(self, stadium_id: str) -> Optional[StadiumModel]:
        """구장 모델 반환"""
        return self.models.get(stadium_id)

    def get_model_info(self, stadium_id: str) -> Dict[str, Any]:
        """특정 구장 모델 메타데이터 반환"""
        if stadium_id not in self.models:
            raise ValueError(f"{stadium_id} 구장 모델을 사용할 수 없습니다.")
        return self.models[stadium_id].get_model_info()

    def get_all_models_info(self) -> Dict[str, Dict[str, Any]]:
        """모든 구장 모델 메타데이터 반환"""
        return {
            stadium_id: model.get_model_info()
            for stadium_id, model in self.models.items()
        }

    def _prepare_features(self, request: PredictionRequest, feature_cols: List[str]) -> pd.DataFrame:
        """
        요청 데이터를 모델 입력 형식으로 변환

        Args:
            request: 예측 요청 데이터
            feature_cols: 피처 컬럼 목록

        Returns:
            피처 DataFrame
        """
        data = {
            "daily_precip_sum": [request.daily_precip_sum],
            "daily_precip_hours": [request.daily_precip_hours],
            "pre_game_precip": [request.pre_game_precip],
            "pre_game_humidity": [request.pre_game_humidity],
            "pre_game_temp": [request.pre_game_temp],
            "pre_game_wind": [request.pre_game_wind],
            "prev_day_precip": [request.prev_day_precip],
            "daily_wind_max": [request.daily_wind_max],
            "daily_temp_mean": [request.daily_temp_mean],
            "month": [request.month],
            "dayofweek": [request.dayofweek],
        }

        df = pd.DataFrame(data)
        return df[feature_cols]

    def _analyze_risk_factors(self, request: PredictionRequest) -> List[str]:
        """
        입력 데이터에서 위험 요소 분석

        Args:
            request: 예측 요청 데이터

        Returns:
            위험 요소 설명 목록
        """
        risk_factors = []

        # 경기 전 강수량
        if request.pre_game_precip >= RISK_THRESHOLDS["pre_game_precip"]:
            risk_factors.append(
                f"경기 전 강수량이 많음 ({request.pre_game_precip}mm)"
            )

        # 일 총 강수량
        if request.daily_precip_sum >= RISK_THRESHOLDS["daily_precip_sum"]:
            risk_factors.append(
                f"일 강수량이 많음 ({request.daily_precip_sum}mm)"
            )

        # 습도
        if request.pre_game_humidity >= RISK_THRESHOLDS["pre_game_humidity"]:
            risk_factors.append(
                f"습도가 매우 높음 ({request.pre_game_humidity}%)"
            )

        # 전날 강수량
        if request.prev_day_precip >= RISK_THRESHOLDS["prev_day_precip"]:
            risk_factors.append(
                f"전날 강수량이 많음 ({request.prev_day_precip}mm)"
            )

        # 풍속
        if request.daily_wind_max >= RISK_THRESHOLDS["daily_wind_max"]:
            risk_factors.append(
                f"강풍 주의 ({request.daily_wind_max}m/s)"
            )

        # 장마철
        if request.month in RAINY_SEASON_MONTHS:
            risk_factors.append(
                f"장마철/여름철 경기 ({request.month}월)"
            )

        return risk_factors

    def _determine_prediction_result(self, probability: float) -> Tuple[str, str]:
        """
        확률에 따른 예측 결과 및 신뢰도 결정

        Args:
            probability: 취소 확률

        Returns:
            (prediction, confidence) 튜플
        """
        if probability >= THRESHOLD_HIGH:
            return "취소 가능성 높음", "high"
        elif probability >= THRESHOLD_MEDIUM:
            return "취소 가능성 있음", "medium"
        else:
            return "정상 진행 예상", "low"

    def predict(self, request: PredictionRequest) -> PredictionResponse:
        """
        우천취소 예측 수행

        Args:
            request: 예측 요청 데이터 (stadium 필드 포함)

        Returns:
            예측 결과
        """
        stadium_id = request.stadium

        if stadium_id not in self.models:
            raise ValueError(f"{stadium_id} 구장 모델을 사용할 수 없습니다.")

        stadium_model = self.models[stadium_id]

        # 피처 준비
        features_df = self._prepare_features(request, stadium_model.feature_cols)

        # 예측 수행
        probabilities = stadium_model.model.predict_proba(features_df)
        cancel_probability = float(probabilities[0][1])

        # 소수점 3자리로 반올림
        cancel_probability = round(cancel_probability, 3)

        # 예측 결과 및 신뢰도 결정
        prediction, confidence = self._determine_prediction_result(cancel_probability)

        # 위험 요소 분석
        risk_factors = self._analyze_risk_factors(request)

        return PredictionResponse(
            stadium=stadium_id,
            stadium_name=stadium_model.metadata.get("name", stadium_id),
            cancellation_probability=cancel_probability,
            prediction=prediction,
            confidence=confidence,
            risk_factors=risk_factors,
        )


# 하위 호환성을 위한 별칭 (단일 구장용 - deprecated)
RainCancelPredictor = MultiStadiumPredictor
