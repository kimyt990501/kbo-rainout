"""
Open-Meteo API를 사용한 날씨 데이터 수집 서비스
"""
import logging
from datetime import datetime, timedelta
from typing import Optional
import httpx

from config import STADIUM_MODELS

logger = logging.getLogger(__name__)

# Open-Meteo API 엔드포인트
FORECAST_API_URL = "https://api.open-meteo.com/v1/forecast"
HISTORICAL_API_URL = "https://archive-api.open-meteo.com/v1/archive"


class WeatherService:
    """Open-Meteo API를 사용한 날씨 데이터 서비스"""

    def __init__(self, timeout: float = 10.0):
        self.timeout = timeout

    async def get_weather_for_game(
        self,
        stadium: str,
        game_date: str,
        game_hour: int = 18
    ) -> dict:
        """
        경기 날씨 데이터 조회

        Args:
            stadium: 구장 ID (예: "jamsil")
            game_date: 경기 날짜 (YYYY-MM-DD)
            game_hour: 경기 시작 시간 (0-23, 기본값 18시)

        Returns:
            모델 입력에 필요한 날씨 데이터 딕셔너리
        """
        # 구장 좌표 가져오기
        stadium_config = STADIUM_MODELS.get(stadium)
        if not stadium_config:
            raise ValueError(f"지원하지 않는 구장입니다: {stadium}")

        lat, lon = stadium_config["coordinates"]

        # 날짜 파싱
        target_date = datetime.strptime(game_date, "%Y-%m-%d")
        prev_date = target_date - timedelta(days=1)
        today = datetime.now().date()

        # 예보 vs 과거 데이터 결정
        is_forecast = target_date.date() >= today

        if is_forecast:
            weather_data = await self._fetch_forecast(lat, lon, game_date, game_hour)
        else:
            weather_data = await self._fetch_historical(lat, lon, game_date, game_hour)

        # 전날 강수량 조회
        prev_day_precip = await self._get_prev_day_precip(
            lat, lon, prev_date.strftime("%Y-%m-%d")
        )
        weather_data["prev_day_precip"] = prev_day_precip

        # month, dayofweek 추가
        weather_data["month"] = target_date.month
        # Python: 월=0 -> 모델: 월=0
        weather_data["dayofweek"] = target_date.weekday()

        logger.info(f"[WEATHER] stadium={stadium}, date={game_date}, data={weather_data}")

        return weather_data

    async def _fetch_forecast(
        self,
        lat: float,
        lon: float,
        date: str,
        game_hour: int
    ) -> dict:
        """예보 데이터 조회 (오늘 이후)"""
        params = {
            "latitude": lat,
            "longitude": lon,
            "hourly": "temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m",
            "daily": "precipitation_sum,precipitation_hours,temperature_2m_mean,wind_speed_10m_max",
            "timezone": "Asia/Seoul",
            "start_date": date,
            "end_date": date,
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(FORECAST_API_URL, params=params)
            response.raise_for_status()
            data = response.json()

        return self._parse_weather_data(data, game_hour)

    async def _fetch_historical(
        self,
        lat: float,
        lon: float,
        date: str,
        game_hour: int
    ) -> dict:
        """과거 데이터 조회"""
        params = {
            "latitude": lat,
            "longitude": lon,
            "hourly": "temperature_2m,relative_humidity_2m,precipitation,wind_speed_10m",
            "daily": "precipitation_sum,precipitation_hours,temperature_2m_mean,wind_speed_10m_max",
            "timezone": "Asia/Seoul",
            "start_date": date,
            "end_date": date,
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(HISTORICAL_API_URL, params=params)
            response.raise_for_status()
            data = response.json()

        return self._parse_weather_data(data, game_hour)

    async def _get_prev_day_precip(self, lat: float, lon: float, date: str) -> float:
        """전날 강수량 조회"""
        today = datetime.now().date()
        target_date = datetime.strptime(date, "%Y-%m-%d").date()

        # 오늘이나 미래면 예보 API, 과거면 아카이브 API
        if target_date >= today:
            api_url = FORECAST_API_URL
        else:
            api_url = HISTORICAL_API_URL

        params = {
            "latitude": lat,
            "longitude": lon,
            "daily": "precipitation_sum",
            "timezone": "Asia/Seoul",
            "start_date": date,
            "end_date": date,
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(api_url, params=params)
                response.raise_for_status()
                data = response.json()

            precip = data.get("daily", {}).get("precipitation_sum", [0])[0]
            return precip if precip is not None else 0.0
        except Exception as e:
            logger.warning(f"전날 강수량 조회 실패: {e}")
            return 0.0

    def _parse_weather_data(self, data: dict, game_hour: int) -> dict:
        """API 응답에서 모델 입력 데이터 추출"""
        daily = data.get("daily", {})
        hourly = data.get("hourly", {})

        # 일별 데이터
        daily_precip_sum = daily.get("precipitation_sum", [0])[0] or 0.0
        daily_precip_hours = daily.get("precipitation_hours", [0])[0] or 0.0
        daily_temp_mean = daily.get("temperature_2m_mean", [20])[0] or 20.0
        daily_wind_max = daily.get("wind_speed_10m_max", [5])[0] or 5.0

        # 경기 전 3시간 데이터 (game_hour-3 ~ game_hour)
        temps = hourly.get("temperature_2m", [])
        humidities = hourly.get("relative_humidity_2m", [])
        precips = hourly.get("precipitation", [])
        winds = hourly.get("wind_speed_10m", [])

        # 경기 전 3시간 인덱스 (예: 18시 경기면 15, 16, 17시)
        start_hour = max(0, game_hour - 3)
        end_hour = game_hour

        # 경기 전 3시간 강수량 합계
        pre_game_precip = sum(
            p for p in precips[start_hour:end_hour] if p is not None
        )

        # 경기 직전 시간의 기상 데이터 (game_hour - 1)
        pre_hour_idx = max(0, game_hour - 1)

        pre_game_humidity = (
            humidities[pre_hour_idx] if pre_hour_idx < len(humidities) else 60.0
        ) or 60.0

        pre_game_temp = (
            temps[pre_hour_idx] if pre_hour_idx < len(temps) else 20.0
        ) or 20.0

        pre_game_wind = (
            winds[pre_hour_idx] if pre_hour_idx < len(winds) else 5.0
        ) or 5.0

        return {
            "daily_precip_sum": round(daily_precip_sum, 1),
            "daily_precip_hours": round(daily_precip_hours, 1),
            "pre_game_precip": round(pre_game_precip, 1),
            "pre_game_humidity": round(pre_game_humidity, 1),
            "pre_game_temp": round(pre_game_temp, 1),
            "pre_game_wind": round(pre_game_wind, 1),
            "daily_wind_max": round(daily_wind_max, 1),
            "daily_temp_mean": round(daily_temp_mean, 1),
        }

    async def get_weather_timeline(
        self,
        stadium: str,
        game_date: str,
        game_hour: int = 18,
        hours_before: int = 3,
        hours_after: int = 3
    ) -> dict:
        """
        경기 시간 전후 타임라인 날씨 데이터 조회

        Args:
            stadium: 구장 ID
            game_date: 경기 날짜 (YYYY-MM-DD)
            game_hour: 경기 시작 시간 (0-23)
            hours_before: 경기 전 몇 시간부터 조회할지
            hours_after: 경기 후 몇 시간까지 조회할지

        Returns:
            타임라인 데이터 딕셔너리
        """
        # 구장 좌표 가져오기
        stadium_config = STADIUM_MODELS.get(stadium)
        if not stadium_config:
            raise ValueError(f"지원하지 않는 구장입니다: {stadium}")

        lat, lon = stadium_config["coordinates"]

        # 날짜 파싱
        target_date = datetime.strptime(game_date, "%Y-%m-%d")
        today = datetime.now().date()

        # 예보 vs 과거 데이터 결정
        is_forecast = target_date.date() >= today

        if is_forecast:
            api_url = FORECAST_API_URL
        else:
            api_url = HISTORICAL_API_URL

        params = {
            "latitude": lat,
            "longitude": lon,
            "hourly": "precipitation",
            "timezone": "Asia/Seoul",
            "start_date": game_date,
            "end_date": game_date,
        }

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(api_url, params=params)
            response.raise_for_status()
            data = response.json()

        hourly = data.get("hourly", {})
        precips = hourly.get("precipitation", [])

        # 타임라인 포인트 생성
        timeline = []
        start_hour = max(0, game_hour - hours_before)
        end_hour = min(23, game_hour + hours_after)

        total_precipitation = 0.0

        for hour in range(start_hour, end_hour + 1):
            if hour < len(precips):
                precipitation = precips[hour] or 0.0
            else:
                precipitation = 0.0

            total_precipitation += precipitation

            # 상대 시간 계산
            relative_hours = hour - game_hour
            if relative_hours == 0:
                relative_time = "경기 시작"
                is_game_time = True
            elif relative_hours < 0:
                relative_time = f"경기 {abs(relative_hours)}시간 전"
                is_game_time = False
            else:
                relative_time = f"경기 {relative_hours}시간 후"
                is_game_time = False

            # 시간 라벨 생성
            time_label = f"{hour:02d}:00"

            timeline.append({
                "hour": hour,
                "time_label": time_label,
                "precipitation": round(precipitation, 1),
                "is_game_time": is_game_time,
                "relative_time": relative_time
            })

        logger.info(
            f"[WEATHER_TIMELINE] stadium={stadium}, date={game_date}, "
            f"game_hour={game_hour}, points={len(timeline)}, "
            f"total_precip={round(total_precipitation, 1)}mm"
        )

        return {
            "timeline": timeline,
            "total_precipitation": round(total_precipitation, 1),
            "data_source": "forecast" if is_forecast else "historical"
        }


# 싱글톤 인스턴스
weather_service = WeatherService()
