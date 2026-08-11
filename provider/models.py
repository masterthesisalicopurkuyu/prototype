from pydantic import BaseModel


class WeatherData(BaseModel):
    """Wetterdaten für einen Standort.

    Felder entsprechen der V1-Baseline-Spezifikation:
    - location: Stadtname (String)
    - temp: Temperatur in Celsius (Float)
    - wind_speed: Windgeschwindigkeit in km/h (Float)
    - condition: Wetterbedingung als Freitext (String)
    - timestamp: ISO-8601-Zeitstempel (String)
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
