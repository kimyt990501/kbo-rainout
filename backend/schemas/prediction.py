"""
Pydantic 요청/응답 스키마 정의
"""
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any

from config import SUPPORTED_STADIUMS, DEFAULT_STADIUM


class PredictionRequest(BaseModel):
    """우천취소 예측 요청 스키마"""

    stadium: str = Field(
        default=DEFAULT_STADIUM,
        description=f"구장 ID (지원: {', '.join(SUPPORTED_STADIUMS)})"
    )
    daily_precip_sum: float = Field(
        ...,
        ge=0,
        description="일 총 강수량 (mm)"
    )
    daily_precip_hours: float = Field(
        ...,
        ge=0,
        description="강수 시간 (시간)"
    )
    pre_game_precip: float = Field(
        ...,
        ge=0,
        description="경기 전 3시간 강수량 (mm)"
    )
    pre_game_humidity: float = Field(
        ...,
        ge=0,
        le=100,
        description="경기 전 습도 (%)"
    )
    pre_game_temp: float = Field(
        ...,
        description="경기 전 기온 (°C)"
    )
    pre_game_wind: float = Field(
        ...,
        ge=0,
        description="경기 전 풍속 (m/s)"
    )
    prev_day_precip: float = Field(
        ...,
        ge=0,
        description="전날 강수량 (mm)"
    )
    daily_wind_max: float = Field(
        ...,
        ge=0,
        description="일 최대 풍속 (m/s)"
    )
    daily_temp_mean: float = Field(
        ...,
        description="일 평균 기온 (°C)"
    )
    month: int = Field(
        ...,
        ge=1,
        le=12,
        description="월 (1-12)"
    )
    dayofweek: int = Field(
        ...,
        ge=0,
        le=6,
        description="요일 (0=월요일, 6=일요일)"
    )

    @field_validator("stadium")
    @classmethod
    def validate_stadium(cls, v: str) -> str:
        """지원하는 구장인지 검증"""
        if v not in SUPPORTED_STADIUMS:
            raise ValueError(
                f"현재 {v} 구장은 지원하지 않습니다. 지원 구장: {', '.join(SUPPORTED_STADIUMS)}"
            )
        return v

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "stadium": "jamsil",
                    "daily_precip_sum": 50.0,
                    "daily_precip_hours": 10.0,
                    "pre_game_precip": 15.0,
                    "pre_game_humidity": 95.0,
                    "pre_game_temp": 25.0,
                    "pre_game_wind": 10.0,
                    "prev_day_precip": 30.0,
                    "daily_wind_max": 20.0,
                    "daily_temp_mean": 24.0,
                    "month": 7,
                    "dayofweek": 5
                }
            ]
        }
    }


class PredictionResponse(BaseModel):
    """우천취소 예측 응답 스키마"""

    stadium: str = Field(
        ...,
        description="예측에 사용된 구장 ID"
    )
    stadium_name: str = Field(
        ...,
        description="구장 한글명"
    )
    cancellation_probability: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="우천취소 확률 (0.0 ~ 1.0)"
    )
    prediction: str = Field(
        ...,
        description="예측 결과 (취소 가능성 높음/취소 가능성 있음/정상 진행 예상)"
    )
    confidence: str = Field(
        ...,
        description="신뢰도 (high/medium/low)"
    )
    risk_factors: List[str] = Field(
        default_factory=list,
        description="위험 요소 목록"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "stadium": "jamsil",
                    "stadium_name": "잠실야구장",
                    "cancellation_probability": 0.87,
                    "prediction": "취소 가능성 높음",
                    "confidence": "high",
                    "risk_factors": [
                        "경기 전 강수량이 많음 (15.0mm)",
                        "습도가 매우 높음 (95.0%)",
                        "장마철/여름철 경기 (7월)"
                    ]
                }
            ]
        }
    }


class HealthResponse(BaseModel):
    """헬스 체크 응답 스키마"""

    status: str = Field(..., description="서버 상태")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {"status": "ok"}
            ]
        }
    }


class StadiumInfo(BaseModel):
    """구장 정보 스키마"""

    id: str = Field(..., description="구장 ID")
    name: str = Field(..., description="구장 한글명")
    team: str = Field(..., description="홈팀명")
    available: bool = Field(..., description="모델 사용 가능 여부")


