"""
MCP-Provider: MCP-Server für den Weather Service.

Dieser Server exponiert dieselbe Geschäftslogik wie der REST-Provider,
nutzt jedoch das Model Context Protocol (MCP) als Integrationsparadigma.

Architektonische Unterschiede zu REST (vgl. MCP Specification [Q3]):

1. Capability-Registration statt Endpoint-Definition:
   Statt HTTP-Endpunkte mit URLs zu definieren, registriert der MCP-Server
   Tools (aufrufbare Funktionen) und Resources (lesbare Datenquellen).
   Der Client entdeckt diese via tools/list und resources/list zur LAUFZEIT.

2. JSON-RPC 2.0 statt RESTful HTTP:
   Die Kommunikation erfolgt über JSON-RPC 2.0 (Q9: JSON-RPC Working
   Group, 2013) anstelle von HTTP-Verben auf ressourcenbasierten URIs.
   Dies ist ein Protokoll-Unterschied, kein Paradigmen-Unterschied – aber
   er beeinflusst die Kopplungsstruktur der Integrationsschicht.

3. Maschinenlesbare Schemas:
   Tool-Definitionen (Name, Description, Input-Schema) werden vom Server
   bereitgestellt und vom Client dynamisch abgerufen. Bei REST muss der
   Entwickler diese Definitionen manuell als Function-Calling-Schemas
   schreiben (tool_definitions.py).

FastMCP (High-Level API des MCP Python SDK) wird verwendet, weil es die
Protokoll-Boilerplate kapselt und die Tool/Resource-Registration
deklarativ ermöglicht.
"""

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
    description="[DEPRECATED – use get_weather_v2] Get current weather data for a specific city. "
    "Returns temperature, wind speed, and weather condition.",
)
def get_weather_tool(location: str) -> str:
    """MCP-Tool für Wetterdaten (deprecated)."""
    result = get_weather(location)
    if result is None:
        available = get_locations().locations
        return json.dumps({
            "error": f"Location '{location}' not found.",
            "available_locations": available,
        })
    return result.model_dump_json()


@mcp.tool(
    name="get_weather_v2",
    description="Get current weather data for a specific city (V2 – preferred). "
    "Returns temperature, wind speed, and weather condition.",
)
def get_weather_v2_tool(location: str) -> str:
    """MCP-Tool für Wetterdaten (V2)."""
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
    """List all available weather locations.

    Diese Resource ist das MCP-Äquivalent zum GET /api/v1/locations
    Endpunkt des REST-Providers. Der Unterschied: Resources werden
    via resources/list entdeckt und über die Resource-URI abgerufen,
    nicht über einen HTTP-Endpoint-Pfad.
    """
    result = get_locations()
    return result.model_dump_json()


if __name__ == "__main__":
    # Startet den MCP-Server über stdio-Transport
    # (Standard-Transport für lokale MCP-Server)
    mcp.run()
