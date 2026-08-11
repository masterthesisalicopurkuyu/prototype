# Prototyp – Weather Agent (REST vs. MCP)

## Zweck

Dieser Prototyp ist die **Instantiation des Bewertungsrahmens** (DSR-Aktivität 4: Demonstrate Artefact, Johannesson & Perjons, 2014, Kap. 8). Er dient ausschließlich der Demonstration und Evaluation des Bewertungsrahmens – nicht der Entwicklung eines produktiven Systems.

## Voraussetzungen

- Python 3.11+ (getestet mit 3.13.4)
- Groq API Key (siehe https://console.groq.com/)

## Setup

```bash
# Virtual Environment erstellen & aktivieren
python -m venv .venv
.venv\Scripts\activate      # Windows
source .venv/bin/activate   # Linux/Mac

# Dependencies installieren
pip install -r requirements.txt

# Groq API Key setzen
set GROQ_API_KEY=<dein-key>         # Windows CMD
$env:GROQ_API_KEY="<dein-key>"      # Windows PowerShell
export GROQ_API_KEY=<dein-key>      # Linux/Mac
```

## Verwendung

### REST-Variante
```bash
# Terminal 1: REST-Server starten
python provider/rest_server.py

# Terminal 2: Agent starten
python main_rest.py
```

### MCP-Variante
```bash
# MCP-Server startet automatisch (stdio-Transport)
python main_mcp.py
```

### Integrationstest (ohne LLM)
```bash
# REST-Server muss laufen!
python provider/rest_server.py  # Terminal 1
python test_integration.py      # Terminal 2
```

## Architektur

```
Provider (weather_service.py) ← IDENTISCH für beide Varianten
    ↓
Integration REST (4 Dateien)  │  Integration MCP (2 Dateien)
    ↓                         │      ↓
Agent (agent.py)              ← IDENTISCH für beide Varianten
    ↓
LLM (Groq API, temperature=0)
```

## Dateistruktur

| Schicht | Datei | Variante | Rolle |
|---|---|---|---|
| Provider | `weather_service.py` | Geteilt | Geschäftslogik |
| Provider | `models.py` | Geteilt | Pydantic-Datenmodelle |
| Provider | `data.py` | Geteilt | Statische Wetterdaten |
| Provider | `rest_server.py` | REST | FastAPI-Server |
| Provider | `mcp_server.py` | MCP | MCP-Server (FastMCP) |
| Agent | `agent.py` | Geteilt | Function-Calling-Agent |
| Agent | `llm_client.py` | Geteilt | Groq API Wrapper |
| Integration | `tool_definitions.py` | REST ★ | Manuelle Schemas |
| Integration | `rest_client.py` | REST ★ | HTTP-Client |
| Integration | `response_mapper.py` | REST ★ | Response-Mapping |
| Integration | `config.json` | REST ★ | URLs, Endpoints |
| Integration | `mcp_client.py` | MCP | MCP-Session |
| Integration | `config.json` | MCP | Server-Params |

★ = Dateien mit Kopplungspunkten, die bei Provider-Änderungen angepasst werden müssen

## Verwendete Versionen

- Python 3.13.4
- FastAPI 0.136.0
- Uvicorn 0.44.0
- Pydantic 2.13.2
- MCP Python SDK 1.27.0
- Groq 1.2.0
- HTTPX 0.28.1

## Reproduktionsstände

Der gemeinsame Ausgangszustand und die vier unabhängig davon
implementierten Evolutionsszenarien sind durch Git-Tags gekennzeichnet:

- `v1-baseline`: gemeinsamer Ausgangszustand
- `v2-scenario-a`: Capability-Erweiterung
- `v2-scenario-b`: Breaking Change
- `v2-scenario-c`: Versionierung und Deprecation
- `v2-scenario-d`: strukturelles Refactoring

Die Szenarien wurden jeweils unabhängig vom Tag `v1-baseline`
implementiert.

## Messgrenze

Die Messung beschränkt sich auf die Integrationsschichten
`integration_rest/` und `integration_mcp/`. Provider, Agentenlogik,
Tests, Prompt-Anpassungen und organisatorischer Aufwand liegen
außerhalb der Messgrenze.

## Ergebnisse

| Szenario | REST CPS | REST IE | REST CC | MCP CPS | MCP IE | MCP CC |
|---|---:|---:|---:|---:|---:|---:|
| A | 2 | 6 | 5 | 0 | 4 | 0 |
| B | 2 | 6 | 5 | 0 | 4 | 0 |
| C | 1 | 7 | 2 | 0 | 4 | 0 |
| D | 2 | 8 | 31 | 2 | 6 | 74 |

Die Werte entsprechen dem in der Masterarbeit dokumentierten
Messprotokoll. Code Churn umfasst hinzugefügte und gelöschte relevante
Zeilen nach Anwendung der festgelegten Filterregeln.
