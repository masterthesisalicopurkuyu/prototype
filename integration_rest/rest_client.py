"""
REST-Integrationsschicht: HTTP-Client für REST-API-Aufrufe.

Diese Datei ist der ZWEITE Kopplungspunkt der REST-Integration.
Sie kapselt die HTTP-Kommunikation mit dem REST-Provider.

KOPPLUNGSPUNKTE IN DIESER DATEI:
    ★ Base-URL (aus config.json geladen)
    ★ Endpoint-Pfade (aus config.json geladen, z.B. '/api/v1/weather')
    ★ HTTP-Methode (GET, hardcoded)
    ★ Query-Parameter-Übergabe (location als params)

Bei Provider-Änderungen (insbesondere Szenario C: Versionierung und
Szenario D: Refactoring) müssen URL-Pfade, Base-URLs und ggf. die
Routing-Logik angepasst werden.

VERGLEICH ZU MCP:
    Bei MCP existiert diese Datei NICHT. Der MCP-Client ruft Tools über
    session.call_tool(tool_name, arguments) auf – ohne HTTP-URLs, ohne
    Endpoint-Pfade, ohne HTTP-Methoden. Das MCP-Protokoll abstrahiert
    den Transport vollständig (Q3: MCP Specification, 2024; Q9: JSON-RPC
    2.0 als Transportprotokoll).
"""

import json
import httpx


class RestToolExecutor:
    """Tool-Executor für die REST-Integrationsschicht.

    Implementiert das ToolExecutor-Interface (agent.py) und übersetzt
    LLM-Tool-Calls in HTTP-Requests an den REST-Provider.
    """

    def __init__(self, config_path: str):
        """REST-Client initialisieren.

        Args:
            config_path: Pfad zur config.json mit Base-URL und Endpoints.
        """
        with open(config_path, "r") as f:
            self.config = json.load(f)

        self.base_url = self.config["base_url"]
        self.endpoints = self.config["endpoints"]

    async def get_available_tools(self) -> list[dict]:
        """Tool-Definitionen zurückgeben.

        Bei REST werden die Definitionen STATISCH aus tool_definitions.py
        geladen. Sie müssen bei jeder Provider-Änderung MANUELL
        aktualisiert werden.

        Vergleich MCP: tools/list liefert Definitionen DYNAMISCH.
        """
        from integration_rest.tool_definitions import TOOL_DEFINITIONS

        return TOOL_DEFINITIONS

    async def execute(self, tool_name: str, arguments: dict) -> str:
        """Tool-Call als HTTP-Request ausführen.

        Args:
            tool_name: Name des Tools (z.B. 'get_weather').
            arguments: Dict mit Parametern (z.B. {'location': 'Stuttgart'}).

        Returns:
            Formatierte Antwort als String (via response_mapper).

        Kopplungskette:
            LLM → tool_name → endpoints[tool_name] → HTTP GET → JSON →
            response_mapper → formatierter String
        """
        from integration_rest.response_mapper import map_response

        endpoint = self.endpoints.get(tool_name)
        if endpoint is None:
            return f"Error: Unknown tool '{tool_name}'"

        url = f"{self.base_url}{endpoint}"

        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=arguments)

            if response.status_code != 200:
                return f"Error: HTTP {response.status_code} - {response.text}"

            raw_data = response.json()
            return map_response(tool_name, raw_data)