class StadiumListResponse(BaseModel):
    """구장 목록 응답 스키마"""

    stadiums: List[StadiumInfo] = Field(..., description="지원 구장 목록")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "stadiums": [
                        {
                            "id": "jamsil",
                            "name": "잠실야구장",
                            "team": "LG/두산",
                            "available": True
                        }
                    ]
                }
            ]
        }
    }


class ModelInfoResponse(BaseModel):
    """단일 모델 정보 응답 스키마"""

    stadium: str = Field(..., description="구장 ID")
    stadium_name: str = Field(..., description="구장 한글명")
    model_type: str = Field(..., description="모델 타입")
    feature_count: int = Field(..., description="피처 개수")
    features: List[str] = Field(..., description="피처 목록")
    description: str = Field(..., description="모델 설명")
    version: str = Field(..., description="모델 버전")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "stadium": "jamsil",
                    "stadium_name": "잠실야구장",
                    "model_type": "XGBoostClassifier",
                    "feature_count": 11,
                    "features": [
                        "daily_precip_sum",
                        "daily_precip_hours",
                        "pre_game_precip",
                        "pre_game_humidity",
                        "pre_game_temp",
                        "pre_game_wind",
                        "prev_day_precip",
                        "daily_wind_max",
                        "daily_temp_mean",
                        "month",
                        "dayofweek"
                    ],
                    "description": "KBO 잠실야구장 우천취소 예측 모델",
                    "version": "1.0.0"
                }
            ]
        }
    }


class AllModelsInfoResponse(BaseModel):
    """모든 모델 정보 응답 스키마"""

    models: Dict[str, ModelInfoResponse] = Field(..., description="구장별 모델 정보")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "models": {
                        "jamsil": {
                            "stadium": "jamsil",
                            "stadium_name": "잠실야구장",
                            "model_type": "XGBoostClassifier",
                            "feature_count": 11,
                            "features": ["daily_precip_sum", "..."],
                            "description": "KBO 잠실야구장 우천취소 예측 모델",
                            "version": "1.0.0"
                        }
                    }
                }
            ]
        }
    }


class WeatherRequest(BaseModel):
    """날씨 데이터 요청 스키마"""

    stadium: str = Field(
        default=DEFAULT_STADIUM,
        description=f"구장 ID (지원: {', '.join(SUPPORTED_STADIUMS)})"
    )
    game_date: str = Field(
        ...,
        description="경기 날짜 (YYYY-MM-DD 형식)"
    )
    game_hour: int = Field(
        default=18,
        ge=0,
        le=23,
        description="경기 시작 시간 (0-23, 기본값 18시)"
    )

    @field_validator("stadium")
    @classmethod
    def validate_stadium(cls, v: str) -> str:
        if v not in SUPPORTED_STADIUMS:
            raise ValueError(
                f"현재 {v} 구장은 지원하지 않습니다. 지원 구장: {', '.join(SUPPORTED_STADIUMS)}"
            )
        return v

    @field_validator("game_date")
    @classmethod
    def validate_game_date(cls, v: str) -> str:
        try:
            from datetime import datetime
            datetime.strptime(v, "%Y-%m-%d")
        except ValueError:
            raise ValueError("날짜 형식이 올바르지 않습니다. YYYY-MM-DD 형식으로 입력하세요.")
        return v

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "stadium": "jamsil",
                    "game_date": "2025-07-15",
                    "game_hour": 18
                }
            ]
        }
    }


class WeatherResponse(BaseModel):
    """날씨 데이터 응답 스키마"""

    stadium: str = Field(..., description="구장 ID")
    stadium_name: str = Field(..., description="구장 한글명")
    game_date: str = Field(..., description="경기 날짜")
    game_hour: int = Field(..., description="경기 시작 시간")
    daily_precip_sum: float = Field(..., description="일 총 강수량 (mm)")
    daily_precip_hours: float = Field(..., description="강수 시간")
    pre_game_precip: float = Field(..., description="경기 전 3시간 강수량 (mm)")
    pre_game_humidity: float = Field(..., description="경기 전 습도 (%)")
    pre_game_temp: float = Field(..., description="경기 전 기온 (°C)")
    pre_game_wind: float = Field(..., description="경기 전 풍속 (m/s)")
    prev_day_precip: float = Field(..., description="전날 강수량 (mm)")
    daily_wind_max: float = Field(..., description="일 최대 풍속 (m/s)")
    daily_temp_mean: float = Field(..., description="일 평균 기온 (°C)")
    month: int = Field(..., description="월 (1-12)")
    dayofweek: int = Field(..., description="요일 (0=월요일, 6=일요일)")
    data_source: str = Field(..., description="데이터 출처 (forecast/historical)")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "stadium": "jamsil",
                    "stadium_name": "잠실야구장",
                    "game_date": "2025-07-15",
                    "game_hour": 18,
                    "daily_precip_sum": 15.5,
                    "daily_precip_hours": 5.0,
                    "pre_game_precip": 3.2,
                    "pre_game_humidity": 85.0,
                    "pre_game_temp": 28.0,
                    "pre_game_wind": 4.5,
                    "prev_day_precip": 10.0,
                    "daily_wind_max": 12.0,
                    "daily_temp_mean": 26.5,
                    "month": 7,
                    "dayofweek": 1,
                    "data_source": "forecast"
                }
            ]
        }
    }


