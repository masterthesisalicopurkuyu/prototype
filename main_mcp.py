"""
Startpunkt der MCP-Variante des Weather Agent.

Der MCP-Server wird automatisch über den stdio-Transport gestartet.
Voraussetzung ist die Umgebungsvariable GROQ_API_KEY.
"""

import sys
import os
import asyncio

# Projektroot zum Python-Path hinzufügen
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent.llm_client import LLMClient
from agent.agent import WeatherAgent
from integration_mcp.mcp_client import McpToolExecutor


async def main():
    """MCP-Variante des Weather Agent ausführen."""
    print("=" * 60)
    print("Weather Agent – MCP-Variante")
    print("=" * 60)

    # Komponenten initialisieren
    llm_client = LLMClient()
    tool_executor = McpToolExecutor(
        config_path=os.path.join("integration_mcp", "config.json")
    )
    agent = WeatherAgent(llm_client=llm_client, tool_executor=tool_executor)

    # Interaktive Schleife
    print("\nAgent bereit. Stelle eine Frage zum Wetter.")
    print("(Eingabe 'exit' zum Beenden)\n")

    while True:
        user_input = input("Du: ").strip()
        if user_input.lower() in ("exit", "quit", "q"):
            break
        if not user_input:
            continue

        try:
            response = await agent.handle(user_input)
            print(f"\nAgent: {response}\n")
        except Exception as e:
            print(f"\nFehler: {e}\n")


if __name__ == "__main__":
    asyncio.run(main())
