"""
API 라우터 및 엔드포인트 정의 (다중 구장 지원)
"""
import logging
from datetime import datetime
from typing import TYPE_CHECKING, Optional, Union

from fastapi import APIRouter, HTTPException, Request, Query

from config import STADIUM_MODELS, SUPPORTED_STADIUMS
from schemas.prediction import (
    PredictionRequest,
    PredictionResponse,
    HealthResponse,
    ModelInfoResponse,
    AllModelsInfoResponse,
    StadiumInfo,
    StadiumListResponse,
    WeatherRequest,
    WeatherResponse,
    WeatherTimelineRequest,
    WeatherTimelineResponse,
)
from services.weather import weather_service

if TYPE_CHECKING:
    from models.predictor import MultiStadiumPredictor

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["prediction"])


def get_predictor(request: Request) -> "MultiStadiumPredictor":
    """앱 상태에서 예측기 인스턴스 가져오기"""
    return request.app.state.predictor


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """
    헬스 체크 엔드포인트

    서버 상태를 확인합니다.
    """
    return HealthResponse(status="ok")


@router.get("/stadiums", response_model=StadiumListResponse)
async def list_stadiums(request: Request) -> StadiumListResponse:
    """
    지원 구장 목록 엔드포인트

    지원 가능한 구장 목록과 각 구장의 모델 사용 가능 여부를 반환합니다.
    """
    predictor = get_predictor(request)
    loaded_stadiums = predictor.get_loaded_stadiums()

    stadiums = []
    for stadium_id, config in STADIUM_MODELS.items():
        stadiums.append(
            StadiumInfo(
                id=stadium_id,
                name=config.get("name", stadium_id),
                team=config.get("team", ""),
                available=stadium_id in loaded_stadiums,
            )
        )

    return StadiumListResponse(stadiums=stadiums)


