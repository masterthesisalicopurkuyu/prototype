"""
REST-Provider: LocationService (Port 8001) – Szenario D (strukturelles Refactoring).

Exponiert nur GET /api/v1/locations; Wetterdaten liegen auf dem WeatherDataService
(Port 8000, rest_server.py).
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from provider.weather_service import get_locations
from provider.models import LocationList

app = FastAPI(
    title="Location Service",
    description="Standalone Location API nach Provider-Aufteilung (Szenario D)",
    version="1.0.0",
)


@app.get(
    "/api/v1/locations",
    response_model=LocationList,
    summary="Verfügbare Standorte auflisten",
)
async def api_get_locations() -> LocationList:
    return get_locations()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8001)
