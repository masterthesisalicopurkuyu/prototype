
import os
from groq import Groq


class LLMClient:
    """Minimaler Client für Function Calling über die Groq API.
Kapselt die Kommunikation mit dem Sprachmodell und stellt dem Agenten
eine einheitliche chat()-Schnittstelle bereit.
    """

    def __init__(self, model: str = "llama-3.3-70b-versatile"):
        """LLM-Client initialisieren.

        Args:
            model: Groq-Modellname. Default: llama-3.3-70b-versatile
                   (70B-Parameter-Modell mit zuverlässigem Function Calling).

        Voraussetzung:
            Umgebungsvariable GROQ_API_KEY muss gesetzt sein.
            API-Key unter: https://console.groq.com/
        """
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            raise ValueError(
                "GROQ_API_KEY Umgebungsvariable nicht gesetzt. "
                "Bitte setzen: set GROQ_API_KEY=<dein-key>"
            )
        self.client = Groq(api_key=api_key)
        self.model = model

    def chat(
        self,
        messages: list[dict],
        tools: list[dict] | None = None,
    ) -> dict:
        """Chat-Completion mit optionalem Function Calling.

        Args:
            messages: Liste von Chat-Nachrichten im OpenAI-Format.
            tools: Optionale Liste von Tool-Definitionen (JSON-Schemas).
                   Bei REST: manuell definiert (tool_definitions.py).
                   Bei MCP: dynamisch via tools/list abgerufen.

        Returns:
            Dict mit 'content' (Text) und/oder 'tool_calls' (Function Calls).

        """
        kwargs = {
            "model": self.model,
            "messages": messages,
            "temperature": 0,  # Determinismus für Reproduzierbarkeit
        }
        if tools:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = "auto"

        response = self.client.chat.completions.create(**kwargs)
        choice = response.choices[0].message

        return {
            "content": choice.content,
            "tool_calls": [
                {
                    "name": tc.function.name,
                    "arguments": tc.function.arguments,
                }
                for tc in (choice.tool_calls or [])
            ],
        }
