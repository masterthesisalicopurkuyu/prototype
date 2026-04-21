"""
Pydantic-Datenmodelle für den Weather Service.

Diese Modelle definieren die Datenstruktur, die BEIDE Provider (REST und MCP)
verwenden. Die Verwendung identischer Modelle stellt funktionale Äquivalenz
sicher (Bedingung 1, vgl. Kap. 7.1): Unterschiede in den Messergebnissen
sind damit auf den Integrationsmechanismus zurückführbar, nicht auf
Datenformat-Differenzen.

Pydantic wird als Modellierungsbibliothek verwendet, weil:
- FastAPI nutzt Pydantic nativ für Request/Response-Validierung
- Pydantic-Modelle erzeugen automatisch JSON-Schemas, die mit der
  OpenAPI-Spezifikation (Q2: OpenAPI Initiative, 2021) kompatibel sind
- Die gleichen Modelle können im MCP-Server für die Tool-Output-
  Strukturierung verwendet werden
"""

from pydantic import BaseModel


class WeatherData(BaseModel):
    """Wetterdaten für einen Standort.

    Ab Szenario B (Breaking Change): Feld ``temperature_celsius`` als
    Objekt mit numerischem Wert und Einheit (statt flachem ``temp``).

    - location: Stadtname (String)
    - temperature_celsius: {"value": float, "unit": str}
    - wind_speed: Windgeschwindigkeit in km/h (Float)
    - condition: Wetterbedingung als Freitext (String)
    - timestamp: ISO-8601-Zeitstempel (String)
    """
    location: str
    temperature_celsius: dict  # {"value": float, "unit": str}
    wind_speed: float
    condition: str
    timestamp: str


class LocationList(BaseModel):
    """Liste verfügbarer Standorte.

    Wird vom GET /api/v1/locations Endpunkt (REST) bzw. der
    weather://locations Resource (MCP) zurückgegeben.
    """
    locations: list[str]
