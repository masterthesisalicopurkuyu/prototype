"""
Gemeinsame Geschäftslogik des Weather Service.

Diese Datei ist das Kernstück der funktionalen Äquivalenz (Bedingung 1,
Kap. 7.1): BEIDE Provider – der FastAPI REST-Server und der MCP-Server –
delegieren an dieselben Funktionen. Dadurch ist sichergestellt, dass
Unterschiede in den Messergebnissen nicht durch funktionale Differenzen
verursacht werden, sondern ausschließlich durch den Integrationsmechanismus.

Bass et al. (2021, Kap. 4) [Q8] bezeichnen dies als Entkopplung der
Geschäftslogik von der Integrationsschicht: Die Provider-Schicht stellt
Capabilities bereit, die Integrationsschicht macht sie zugänglich, und
der Agent konsumiert sie. Änderungen an der Geschäftslogik (z.B. neue
Datenfelder in Szenario A) werden hier vorgenommen und propagieren dann
über die jeweilige Integrationsschicht zum Agent – genau diese Propagation
ist Gegenstand der Messung.
"""

from provider.data import WEATHER_DATA, AVAILABLE_LOCATIONS
from provider.models import WeatherData, LocationList


def get_weather(location: str) -> WeatherData | None:
    """Wetterdaten für einen Standort abrufen.

    Args:
        location: Stadtname (case-sensitive).

    Returns:
        WeatherData-Objekt oder None, wenn der Standort nicht existiert.

    Diese Funktion wird von BEIDEN Providern aufgerufen:
    - REST: rest_server.py → GET /api/v1/weather?location={name}
    - MCP:  mcp_server.py  → Tool 'get_weather'
    """
    data = WEATHER_DATA.get(location)
    if data is None:
        return None
    return WeatherData(**data)


def get_locations() -> LocationList:
    """Liste aller verfügbaren Standorte abrufen.

    Returns:
        LocationList-Objekt mit allen Städtenamen.

    Diese Funktion wird von BEIDEN Providern aufgerufen:
    - REST: rest_server.py → GET /api/v1/locations
    - MCP:  mcp_server.py  → Resource 'weather://locations'
    """
    return LocationList(locations=AVAILABLE_LOCATIONS)
