# KBO Rainout Predictor

KBO(한국야구위원회) 경기의 우천취소 가능성을 예측하는 머신러닝 기반 웹 애플리케이션입니다.

## 프로젝트 개요

이 프로젝트는 과거 KBO 경기 데이터와 기상 데이터를 분석하여 특정 날씨 조건에서 경기가 취소될 확률을 예측합니다. 잠실, 대구, 수원 등 주요 야구장별로 최적화된 머신러닝 모델을 사용합니다.

## 기술 스택

### Backend
- **Framework**: FastAPI 0.109+
- **ML Libraries**: XGBoost, LightGBM, scikit-learn
- **Data Processing**: Pandas, NumPy
- **Server**: Uvicorn

### Frontend
- **Framework**: Vue 3.4
- **Language**: TypeScript 5.4
- **State Management**: Pinia
- **Routing**: Vue Router
- **Build Tool**: Vite 5.0
- **HTTP Client**: Axios

### Infrastructure
- **Containerization**: Docker, Docker Compose
- **Web Server**: Nginx (프론트엔드)

## 프로젝트 구조

```
kbo_cancel/
├── backend/                    # FastAPI 백엔드
│   ├── api/                    # API 라우트
│   ├── models/                 # ML 모델 로딩 및 예측
│   ├── schemas/                # Pydantic 스키마
│   ├── services/               # 비즈니스 로직
│   ├── config.py               # 설정
│   └── main.py                 # 애플리케이션 엔트리포인트
├── frontend/                   # Vue.js 프론트엔드
│   ├── src/
│   │   ├── api/                # API 클라이언트
│   │   ├── components/         # Vue 컴포넌트
│   │   ├── pages/              # 페이지 컴포넌트
│   │   ├── router/             # 라우터 설정
│   │   ├── store/              # Pinia 스토어
│   │   └── styles/             # 스타일시트
│   └── public/                 # 정적 파일
├── models/                     # 학습된 ML 모델 파일
│   ├── kbo_jamsil_model.pkl
│   ├── kbo_daegu_model.pkl
│   └── *.png                   # EDA 및 Feature Importance 이미지
├── data/                       # 경기 및 날씨 데이터
│   ├── jamsil/
│   ├── daegu/
│   └── suwon/
├── cancel_crawler.py           # KBO 경기 데이터 크롤러
├── weather_collector_openmeteo.py  # 날씨 데이터 수집기
├── kbo_rain_model.py           # 모델 학습 스크립트
├── run_pipeline.py             # 전체 파이프라인 실행
├── stadium_config.py           # 구장 설정
└── docker-compose.yml          # Docker Compose 설정
```

## 설치 및 실행

### 사전 요구사항
- Docker & Docker Compose
- Python 3.11+ (로컬 개발 시)
- Node.js 18+ (로컬 개발 시)

### Docker Compose로 실행하기

```bash
# 전체 애플리케이션 실행
docker-compose up -d

# 프론트엔드 접속
# http://localhost:8080

# 백엔드 API 접속
# http://localhost:8600/docs
```

### 로컬 개발 환경

#### 백엔드 실행

```bash
cd backend

# 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 서버 실행
uvicorn main:app --reload --host 0.0.0.0 --port 8600
```

#### 프론트엔드 실행

```bash
cd frontend

# 의존성 설치
npm install

# 개발 서버 실행
npm run dev

# 프로덕션 빌드
npm run build
```

## 주요 기능

### 1. 경기 취소 확률 예측
- 날씨 조건(강수량, 강수 확률, 기온, 풍속 등)을 입력하면 경기 취소 확률을 실시간으로 계산
- 구장별로 최적화된 머신러닝 모델 사용

### 2. 구장별 모델
- 잠실 야구장
- 대구 삼성 라이온즈 파크
- 수원 KT 위즈 파크
- 각 구장의 특성을 반영한 개별 모델

### 3. 데이터 파이프라인
- KBO 공식 사이트에서 경기 데이터 크롤링
- Open-Meteo API를 통한 과거 기상 데이터 수집
- 자동화된 데이터 병합 및 전처리

### 4. 모델 학습 및 평가
- XGBoost 기반 분류 모델
- Feature Importance 시각화
- 성능 평가 및 모델 저장

## API 엔드포인트

### Health Check
```
GET /api/health
```

### 예측
```
POST /api/predict
Content-Type: application/json

{
  "stadium": "jamsil",
  "precipitation": 5.0,
  "precipitation_probability": 60,
  "temperature": 15.0,
  "wind_speed": 8.0,
  "humidity": 70
}
```

## 데이터 수집 및 모델 학습

### 1. 경기 데이터 크롤링
```bash
python cancel_crawler.py
```

### 2. 날씨 데이터 수집
```bash
python weather_collector_openmeteo.py
```

### 3. 모델 학습
```bash
python kbo_rain_model.py
```

### 4. 전체 파이프라인 실행
```bash
python run_pipeline.py
```

## 환경 변수

### Backend
환경 변수가 필요한 경우 `.env` 파일을 생성하세요:
```
MODEL_DIR=./models
```

### Frontend
`frontend/.env.development` 및 `frontend/.env.production` 파일에서 API 엔드포인트를 설정할 수 있습니다.

## 라이선스

이 프로젝트는 개인 프로젝트입니다.

## 기여

버그 리포트 및 기능 제안은 Issues를 통해 제출해주세요.
