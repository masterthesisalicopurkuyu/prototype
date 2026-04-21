"""
REST-Provider: WeatherDataService (Port 8000) – Szenario D (strukturelles Refactoring).

Exponiert nur GET /api/v1/weather. Standorte liegen auf dem LocationService
(Port 8001, rest_location_server.py).

OpenAPI unter /docs und /openapi.json bleibt pro Dienst verfügbar (je eine Spec).
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, HTTPException
from provider.weather_service import get_weather, get_locations
from provider.models import WeatherData

app = FastAPI(
    title="Weather Data Service",
    description="Minimal Weather API nach Provider-Aufteilung (Szenario D)",
    version="1.0.0",
)


@app.get(
    "/api/v1/weather",
    response_model=WeatherData,
    summary="Wetterdaten für einen Standort abrufen",
)
async def api_get_weather(location: str) -> WeatherData:
    result = get_weather(location)
    if result is None:
        raise HTTPException(
            status_code=404,
            detail=f"Location '{location}' not found. "
            f"Available: {get_locations().locations}",
        )
    return result


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
