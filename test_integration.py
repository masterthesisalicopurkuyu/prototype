"""
Automatisierter Integrationstest – prüft alle Schichten ohne LLM.

Dieser Test verifiziert:
1. Provider-Schicht: Geschäftslogik liefert korrekte Daten
2. REST-Integrationsschicht: HTTP-Calls + Response-Mapping funktionieren
3. MCP-Integrationsschicht: tools/list + call_tool funktionieren
4. Funktionale Äquivalenz: Beide Varianten liefern identische Daten

KEIN LLM nötig – der Test prüft die Infrastruktur, nicht den Agent.
"""

import asyncio
import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


async def test_provider():
    """Test 1: Provider-Geschäftslogik."""
    print("\n[1] Provider-Geschäftslogik testen...")
    from provider.weather_service import get_weather, get_locations

    weather = get_weather("Stuttgart")
    assert weather is not None, "Stuttgart sollte existieren"
    assert weather.location == "Stuttgart"
    assert weather.temp == 22.5
    assert weather.condition == "sunny"
    print(f"    ✓ get_weather('Stuttgart') = {weather.temp}°C, {weather.condition}")

    none_result = get_weather("Atlantis")
    assert none_result is None, "Atlantis sollte None sein"
    print("    ✓ get_weather('Atlantis') = None")

    locations = get_locations()
    assert len(locations.locations) == 3
    assert "Stuttgart" in locations.locations
    print(f"    ✓ get_locations() = {locations.locations}")


async def test_rest_integration():
    """Test 2: REST-Integrationsschicht (REST-Server muss laufen!)."""
    print("\n[2] REST-Integrationsschicht testen...")
    import httpx

    try:
        async with httpx.AsyncClient() as client:
            # Weather-Endpoint
            r = await client.get(
                "http://127.0.0.1:8000/api/v1/weather",
                params={"location": "Stuttgart"},
            )
            assert r.status_code == 200
            data = r.json()
            assert data["location"] == "Stuttgart"
            assert data["temp"] == 22.5
            print(f"    ✓ GET /api/v1/weather?location=Stuttgart → {data['temp']}°C")

            # Locations-Endpoint
            r = await client.get("http://127.0.0.1:8000/api/v1/locations")
            assert r.status_code == 200
            data = r.json()
            assert len(data["locations"]) == 3
            print(f"    ✓ GET /api/v1/locations → {data['locations']}")

            # Tool-Definitionen
            from integration_rest.tool_definitions import TOOL_DEFINITIONS
            assert len(TOOL_DEFINITIONS) == 2
            assert TOOL_DEFINITIONS[0]["function"]["name"] == "get_weather"
            print(f"    ✓ tool_definitions.py → {len(TOOL_DEFINITIONS)} Tools definiert")

            # Response-Mapping
            from integration_rest.response_mapper import map_response
            mapped = map_response("get_weather", {
                "location": "Stuttgart", "temp": 22.5,
                "wind_speed": 15.3, "condition": "sunny"
            })
            assert "22.5°C" in mapped
            print(f"    ✓ response_mapper → '{mapped[:50]}...'")

            # RestToolExecutor
            from integration_rest.rest_client import RestToolExecutor
            executor = RestToolExecutor("integration_rest/config.json")
            tools = await executor.get_available_tools()
            assert len(tools) == 2
            result = await executor.execute("get_weather", {"location": "Berlin"})
            assert "18.0°C" in result
            print(f"    ✓ RestToolExecutor.execute('get_weather', Berlin) → OK")

    except httpx.ConnectError:
        print("    ⚠ REST-Server nicht erreichbar! Starte: python provider/rest_server.py")
        return False

    return True


async def test_mcp_integration():
    """Test 3: MCP-Integrationsschicht."""
    print("\n[3] MCP-Integrationsschicht testen...")
    from integration_mcp.mcp_client import McpToolExecutor

    executor = McpToolExecutor("integration_mcp/config.json")

    # tools/list
    tools = await executor.get_available_tools()
    assert len(tools) >= 1
    tool_names = [t["function"]["name"] for t in tools]
    assert "get_weather" in tool_names
    print(f"    ✓ tools/list → {tool_names}")

    # Schema vorhanden
    weather_tool = [t for t in tools if t["function"]["name"] == "get_weather"][0]
    assert "location" in weather_tool["function"]["parameters"]["properties"]
    print(f"    ✓ Input-Schema automatisch: {list(weather_tool['function']['parameters']['properties'].keys())}")

    # call_tool
    result = await executor.execute("get_weather", {"location": "München"})
    result_data = json.loads(result)
    assert result_data["location"] == "München"
    assert result_data["temp"] == 20.3
    print(f"    ✓ call_tool('get_weather', München) → {result_data['temp']}°C")

    return True


async def test_functional_equivalence():
    """Test 4: Funktionale Äquivalenz – beide liefern identische Daten."""
    print("\n[4] Funktionale Äquivalenz prüfen...")
    import httpx

    try:
        # REST-Daten
        async with httpx.AsyncClient() as client:
            r = await client.get(
                "http://127.0.0.1:8000/api/v1/weather",
                params={"location": "Stuttgart"},
            )
            rest_data = r.json()

        # MCP-Daten
        from integration_mcp.mcp_client import McpToolExecutor
        mcp_executor = McpToolExecutor("integration_mcp/config.json")
        mcp_result = await mcp_executor.execute("get_weather", {"location": "Stuttgart"})
        mcp_data = json.loads(mcp_result)

        # Vergleich (ohne Timestamp, da der je nach Aufrufzeitpunkt variiert)
        assert rest_data["location"] == mcp_data["location"]
        assert rest_data["temp"] == mcp_data["temp"]
        assert rest_data["wind_speed"] == mcp_data["wind_speed"]
        assert rest_data["condition"] == mcp_data["condition"]
        print(f"    ✓ REST: {rest_data['temp']}°C  ==  MCP: {mcp_data['temp']}°C")
        print(f"    ✓ REST: {rest_data['condition']}  ==  MCP: {mcp_data['condition']}")
        print("    ✓ Funktionale Äquivalenz bestätigt!")

    except httpx.ConnectError:
        print("    ⚠ REST-Server nicht erreichbar!")
        return False

    return True


async def main():
    print("=" * 60)
    print("PROTOTYP INTEGRATIONSTEST")
    print("=" * 60)

    await test_provider()
    rest_ok = await test_rest_integration()
    mcp_ok = await test_mcp_integration()

    if rest_ok and mcp_ok:
        await test_functional_equivalence()

    print("\n" + "=" * 60)
    print("ALLE TESTS ABGESCHLOSSEN")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
