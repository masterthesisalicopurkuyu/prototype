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

        self.server_params = StdioServerParameters(
            command=self.config["server"]["command"],
            args=self.config["server"]["args"],
        )

    async def get_available_tools(self) -> list[dict]:
        """Ruft die verfügbaren Werkzeuge über MCP tools/list ab.
Die zurückgegebenen Werkzeugdefinitionen werden in das vom LLM-Client
erwartete Function-Calling-Format konvertiert.
        """
        async with stdio_client(self.server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()

                # tools/list: Dynamische Capability-Discovery
                tools_result = await session.list_tools()

                # Konvertierung MCP-Tool-Format → Function-Calling-Format
                tool_definitions = []
                for tool in tools_result.tools:
                    tool_def = {
                        "type": "function",
                        "function": {
                            "name": tool.name,
                            "description": tool.description or "",
                            "parameters": tool.inputSchema,
                        },
                    }
                    tool_definitions.append(tool_def)

                return tool_definitions

    async def execute(self, tool_name: str, arguments: dict) -> str:
        """Tool-Call via MCP call_tool ausführen.

        Args:
            tool_name: Tool-Name (vom LLM aus tools/list ausgewählt).
            arguments: Dict mit Parametern.

        Returns:
            Tool-Response als String (TextContent vom MCP-Server).
        """
        async with stdio_client(self.server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()

                result = await session.call_tool(tool_name, arguments)

                # MCP liefert Content-Objekte (TextContent, ImageContent, etc.)
                # Für den Weather Service: TextContent mit JSON-String
                if result.content:
                    return result.content[0].text

                return "No result returned from MCP server."
