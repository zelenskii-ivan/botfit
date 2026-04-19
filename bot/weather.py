"""Прогноз погоды на завтро (OpenWeatherMap), кэш 3 ч в shelf.weather."""
from __future__ import annotations

import logging
from datetime import date, datetime, timedelta
from typing import Any

import httpx

from bot.config import WEATHER_API_KEY, WEATHER_LAT, WEATHER_LON, WEATHER_CITY

log = logging.getLogger(__name__)

CACHE_TTL_SEC = 3 * 3600


def _tomorrow_date_str() -> str:
    return (date.today() + timedelta(days=1)).strftime("%Y-%m-%d")


async def fetch_tomorrow_forecast_openweather() -> dict[str, Any]:
    if not WEATHER_API_KEY:
        raise RuntimeError("WEATHER_API_KEY не задан")

    async with httpx.AsyncClient(timeout=30.0) as client:
        url = "https://api.openweathermap.org/data/2.5/forecast"
        if WEATHER_LAT is not None and WEATHER_LON is not None:
            params: dict = {
                "lat": WEATHER_LAT,
                "lon": WEATHER_LON,
                "appid": WEATHER_API_KEY,
                "units": "metric",
                "lang": "ru",
            }
        else:
            params = {
                "q": WEATHER_CITY,
                "appid": WEATHER_API_KEY,
                "units": "metric",
                "lang": "ru",
            }
        r = await client.get(url, params=params)
        r.raise_for_status()
        data = r.json()

    tomorrow = _tomorrow_date_str()
    samples: list[dict[str, Any]] = []
    for item in data.get("list", []):
        dt_txt = item.get("dt_txt", "")
        if dt_txt.startswith(tomorrow):
            samples.append(item)

    if not samples:
        for item in data.get("list", [])[:5]:
            samples.append(item)

    if not samples:
        return {
            "date": tomorrow,
            "temp_min": None,
            "temp_max": None,
            "description": "нет данных",
            "rain": False,
            "snow": False,
        }

    temps: list[float] = []
    descs: list[str] = []
    rain = False
    snow = False
    for s in samples:
        main = s.get("main") or {}
        if "temp" in main:
            temps.append(float(main["temp"]))
        w0 = (s.get("weather") or [{}])[0]
        if w0.get("description"):
            descs.append(w0["description"])
        if s.get("rain"):
            rain = True
        if s.get("snow"):
            snow = True

    return {
        "date": tomorrow,
        "temp_min": min(temps) if temps else None,
        "temp_max": max(temps) if temps else None,
        "description": descs[len(descs) // 2] if descs else "переменная облачность",
        "rain": rain,
        "snow": snow,
    }


async def get_tomorrow_weather_cached() -> dict[str, Any]:
    from bot import state as state_mod

    now = datetime.now()
    cache = state_mod.shelf.get("weather") or {}
    cached_at = cache.get("cached_at")
    data = cache.get("tomorrow")

    if cached_at and data:
        try:
            ts = datetime.fromisoformat(cached_at)
            if (now - ts).total_seconds() < CACHE_TTL_SEC:
                return data
        except (TypeError, ValueError):
            pass

    fresh = await fetch_tomorrow_forecast_openweather()
    state_mod.shelf["weather"] = {
        "tomorrow": fresh,
        "cached_at": now.isoformat(timespec="seconds"),
    }
    state_mod.save_shelf_persist()
    return fresh
