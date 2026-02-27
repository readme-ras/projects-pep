"""
Weather tool — wraps Open-Meteo (free, no API key needed)
+ optional OpenWeatherMap for richer data (set OWM_API_KEY in .env).
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

OWM_KEY   = os.getenv("OWM_API_KEY", "")
GEO_URL   = "https://geocoding-api.open-meteo.com/v1/search"
METEO_URL = "https://api.open-meteo.com/v1/forecast"
OWM_URL   = "https://api.openweathermap.org/data/2.5/weather"

# ── Schema exposed to the agent ────────────────────────────────────────────────

TOOL_SCHEMA = {
    "name": "get_weather",
    "description": (
        "Get the current weather for any city. "
        "Returns temperature, feels-like, humidity, wind speed, and a short description."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "city": {
                "type": "string",
                "description": "City name, e.g. 'London' or 'New York'",
            },
            "units": {
                "type": "string",
                "enum": ["celsius", "fahrenheit"],
                "description": "Temperature unit (default: celsius)",
            },
        },
        "required": ["city"],
    },
}


# ── Geocoding ──────────────────────────────────────────────────────────────────

def _geocode(city: str) -> tuple[float, float, str]:
    """Return (lat, lon, resolved_name) for a city string."""
    resp = requests.get(GEO_URL, params={"name": city, "count": 1}, timeout=10)
    resp.raise_for_status()
    results = resp.json().get("results", [])
    if not results:
        raise ValueError(f"City not found: '{city}'")
    r = results[0]
    name = f"{r['name']}, {r.get('country', '')}"
    return r["latitude"], r["longitude"], name


# ── Weather fetch ──────────────────────────────────────────────────────────────

def _open_meteo(lat: float, lon: float, fahrenheit: bool) -> dict:
    temp_unit = "fahrenheit" if fahrenheit else "celsius"
    wind_unit = "mph" if fahrenheit else "kmh"
    params = {
        "latitude":          lat,
        "longitude":         lon,
        "current":           "temperature_2m,apparent_temperature,relative_humidity_2m,wind_speed_10m,weather_code",
        "temperature_unit":  temp_unit,
        "wind_speed_unit":   wind_unit,
        "timezone":          "auto",
    }
    resp = requests.get(METEO_URL, params=params, timeout=10)
    resp.raise_for_status()
    cur = resp.json()["current"]
    return {
        "temperature":    round(cur["temperature_2m"], 1),
        "feels_like":     round(cur["apparent_temperature"], 1),
        "humidity":       cur["relative_humidity_2m"],
        "wind_speed":     round(cur["wind_speed_10m"], 1),
        "description":    _wmo_description(cur["weather_code"]),
        "temp_unit":      "°F" if fahrenheit else "°C",
        "wind_unit":      wind_unit,
        "source":         "Open-Meteo",
    }


def _wmo_description(code: int) -> str:
    """Map WMO weather interpretation code to human text."""
    table = {
        0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
        45: "Foggy", 48: "Icy fog",
        51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
        61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
        71: "Slight snow", 73: "Moderate snow", 75: "Heavy snow",
        80: "Slight rain showers", 81: "Moderate rain showers", 82: "Violent rain showers",
        95: "Thunderstorm", 96: "Thunderstorm with hail", 99: "Heavy thunderstorm with hail",
    }
    return table.get(code, f"Weather code {code}")


# ── Public function called by the agent ───────────────────────────────────────

def get_weather(city: str, units: str = "celsius") -> dict:
    fahrenheit = units.lower() == "fahrenheit"
    lat, lon, resolved = _geocode(city)
    data = _open_meteo(lat, lon, fahrenheit)
    data["city"] = resolved
    data["lat"]  = lat
    data["lon"]  = lon
    return data
