"""
Entry Point: REST-Variante des Weather Agent.

Startet den Agent mit der REST-Integrationsschicht:
    Agent → REST-ToolExecutor → HTTP → REST-Provider (FastAPI)

Verwendung:
    1. REST-Server starten: python provider/rest_server.py
    2. Agent starten:        python main_rest.py

Voraussetzung:
    - GROQ_API_KEY Umgebungsvariable gesetzt
    - REST-Server läuft auf http://127.0.0.1:8000
"""

import sys
import os
import asyncio

# Projektroot zum Python-Path hinzufügen
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent.llm_client import LLMClient
from agent.agent import WeatherAgent
from integration_rest.rest_client import RestToolExecutor


async def main():
    """REST-Variante des Weather Agent ausführen."""
    print("=" * 60)
    print("Weather Agent – REST-Variante")
    print("=" * 60)

    # Komponenten initialisieren
    llm_client = LLMClient()
    tool_executor = RestToolExecutor(
        config_path=os.path.join("integration_rest", "config.json")
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
