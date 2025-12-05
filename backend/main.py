"""
KBO 우천취소 예측 API - FastAPI 앱 진입점 (다중 구장 지원)
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import (
    API_TITLE,
    API_DESCRIPTION,
    API_VERSION,
    CORS_ORIGINS,
)
from api.routes import router
from models.predictor import MultiStadiumPredictor

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    앱 생명주기 관리

    시작 시 모든 구장 모델을 로드하고, 종료 시 정리 작업을 수행합니다.
    """
    # Startup
    logger.info("=== KBO 우천취소 예측 API 시작 (다중 구장 지원) ===")

    # 다중 구장 모델 로딩
    predictor = MultiStadiumPredictor()
    try:
        predictor.load_all_models()
        app.state.predictor = predictor

        loaded_stadiums = predictor.get_loaded_stadiums()
        logger.info(f"로딩 완료된 구장: {loaded_stadiums}")

    except RuntimeError as e:
        logger.error(f"모델 로딩 실패: {e}")
        raise
    except Exception as e:
        logger.error(f"모델 로딩 중 오류 발생: {e}")
        raise

    yield

    # Shutdown
    logger.info("=== KBO 우천취소 예측 API 종료 ===")


# FastAPI 앱 생성
app = FastAPI(
    title=API_TITLE,
    description=API_DESCRIPTION,
    version=API_VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# CORS 미들웨어 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(router)


@app.get("/", tags=["root"])
async def root():
    """루트 엔드포인트"""
    return {
        "message": "KBO 우천취소 예측 API (다중 구장 지원)",
        "version": API_VERSION,
        "docs": "/docs",
        "endpoints": {
            "stadiums": "/api/stadiums",
            "predict": "/api/predict",
            "model_info": "/api/model-info",
            "health": "/api/health",
        }
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8600,
        reload=True,
    )
