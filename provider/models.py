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

    Felder entsprechen der V1-Baseline-Spezifikation (Kap. 7.7):
    - location: Stadtname (String)
    - temp: Temperatur in Celsius (Float)
    - wind_speed: Windgeschwindigkeit in km/h (Float)
    - condition: Wetterbedingung als Freitext (String)
    - timestamp: ISO-8601-Zeitstempel (String)

    WICHTIG: Die Feldnamen (insb. 'temp') sind bewusst gewählt, um in
    Szenario B (Breaking Change) eine Umbenennung zu 'temperature_celsius'
    durchführen zu können. Die Kurzform 'temp' ist ein realistisches Muster
    in API-Designs, das häufig zu Breaking Changes führt (vgl. P8: Espinha,
    Zaidman & Gross, 2015 – API Evolution Patterns).
    """
    location: str
    temp: float
    wind_speed: float
    condition: str
    timestamp: str


class LocationList(BaseModel):
    """Liste verfügbarer Standorte.

    Wird vom GET /api/v1/locations Endpunkt (REST) bzw. der
    weather://locations Resource (MCP) zurückgegeben.
    """
    locations: list[str]
