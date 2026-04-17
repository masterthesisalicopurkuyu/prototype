"""
Agent-Kern: Minimaler Function-Calling-Agent.

Dieser Agent ist in BEIDEN Varianten (REST und MCP) IDENTISCH. Er ist
die Kontrollbedingung des Experiments – wenn sich der Agent zwischen den
Varianten unterscheiden würde, wären Unterschiede in M1–M3 nicht mehr
eindeutig auf den Integrationsmechanismus zurückführbar (Wohlin et al.,
2012, Kap. 3 [Q7]).

Der Agent implementiert das grundlegende Tool-Learning-Framework nach
Qin et al. (2024) [Q5]:
    1. Understand: User-Prompt empfangen
    2. Select: LLM wählt passendes Tool basierend auf Tool-Definitionen
    3. Execute: Agent führt den Tool-Call über den ToolExecutor aus

Schick et al. (2023) [Q4] zeigen mit Toolformer, dass LLMs autonom
entscheiden können, welche APIs aufgerufen werden. Function Calling
(OpenAI, 2023 [Q10]) formalisiert dieses Muster: Das LLM erhält
strukturierte Tool-Beschreibungen und gibt strukturierte Aufrufe zurück.

BEWUSST EINFACH gehalten (~60 LOC):
- Kein mehrstufiges Reasoning
- Keine Planungsfähigkeit
- Keine Schleifen oder Retry-Logik
- Kein Agent-Framework (LangChain, AutoGen)

Begründung: Ein komplexer Agent würde das LLM-Verhalten als Störvariable
einführen (Wohlin et al., 2012 [Q7]). Die Metriken (M1–M3) messen den
ENTWICKLER-Aufwand zur Anpassung des Integrationscodes, nicht die
Qualität der LLM-Antworten oder die Agent-Architektur.
"""

import json
from abc import ABC, abstractmethod
from agent.llm_client import LLMClient


class ToolExecutor(ABC):
    """Abstrakte Schnittstelle für Tool-Ausführung.

    Beide Integrationsschichten (REST und MCP) implementieren dieses
    Interface. Dadurch kann der Agent-Kern UNABHÄNGIG vom konkreten
    Integrationsmechanismus arbeiten.

    Methoden:
        get_available_tools(): Liefert Tool-Definitionen für das LLM.
            - REST: Gibt manuell definierte Schemas zurück (tool_definitions.py)
            - MCP: Ruft tools/list ab und konvertiert in Function-Calling-Format

        execute(tool_name, arguments): Führt einen Tool-Call aus.
            - REST: HTTP-Call + Response-Mapping
            - MCP: MCP call_tool
    """

    @abstractmethod
    async def get_available_tools(self) -> list[dict]:
        """Verfügbare Tools als Function-Calling-Schemas zurückgeben."""
        ...

    @abstractmethod
    async def execute(self, tool_name: str, arguments: dict) -> str:
        """Tool-Call ausführen und Ergebnis als String zurückgeben."""
        ...


class WeatherAgent:
    """Minimaler Function-Calling-Agent für den Weather Service.

    Interaktionsablauf (identisch für beide Varianten):
        1. User-Prompt empfangen
        2. Verfügbare Tools vom ToolExecutor abrufen
        3. Prompt + Tools an LLM senden
        4. LLM wählt Tool + Parameter (oder antwortet direkt)
        5. Bei Tool-Call: Tool über ToolExecutor ausführen
        6. Ergebnis an LLM senden für finale Antwort
        7. Formatierte Antwort zurückgeben
    """

    def __init__(self, llm_client: LLMClient, tool_executor: ToolExecutor):
        """Agent initialisieren.

        Args:
            llm_client: LLM-Client für Chat-Completions.
            tool_executor: Integrationsschicht (REST oder MCP).
                           Der Agent weiß NICHT, welche Variante er nutzt.
        """
        self.llm = llm_client
        self.tools = tool_executor

    async def handle(self, user_message: str) -> str:
        """Benutzeranfrage verarbeiten.

        Args:
            user_message: Freitext-Anfrage des Benutzers.

        Returns:
            Formatierte Antwort als String.
        """
        # Schritt 1: Verfügbare Tools abrufen
        available_tools = await self.tools.get_available_tools()

        # Schritt 2: User-Prompt + Tools an LLM senden
        messages = [{"role": "user", "content": user_message}]
        response = self.llm.chat(messages=messages, tools=available_tools)

        # Schritt 3: Prüfen ob LLM einen Tool-Call zurückgibt
        if response["tool_calls"]:
            tool_call = response["tool_calls"][0]
            tool_name = tool_call["name"]
            tool_args = json.loads(tool_call["arguments"])

            # Schritt 4: Tool über den ToolExecutor ausführen
            tool_result = await self.tools.execute(tool_name, tool_args)

            # Schritt 5: Ergebnis an LLM für finale Antwort senden
            messages.append({
                "role": "assistant",
                "content": None,
                "tool_calls": [
                    {
                        "id": "call_1",
                        "type": "function",
                        "function": {
                            "name": tool_name,
                            "arguments": tool_call["arguments"],
                        },
                    }
                ],
            })
            messages.append({
                "role": "tool",
                "tool_call_id": "call_1",
                "content": tool_result,
            })

            final_response = self.llm.chat(messages=messages)
            return final_response["content"]

        # Kein Tool-Call → direkte Textantwort
        return response["content"]
