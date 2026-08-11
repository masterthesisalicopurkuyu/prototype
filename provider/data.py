from datetime import datetime, timezone

# Statische Wetterdaten – V1 Baseline
# Die Daten werden von weather_service.py abgerufen und von beiden
# Providern (REST und MCP) identisch ausgeliefert.
WEATHER_DATA: dict[str, dict] = {
    "Stuttgart": {
        "location": "Stuttgart",
        "temp": 22.5,
        "wind_speed": 15.3,
        "condition": "sunny",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    },
    "Berlin": {
        "location": "Berlin",
        "temp": 18.0,
        "wind_speed": 22.1,
        "condition": "cloudy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    },
    "München": {
        "location": "München",
        "temp": 20.3,
        "wind_speed": 10.5,
        "condition": "partly cloudy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    },
}

# Liste der verfügbaren Standorte
AVAILABLE_LOCATIONS: list[str] = list(WEATHER_DATA.keys())
