"""
REST-Provider: FastAPI-Server für den Weather Service.

Dieser Server exponiert die Geschäftslogik als RESTful HTTP-API und folgt
den REST-Constraints nach Fielding (2000) [Q1]:

- Uniform Interface: Ressourcenbasierte URIs (/api/v1/weather,
  /api/v1/locations) mit standardisierten HTTP-Methoden (GET).
- Statelessness: Jeder Request enthält alle nötigen Informationen;
  der Server hält keinen Client-State.
- Client-Server: Klare Trennung zwischen Provider und Consumer.

FastAPI wurde gewählt, weil es automatisch eine OpenAPI-Spezifikation
(Q2: OpenAPI Initiative, 2021) generiert (/docs, /openapi.json). Diese
maschinenlesbare Beschreibung dient als Referenzdokumentation für die
Impact-Analyse (M2) bei Provider-Änderungen. Die auto-generierte Spec
zeigt den Unterschied zu MCP: Bei REST ist die API-Beschreibung ein
STATISCHES Dokument, das der Entwickler manuell konsultieren muss. Bei
MCP liefert tools/list dieselbe Information DYNAMISCH zur Laufzeit.

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
    """GET /api/v1/weather?location={name}

    Kopplungspunkte für den Consumer (REST-Integrationsschicht):
    - URL-Pfad: /api/v1/weather (hardcoded in config.json)
    - Query-Parameter: location (hardcoded in rest_client.py)
    - Response-Feldnamen: location, temp, wind_speed, condition, timestamp
      (hardcoded in response_mapper.py und tool_definitions.py)
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
    """GET /api/v1/locations

    Kopplungspunkte für den Consumer:
    - URL-Pfad: /api/v1/locations (hardcoded in config.json)
    - Response-Feld: locations (Array von Strings)
    """
    return get_locations()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="127.0.0.1", port=8000)
