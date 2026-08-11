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
    """
    return (
        f"Weather in {raw_response['location']}: "
        f"{raw_response['temp']}°C, "
        f"Wind: {raw_response['wind_speed']} km/h, "
        f"Condition: {raw_response['condition']}"
    )


def map_locations_response(raw_response: dict) -> str:
    """Locations-Response formatieren."""
    locations = raw_response.get("locations", [])
    return f"Available locations: {', '.join(locations)}"
