"""
MCP-Integrationsschicht: MCP-Client mit dynamischer Tool-Discovery.

Diese Datei ist der EINZIGE Code-Kopplungspunkt der MCP-Integration
(neben config.json). Sie kapselt die MCP-Kommunikation und nutzt das
Protokoll für automatische Tool-Discovery und -Ausführung.

ARCHITEKTONISCHER UNTERSCHIED ZU REST (4 Dateien → 2 Dateien):

    1. KEINE tool_definitions.py nötig:
       tools/list (Q3: MCP Specification, 2024) liefert Tool-Definitionen
       inklusive Input-Schema dynamisch. Diese werden automatisch in das
       Function-Calling-Format konvertiert, das der LLM-Client erwartet.
       → Eliminiert den manuellen Kopplungspunkt 'Tool-Schemas'.

    2. KEIN response_mapper.py nötig:
       call_tool() liefert ein strukturiertes Content-Objekt (TextContent
       gemäß MCP Specification). Der LLM erhält die Response direkt als
       Text – kein manuelles Feldnamen-Mapping erforderlich.
       → Eliminiert die hardcodierten Feldnamen als Kopplungspunkte.

    3. KEIN HTTP-Client (rest_client.py) nötig:
       MCP abstrahiert den Transport über JSON-RPC 2.0 (Q9). Der Client
       muss keine URLs, Endpoint-Pfade oder HTTP-Methoden kennen.
       → Eliminiert URL- und Endpoint-Kopplungspunkte.

KOPPLUNGSPUNKTE IN DIESER DATEI:
    ★ Server-Verbindungsparameter (aus config.json)
    ★ Tool-Name 'get_weather_tool' (wird zur Laufzeit entdeckt, aber
      im Agent-Code NICHT hardcoded referenziert – der Agent verwendet
      den Namen, den das LLM aus tools/list auswählt)

VERGLEICH DER KOPPLUNGSPUNKTE:
    REST: ~8 Kopplungspunkte (URLs, Feldnamen, Schemas, HTTP-Methoden)
    MCP:  ~2 Kopplungspunkte (Server-Adresse, Transport-Typ)
    Diese Differenz ist die strukturelle Grundlage für die erwarteten
    Metrik-Unterschiede (Hypothesen H1–H4, Kap. 7.15).
"""

import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class McpToolExecutor:
    """Tool-Executor für die MCP-Integrationsschicht.

    Implementiert das ToolExecutor-Interface (agent.py) und nutzt das
    MCP-Protokoll für dynamische Tool-Discovery und -Ausführung.
    """

    def __init__(self, config_path: str):
        """MCP-Client initialisieren.

        Args:
            config_path: Pfad zur config.json mit Server-Parametern.
        """
        with open(config_path, "r") as f:
            self.config = json.load(f)

        # Szenario D: mehrere MCP-Server (stdio), tools/list pro Server aggregieren
        self.server_params_list = [
            StdioServerParameters(command=srv["command"], args=srv["args"])
            for srv in self.config["servers"]
        ]

    async def get_available_tools(self) -> list[dict]:
        """Tool-Definitionen via MCP tools/list dynamisch abrufen.

        ENTSCHEIDENDER UNTERSCHIED ZU REST:
        Diese Methode ruft tools/list auf dem MCP-Server auf. Der Server
        liefert ALLE registrierten Tools mit Name, Description und
        Input-Schema. Diese werden automatisch in das OpenAI-kompatible
        Function-Calling-Format konvertiert.

        Bei REST (tool_definitions.py) werden die Schemas MANUELL
        definiert und STATISCH geladen. Bei jeder Provider-Änderung
        muss der Entwickler die Schemas manuell aktualisieren.

        Bei MCP reflektiert tools/list AUTOMATISCH den aktuellen
        Server-Zustand. Wenn der Server ein neues Tool registriert
        (Szenario A) oder ein Schema ändert (Szenario B), wird dies
        beim nächsten tools/list-Aufruf sichtbar – OHNE Code-Änderung.
        """
        all_tools = []
        for params in self.server_params_list:
            async with stdio_client(params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    tools_result = await session.list_tools()
                    for tool in tools_result.tools:
                        all_tools.append({
                            "type": "function",
                            "function": {
                                "name": tool.name,
                                "description": tool.description or "",
                                "parameters": tool.inputSchema,
                            },
                        })
        return all_tools

    async def execute(self, tool_name: str, arguments: dict) -> str:
        """Tool-Call via MCP call_tool ausführen.

        Args:
            tool_name: Tool-Name (vom LLM aus tools/list ausgewählt).
            arguments: Dict mit Parametern.

        Returns:
            Tool-Response als String (TextContent vom MCP-Server).

        KEIN Response-Mapping nötig:
        call_tool() liefert ein strukturiertes Content-Objekt. Der
        TextContent wird direkt als String zurückgegeben. Feldnamen
        werden NICHT hardcoded referenziert → kein Kopplungspunkt.
        """
        for params in self.server_params_list:
            async with stdio_client(params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    tools_result = await session.list_tools()
                    if tool_name not in {t.name for t in tools_result.tools}:
                        continue
                    result = await session.call_tool(tool_name, arguments)
                    if result.content:
                        return result.content[0].text
                    return "No result returned from MCP server."

        return f"Error: Tool '{tool_name}' not found on any server."
