from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.request import urlopen
from urllib.error import URLError

LATITUDE = 51.0197
LONGITUDE = -4.2079
LOCATION_NAME = "Bideford, England"

DATA_DIR = Path(__file__).parent.parent / "data"
OUTPUT_PATH = DATA_DIR / "weather.json"

API_URL = (
    "https://api.open-meteo.com/v1/forecast"
    f"?latitude={LATITUDE}&longitude={LONGITUDE}"
    "&current=temperature_2m,weather_code"
    "&daily=temperature_2m_max,temperature_2m_min"
    "&timezone=auto&forecast_days=1"
)

WEATHER_CODE_MAP: dict[int, tuple[str, str]] = {
    0: ("clear", "Clear Sky"),
    1: ("mostly-clear", "Mostly Clear"),
    2: ("partly-cloudy", "Partly Cloudy"),
    3: ("cloudy", "Overcast"),
    45: ("fog", "Fog"),
    48: ("fog", "Fog"),
    51: ("drizzle", "Light Drizzle"),
    53: ("drizzle", "Drizzle"),
    55: ("drizzle", "Heavy Drizzle"),
    61: ("rain", "Light Rain"),
    63: ("rain", "Rain"),
    65: ("rain", "Heavy Rain"),
    71: ("snow", "Light Snow"),
    73: ("snow", "Snow"),
    75: ("snow", "Heavy Snow"),
    80: ("rain", "Rain Showers"),
    81: ("rain", "Rain Showers"),
    82: ("rain", "Violent Showers"),
    95: ("thunderstorm", "Thunderstorm"),
    96: ("thunderstorm", "Thunderstorm"),
    99: ("thunderstorm", "Severe Thunderstorm"),
}

FALLBACK_ICON, FALLBACK_CONDITION = "cloudy", "Unknown"


def fetch_weather() -> dict[str, Any]:
    with urlopen(API_URL, timeout=10) as response:
        raw = json.loads(response.read())

    current = raw["current"]
    daily = raw["daily"]

    code = current["weather_code"]
    icon, condition = WEATHER_CODE_MAP.get(code, (FALLBACK_ICON, FALLBACK_CONDITION))

    return {
        "location": LOCATION_NAME,
        "temperature_c": round(current["temperature_2m"]),
        "condition": condition,
        "icon": icon,
        "high_c": round(daily["temperature_2m_max"][0]),
        "low_c": round(daily["temperature_2m_min"][0]),
        "updated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }


def write_weather_json(weather: dict[str, Any]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(json.dumps(weather, indent=2) + "\n")


def main() -> None:
    try:
        weather = fetch_weather()
        write_weather_json(weather)
        print(f"[weather] Updated: {weather['temperature_c']}°C, {weather['condition']}")
        exit(0)
    except Exception as error:
        print(f"[weather] Fetch failed, keeping existing data: {error}")
        exit(0)


if __name__ == "__main__":
    main()
