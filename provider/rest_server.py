"""
REST-Provider: FastAPI-Server für den Weather Service.

Port 8000 als Default-Port für den REST-Provider.
"""

import sys
import os

# Projektroot zum Python-Path hinzufügen
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, HTTPException
from provider.weather_service import get_weather, get_locations
from provider.models import WeatherData, LocationList

app = FastAPI(
    title="Weather Service API",
    description="Minimal Weather Service für den Prototyp-Vergleich REST vs. MCP",
    version="1.0.0",
)


@app.get(
    "/api/v1/weather",
    response_model=WeatherData,
    summary="Wetterdaten für einen Standort abrufen",
    description="Gibt aktuelle Wetterdaten für den angegebenen Standort zurück.",
)
async def api_get_weather(location: str) -> WeatherData:
    """Liefert Wetterdaten für den angegebenen Standort.
    """
    result = get_weather(location)
    if result is None:
        raise HTTPException(
            status_code=404,
            detail=f"Location '{location}' not found. "
            f"Available: {get_locations().locations}",
        )
    return result


@app.get(
    "/api/v1/locations",
    response_model=LocationList,
    summary="Verfügbare Standorte auflisten",
    description="Gibt eine Liste aller verfügbaren Standorte zurück.",
)
async def api_get_locations() -> LocationList:
    """Liefert die verfügbaren Wetterstandorte.
    """
    return get_locations()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
