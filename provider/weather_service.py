from provider.data import WEATHER_DATA, AVAILABLE_LOCATIONS
from provider.models import WeatherData, LocationList


def get_weather(location: str) -> WeatherData | None:
    """Wetterdaten für einen Standort abrufen.

    Args:
        location: Stadtname (case-sensitive).

    Returns:
        WeatherData-Objekt oder None, wenn der Standort nicht existiert.
    """
    data = WEATHER_DATA.get(location)
    if data is None:
        return None
    return WeatherData(**data)


def get_locations() -> LocationList:
    """Liste aller verfügbaren Standorte abrufen.

    Returns:
        LocationList-Objekt mit allen Städtenamen.
    """
    return LocationList(locations=AVAILABLE_LOCATIONS)