class WeatherTimelineRequest(BaseModel):
    """날씨 타임라인 요청 스키마"""

    stadium: str = Field(
        default=DEFAULT_STADIUM,
        description=f"구장 ID (지원: {', '.join(SUPPORTED_STADIUMS)})"
    )
    game_date: str = Field(
        ...,
        description="경기 날짜 (YYYY-MM-DD 형식)"
    )
    game_hour: int = Field(
        default=18,
        ge=0,
        le=23,
        description="경기 시작 시간 (0-23, 기본값 18시)"
    )
    hours_before: int = Field(
        default=3,
        ge=0,
        le=12,
        description="경기 전 몇 시간부터 조회할지 (기본값 3시간)"
    )
    hours_after: int = Field(
        default=3,
        ge=0,
        le=12,
        description="경기 후 몇 시간까지 조회할지 (기본값 3시간)"
    )

    @field_validator("stadium")
    @classmethod
    def validate_stadium(cls, v: str) -> str:
        if v not in SUPPORTED_STADIUMS:
            raise ValueError(
                f"현재 {v} 구장은 지원하지 않습니다. 지원 구장: {', '.join(SUPPORTED_STADIUMS)}"
            )
        return v

    @field_validator("game_date")
    @classmethod
    def validate_game_date(cls, v: str) -> str:
        try:
            from datetime import datetime
            datetime.strptime(v, "%Y-%m-%d")
        except ValueError:
            raise ValueError("날짜 형식이 올바르지 않습니다. YYYY-MM-DD 형식으로 입력하세요.")
        return v

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "stadium": "jamsil",
                    "game_date": "2025-07-15",
                    "game_hour": 18,
                    "hours_before": 3,
                    "hours_after": 3
                }
            ]
        }
    }


class TimelinePoint(BaseModel):
    """타임라인 단일 시간대 데이터"""

    hour: int = Field(..., description="시간 (0-23)")
    time_label: str = Field(..., description="시간 라벨 (예: '15:00', '18:30')")
    precipitation: float = Field(..., ge=0, description="강수량 (mm)")
    is_game_time: bool = Field(default=False, description="경기 시작 시간 여부")
    relative_time: str = Field(..., description="상대 시간 (예: '경기 3시간 전', '경기 시작', '경기 중')")


class WeatherTimelineResponse(BaseModel):
    """날씨 타임라인 응답 스키마"""

    stadium: str = Field(..., description="구장 ID")
    stadium_name: str = Field(..., description="구장 한글명")
    game_date: str = Field(..., description="경기 날짜")
    game_hour: int = Field(..., description="경기 시작 시간")
    timeline: List[TimelinePoint] = Field(..., description="시간대별 날씨 데이터")
    total_precipitation: float = Field(..., description="전체 기간 누적 강수량 (mm)")
    data_source: str = Field(..., description="데이터 출처 (forecast/historical)")

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "stadium": "jamsil",
                    "stadium_name": "잠실야구장",
                    "game_date": "2025-07-15",
                    "game_hour": 18,
                    "timeline": [
                        {
                            "hour": 15,
                            "time_label": "15:00",
                            "precipitation": 2.5,
                            "is_game_time": False,
                            "relative_time": "경기 3시간 전"
                        },
                        {
                            "hour": 18,
                            "time_label": "18:00",
                            "precipitation": 5.2,
                            "is_game_time": True,
                            "relative_time": "경기 시작"
                        },
                        {
                            "hour": 21,
                            "time_label": "21:00",
                            "precipitation": 1.8,
                            "is_game_time": False,
                            "relative_time": "경기 3시간 후"
                        }
                    ],
                    "total_precipitation": 25.3,
                    "data_source": "forecast"
                }
            ]
        }
    }
