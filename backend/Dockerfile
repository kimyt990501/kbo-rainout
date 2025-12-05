# KBO 우천취소 예측 API - Docker 이미지
FROM python:3.11-slim

# 환경 변수 설정
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    MODEL_DIR=/app/models_data

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 의존성 설치 (XGBoost에 필요한 libgomp)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# 의존성 파일 복사 및 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 복사
COPY . .

# 모델 데이터 디렉토리 생성 (docker-compose에서 볼륨 마운트용)
RUN mkdir -p /app/models_data

# 포트 노출
EXPOSE 8600

# 헬스체크
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8600/api/health')" || exit 1

# 실행 명령
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8600"]
