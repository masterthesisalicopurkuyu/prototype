import sys
import os
import json

# Projektroot zum Python-Path hinzufügen
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp.server.fastmcp import FastMCP
from provider.weather_service import get_weather, get_locations

# MCP-Server-Instanz
mcp = FastMCP(
    name="Weather Service MCP",
    instructions="Provides current weather data for German cities.",
)


@mcp.tool(
    name="get_weather",
    description="Get current weather data for a specific city. "
    "Returns temperature, wind speed, and weather condition.",
)
def get_weather_tool(location: str) -> str:
    """Liefert Wetterdaten für den angegebenen Standort.
    """
    result = get_weather(location)
    if result is None:
        available = get_locations().locations
        return json.dumps({
            "error": f"Location '{location}' not found.",
            "available_locations": available,
        })
    return result.model_dump_json()


@mcp.resource("weather://locations")
def get_locations_resource() -> str:
    """Liefert die verfügbaren Wetterstandorte.
    """
    result = get_locations()
    return result.model_dump_json()


if __name__ == "__main__":
    # Startet den MCP-Server über stdio-Transport
    # (Standard-Transport für lokale MCP-Server)
    mcp.run()
