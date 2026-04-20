"""
REST-Integrationsschicht: Manuell definierte Function-Calling-Schemas.

Diese Datei ist der ERSTE von vier Kopplungspunkten der REST-Integration.
Sie enthält die Tool-Definitionen, die dem LLM mitteilen, welche Funktionen
verfügbar sind und welche Parameter sie erwarten.

WARUM diese Datei bei REST existiert, aber bei MCP NICHT:
    Bei REST existiert kein Protokoll, das diese Beschreibungen automatisch
    zur Laufzeit liefert. Die OpenAPI-Spezifikation (Q2: OpenAPI Initiative,
    2021) beschreibt die API maschinenlesbar, wird aber nicht dynamisch vom
    Client abgefragt, um Function-Calling-Schemas zu generieren. Der
    Entwickler muss die Schemas MANUELL schreiben.

    Bei MCP liefert tools/list (Q3: MCP Specification, 2024) die
    Tool-Definitionen inklusive Input-Schema dynamisch. Der MCP-Client
    konvertiert diese automatisch in das Function-Calling-Format.

    Dieser Unterschied ist PARADIGMENBEDINGT, nicht designbedingt.
    Peter Sun et al. (2022) [Q12] argumentieren, dass solche
    integrationsspezifischen Kopplungspunkte von generischen Metriken
    wie CBO nicht erfasst werden.

KOPPLUNGSPUNKTE IN DIESER DATEI:
    ★ Tool-Name ('get_weather') → muss mit REST-Endpoint-Mapping übereinstimmen
    ★ Parameter-Name ('location') → muss mit Query-Parameter übereinstimmen
    ★ Beschreibungstext → muss API-Funktion korrekt beschreiben
    → Bei Provider-Änderungen (Szenarien A-D) muss diese Datei angepasst werden
"""

# Tool-Definitionen im OpenAI-kompatiblen Function-Calling-Format
# (vgl. OpenAI, 2023 [Q10]: "You can describe functions to the model")
# Dieses Format wird auch von Groq und anderen LLM-Providern unterstützt,
# da Function Calling ein LLM-agnostisches Konzept ist (Qin et al., 2024 [Q5]).
TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get current weather data for a specific city. "
            "Returns temperature, wind speed, weather condition, and humidity.",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "City name, e.g. 'Stuttgart', 'Berlin', 'München'",
                    }
                },
                "required": ["location"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_locations",
            "description": "List all available weather locations.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": [],
            },
        },
    },
]
