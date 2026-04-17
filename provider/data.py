"""
Statische Wetterdaten (In-Memory).

Die Verwendung statischer In-Memory-Daten anstelle einer externen Datenbank
ist eine bewusste Designentscheidung:

1. Keine externe DB-Abhängigkeit: Eine Datenbank wäre eine Störvariable,
   die bei beiden Varianten identisch wäre, aber die Reproduzierbarkeit
   (R11) gefährden könnte (DB-Version, Konfiguration, Netzwerk).

2. Deterministische Ergebnisse: Rein lesende Operationen auf statische
   Daten erzeugen bei jedem Aufruf identische Ergebnisse. Dies ist
   Voraussetzung für die Vergleichbarkeit der Agent-Antworten zwischen
   REST- und MCP-Variante.

3. Minimale Komplexität (Bedingung 2, Kap. 7.1): Die Komplexität der
   Arbeit liegt im Bewertungsrahmen, nicht in der Datenquelle.

Drei Städte (Stuttgart, Berlin, München) reichen aus, um die
Provider-Funktionalität zu demonstrieren und alle vier Szenarien
durchzuführen.
"""

from datetime import datetime, timezone

# Statische Wetterdaten – V1 Baseline
# Die Daten werden von weather_service.py abgerufen und von beiden
# Providern (REST und MCP) identisch ausgeliefert.
WEATHER_DATA: dict[str, dict] = {
    "Stuttgart": {
        "location": "Stuttgart",
        "temperature_celsius": {"value": 22.5, "unit": "°C"},
        "wind_speed": 15.3,
        "condition": "sunny",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    },
    "Berlin": {
        "location": "Berlin",
        "temperature_celsius": {"value": 18.0, "unit": "°C"},
        "wind_speed": 22.1,
        "condition": "cloudy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    },
    "München": {
        "location": "München",
        "temperature_celsius": {"value": 20.3, "unit": "°C"},
        "wind_speed": 10.5,
        "condition": "partly cloudy",
        "timestamp": datetime.now(timezone.utc).isoformat(),
    },
}

# Liste der verfügbaren Standorte
AVAILABLE_LOCATIONS: list[str] = list(WEATHER_DATA.keys())
