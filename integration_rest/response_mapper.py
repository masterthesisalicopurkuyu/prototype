"""
REST-Integrationsschicht: Response-Mapping.

Diese Datei ist der DRITTE Kopplungspunkt der REST-Integration.
Sie transformiert die rohen JSON-Responses des REST-Providers in ein
für den LLM-Agent verwertbares Textformat.

WARUM diese Datei bei REST existiert, aber NICHT bei MCP:

    Bei REST liefert der HTTP-Response ein generisches JSON-Objekt.
    Der Entwickler muss die Feldnamen kennen und manuell referenzieren,
    um die Daten dem LLM-Kontext zugänglich zu machen. Jede
    Feldnamen-Referenz ist ein HARDCODED Kopplungspunkt.

    Bei MCP hingegen liefert call_tool() ein strukturiertes Content-
    Objekt, das das Protokoll selbst definiert (MCP Specification [Q3]:
    'content' field mit TextContent). Der LLM erhält die Tool-Response
    direkt als Text-Content. Ein expliziter Mapper ist daher
    PROTOKOLLBEDINGT nicht erforderlich – nicht weil der Prototyp ihn
    willkürlich weglässt, sondern weil das MCP-Protokoll diese
    Abstraktionsschicht nativ bereitstellt.

    Diese Asymmetrie (4 vs. 2 Dateien) ist eine direkte Konsequenz der
    Paradigmen und wird in Threats to Validity (Kap. 9, Threat 5) als
    potentielle Asymmetrie diskutiert.

KOPPLUNGSPUNKTE IN DIESER DATEI:
    ★ Feldname 'location' (hardcoded)
    ★ Feldname 'temperature_celsius' (hardcoded)
    ★ Feldname 'wind_speed' (hardcoded)
    ★ Feldname 'condition' (hardcoded)
    → Szenario B: Breaking Change temp → temperature_celsius (Struktur).
"""


def map_response(tool_name: str, raw_response: dict) -> str:
    """REST-JSON-Response auf Agent-lesbares Format mappen.

    Args:
        tool_name: Name des aufgerufenen Tools.
        raw_response: Rohe JSON-Response des REST-Providers.

    Returns:
        Formatierter String für den LLM-Kontext.
    """
    if tool_name == "get_weather":
        return map_weather_response(raw_response)
    elif tool_name == "get_locations":
        return map_locations_response(raw_response)
    else:
        return str(raw_response)


def map_weather_response(raw_response: dict) -> str:
    """Wetter-Response formatieren.

    HARDCODED Feldnamen: location, temperature_celsius, wind_speed, condition.
    """
    temp_data = raw_response["temperature_celsius"]
    return (
        f"Weather in {raw_response['location']}: "
        f"{temp_data['value']}{temp_data['unit']}, "
        f"Wind: {raw_response['wind_speed']} km/h, "
        f"Condition: {raw_response['condition']}"
    )


def map_locations_response(raw_response: dict) -> str:
    """Locations-Response formatieren."""
    locations = raw_response.get("locations", [])
    return f"Available locations: {', '.join(locations)}"
