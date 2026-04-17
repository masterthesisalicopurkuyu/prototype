"""
LLM-Client: Wrapper für die Groq API mit Function-Calling-Support.

Die Wahl von Groq als LLM-Provider ist eine pragmatische Entscheidung, die
die Methodik nicht beeinflusst:

1. Function Calling ist LLM-agnostisch (Qin et al., 2024 [Q5]): Das
   Tool-Learning-Framework (understand → select → execute) ist unabhängig
   vom konkreten LLM-Provider. Groq nutzt dasselbe OpenAI-kompatible
   Function-Calling-Format wie GPT-4, Gemini und andere Modelle.

2. Kostenfreiheit: Der kostenlose Groq-API-Tier ermöglicht die Durchführung
   des Experiments ohne finanzielle Barrieren. Der ursprünglich geplante
   Google Gemini Free Tier ist in der EU/Deutschland nicht verfügbar
   (regulatorische Einschränkung), weshalb Groq als EU-verfügbare
   Alternative gewählt wurde.

3. Determinismus: temperature=0 wird für maximale Reproduzierbarkeit
   gesetzt (vgl. Wohlin et al., 2012, Kap. 5 [Q7]: Kontrolle von
   Störvariablen). Bei temperature=0 wählt das Modell die
   wahrscheinlichste Antwort, was stochastische Varianz minimiert.

4. Konfundierungskontrolle: Das LLM wird in BEIDEN Varianten (REST und
   MCP) identisch eingesetzt – gleiches Modell, gleiche Parameter. Eine
   Variable, die in beiden Treatments identisch ist, kann keine
   systematische Differenz verursachen (Wohlin et al., 2012, Kap. 3 [Q7]).

Quelle für Groq Function Calling:
    Groq (2025). Tool Use with Groq API.
    https://console.groq.com/docs/tool-use
"""

import os
from groq import Groq


class LLMClient:
    """Minimaler LLM-Client für Function Calling.

    Kapselt die Groq-API-Kommunikation und stellt eine einheitliche
    Schnittstelle bereit, die vom Agent-Kern (agent.py) genutzt wird.
    Der Agent-Kern kennt NICHT den konkreten LLM-Provider – er nutzt
    nur die chat()-Methode mit Tools.

    Diese Abstraktion folgt dem Dependency-Inversion-Prinzip (Bass et al.,
    2021 [Q8]): Der Agent hängt von einer Abstraktion ab, nicht von
    einer konkreten LLM-Implementierung.
    """

    def __init__(self, model: str = "llama-3.3-70b-versatile"):
        """LLM-Client initialisieren.

        Args:
            model: Groq-Modellname. Default: llama-3.3-70b-versatile
                   (70B-Parameter-Modell mit zuverlässigem Function Calling).

        Voraussetzung:
            Umgebungsvariable GROQ_API_KEY muss gesetzt sein.
            API-Key kostenlos erhältlich unter: https://console.groq.com/
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

        Function Calling (vgl. OpenAI, 2023 [Q10]; Qin et al., 2024 [Q5]):
            Wenn Tools übergeben werden, kann das LLM entscheiden, eine
            Funktion aufzurufen, anstatt eine Text-Antwort zu generieren.
            Die Entscheidung basiert auf dem User-Prompt und den
            Tool-Beschreibungen (Name, Description, Parameter-Schema).
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
