"""
MCP-Provider: WeatherDataService – Szenario D (strukturelles Refactoring).

Registriert nur get_weather; Standorte liegen auf mcp_location_server.py.
"""

import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp.server.fastmcp import FastMCP
from provider.weather_service import get_weather, get_locations

mcp = FastMCP(
    name="Weather Data MCP",
    instructions="Provides current weather data for German cities.",
)


@mcp.tool(
    name="get_weather",
    description="Get current weather data for a specific city. "
    "Returns temperature, wind speed, weather condition, and humidity.",
)
def get_weather_tool(location: str) -> str:
    result = get_weather(location)
    if result is None:
        available = get_locations().locations
        return json.dumps({
            "error": f"Location '{location}' not found.",
            "available_locations": available,
        })
    return result.model_dump_json()


if __name__ == "__main__":
    mcp.run()