@router.get(
    "/model-info",
    response_model=Union[ModelInfoResponse, AllModelsInfoResponse],
    responses={
        200: {
            "description": "모델 정보 반환",
            "content": {
                "application/json": {
                    "examples": {
                        "single_stadium": {
                            "summary": "단일 구장 정보",
                            "value": {
                                "stadium": "jamsil",
                                "stadium_name": "잠실야구장",
                                "model_type": "XGBClassifier",
                                "feature_count": 11,
                                "features": ["daily_precip_sum", "..."],
                                "description": "KBO 잠실야구장 우천취소 예측 모델",
                                "version": "1.1.0"
                            }
                        },
                        "all_stadiums": {
                            "summary": "모든 구장 정보",
                            "value": {
                                "models": {
                                    "jamsil": {
                                        "stadium": "jamsil",
                                        "stadium_name": "잠실야구장",
                                        "model_type": "XGBClassifier",
                                        "feature_count": 11,
                                        "features": ["..."],
                                        "description": "...",
                                        "version": "1.1.0"
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }
)
async def get_model_info(
    request: Request,
    stadium: Optional[str] = Query(
        default=None,
        description=f"구장 ID (미지정 시 모든 구장 정보 반환). 지원: {', '.join(SUPPORTED_STADIUMS)}"
    )
) -> Union[ModelInfoResponse, AllModelsInfoResponse]:
    """
    모델 정보 엔드포인트

    특정 구장 또는 모든 구장의 모델 메타데이터를 반환합니다.

    - **stadium** (선택): 구장 ID. 미지정 시 모든 구장 정보 반환
    """
    predictor = get_predictor(request)

    try:
        if stadium:
            # 특정 구장 정보 반환
            if not predictor.is_stadium_available(stadium):
                raise HTTPException(
                    status_code=404,
                    detail=f"{stadium} 구장 모델을 사용할 수 없습니다."
                )
            model_info = predictor.get_model_info(stadium)
            return ModelInfoResponse(**model_info)
        else:
            # 모든 구장 정보 반환
            all_info = predictor.get_all_models_info()
            models_response = {
                stadium_id: ModelInfoResponse(**info)
                for stadium_id, info in all_info.items()
            }
            return AllModelsInfoResponse(models=models_response)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"모델 정보 조회 중 오류 발생: {e}")
        raise HTTPException(
            status_code=500,
            detail="모델 정보 조회 중 오류가 발생했습니다."
        )


@router.post("/predict", response_model=PredictionResponse)
async def predict_cancellation(
    request: Request,
    prediction_request: PredictionRequest
) -> PredictionResponse:
    """
    우천취소 예측 엔드포인트

    경기 전 날씨 데이터를 입력받아 우천취소 확률을 예측합니다.

    - **stadium**: 구장 ID (기본값: jamsil)
    - **daily_precip_sum**: 일 총 강수량 (mm)
    - **daily_precip_hours**: 강수 시간 (시간)
    - **pre_game_precip**: 경기 전 3시간 강수량 (mm)
    - **pre_game_humidity**: 경기 전 습도 (%)
    - **pre_game_temp**: 경기 전 기온 (°C)
    - **pre_game_wind**: 경기 전 풍속 (m/s)
    - **prev_day_precip**: 전날 강수량 (mm)
    - **daily_wind_max**: 일 최대 풍속 (m/s)
    - **daily_temp_mean**: 일 평균 기온 (°C)
    - **month**: 월 (1-12)
    - **dayofweek**: 요일 (0=월요일, 6=일요일)
    """
    predictor = get_predictor(request)
    stadium_id = prediction_request.stadium

    # 구장 모델 사용 가능 여부 확인
    if not predictor.is_stadium_available(stadium_id):
        raise HTTPException(
            status_code=404,
            detail=f"{stadium_id} 구장 모델을 사용할 수 없습니다."
        )

    # 요청 로깅
    request_time = datetime.now().isoformat()
    logger.info(f"[{request_time}] 예측 요청 수신")
    logger.info(f"[PREDICT] stadium={stadium_id}, 입력 데이터: {prediction_request.model_dump()}")

    try:
        # 예측 수행
        result = predictor.predict(prediction_request)

        # 결과 로깅
        logger.info(
            f"[PREDICT] stadium={stadium_id}, "
            f"probability={result.cancellation_probability}, "
            f"prediction={result.prediction}, confidence={result.confidence}"
        )

        return result

    except ValueError as e:
        logger.error(f"예측 요청 오류: {e}")
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"예측 중 오류 발생: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="예측 중 오류가 발생했습니다."
        )


@router.post("/weather", response_model=WeatherResponse)
async def get_weather(weather_request: WeatherRequest) -> WeatherResponse:
    """
    날씨 데이터 조회 엔드포인트

    Open-Meteo API를 사용하여 경기 날씨 데이터를 조회합니다.

    - **stadium**: 구장 ID (기본값: jamsil)
    - **game_date**: 경기 날짜 (YYYY-MM-DD 형식)
    - **game_hour**: 경기 시작 시간 (0-23, 기본값 18시)

    예보 데이터는 현재일 기준 최대 16일 이후까지 조회 가능합니다.
    과거 데이터는 아카이브에서 조회됩니다.
    """
    stadium_id = weather_request.stadium
    game_date = weather_request.game_date
    game_hour = weather_request.game_hour

    # 구장 정보 확인
    stadium_config = STADIUM_MODELS.get(stadium_id)
    if not stadium_config:
        raise HTTPException(
            status_code=404,
            detail=f"{stadium_id} 구장은 지원하지 않습니다."
        )

    logger.info(f"[WEATHER] 날씨 조회 요청: stadium={stadium_id}, date={game_date}, hour={game_hour}")

    try:
        # 날씨 데이터 조회
        weather_data = await weather_service.get_weather_for_game(
            stadium=stadium_id,
            game_date=game_date,
            game_hour=game_hour
        )

        # 데이터 출처 결정
        from datetime import datetime
        target_date = datetime.strptime(game_date, "%Y-%m-%d").date()
        today = datetime.now().date()
        data_source = "forecast" if target_date >= today else "historical"

        return WeatherResponse(
            stadium=stadium_id,
            stadium_name=stadium_config["name"],
            game_date=game_date,
            game_hour=game_hour,
            data_source=data_source,
            **weather_data
        )

    except ValueError as e:
        logger.error(f"날씨 조회 요청 오류: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"날씨 조회 중 오류 발생: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="날씨 데이터 조회 중 오류가 발생했습니다."
        )


@router.post("/weather/timeline", response_model=WeatherTimelineResponse)
async def get_weather_timeline(
    timeline_request: WeatherTimelineRequest
) -> WeatherTimelineResponse:
    """
    날씨 타임라인 조회 엔드포인트

    경기 시간 전후의 시간대별 강수량 데이터를 조회합니다.

    - **stadium**: 구장 ID
    - **game_date**: 경기 날짜 (YYYY-MM-DD 형식)
    - **game_hour**: 경기 시작 시간 (0-23, 기본값 18시)
    - **hours_before**: 경기 전 몇 시간부터 조회할지 (기본값 3시간)
    - **hours_after**: 경기 후 몇 시간까지 조회할지 (기본값 3시간)
    """
    stadium_id = timeline_request.stadium
    game_date = timeline_request.game_date
    game_hour = timeline_request.game_hour
    hours_before = timeline_request.hours_before
    hours_after = timeline_request.hours_after

    # 구장 정보 확인
    stadium_config = STADIUM_MODELS.get(stadium_id)
    if not stadium_config:
        raise HTTPException(
            status_code=404,
            detail=f"{stadium_id} 구장은 지원하지 않습니다."
        )

    logger.info(
        f"[TIMELINE] 타임라인 조회 요청: stadium={stadium_id}, "
        f"date={game_date}, hour={game_hour}, "
        f"before={hours_before}h, after={hours_after}h"
    )

    try:
        # 타임라인 데이터 조회
        timeline_data = await weather_service.get_weather_timeline(
            stadium=stadium_id,
            game_date=game_date,
            game_hour=game_hour,
            hours_before=hours_before,
            hours_after=hours_after
        )

        return WeatherTimelineResponse(
            stadium=stadium_id,
            stadium_name=stadium_config["name"],
            game_date=game_date,
            game_hour=game_hour,
            **timeline_data
        )

    except ValueError as e:
        logger.error(f"타임라인 조회 요청 오류: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"타임라인 조회 중 오류 발생: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="타임라인 데이터 조회 중 오류가 발생했습니다."
        )
