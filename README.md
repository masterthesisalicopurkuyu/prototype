# Prototyp – Weather Agent (REST vs. MCP)

## Zweck

Dieser Prototyp ist die **Instantiation des Bewertungsrahmens** (DSR-Aktivität 4: Demonstrate Artefact, Johannesson & Perjons, 2014, Kap. 8). Er dient ausschließlich der Demonstration und Evaluation des Bewertungsrahmens – nicht der Entwicklung eines produktiven Systems.

## Voraussetzungen

- Python 3.11+ (getestet mit 3.13.4)
- Groq API Key (kostenlos: https://console.groq.com/)

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
# Szenario D: zwei REST-Dienste (Wetter :8000, Standorte :8001)
# Terminal 1: WeatherDataService
python provider/rest_server.py
# Terminal 2: LocationService
python provider/rest_location_server.py

# Terminal 3: Agent starten
python main_rest.py
```

### MCP-Variante
```bash
# MCP-Server startet automatisch (stdio-Transport)
python main_mcp.py
```

### Integrationstest (ohne LLM)
```bash
# Beide REST-Dienste müssen laufen (Szenario D)
python provider/rest_server.py           # Terminal 1 (Port 8000)
python provider/rest_location_server.py    # Terminal 2 (Port 8001)
python test_integration.py                 # Terminal 3
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
| Provider | `rest_server.py` | REST | FastAPI Weather (:8000, Szenario D) |
| Provider | `rest_location_server.py` | REST | FastAPI Locations (:8001, Szenario D) |
| Provider | `mcp_server.py` | MCP | MCP Weather-Server |
| Provider | `mcp_location_server.py` | MCP | MCP Location-Server |
| Agent | `agent.py` | Geteilt | Function-Calling-Agent |
| Agent | `llm_client.py` | Geteilt | Groq API Wrapper |
| Integration | `tool_definitions.py` | REST ★ | Manuelle Schemas |
| Integration | `rest_client.py` | REST ★ | HTTP-Client |
| Integration | `response_mapper.py` | REST ★ | Response-Mapping |
| Integration | `config.json` | REST ★ | URLs, Endpoints |
| Integration | `mcp_client.py` | MCP | MCP-Session |
| Integration | `config.json` | MCP | Server-Params |

★ = Dateien mit Kopplungspunkten, die bei Provider-Änderungen angepasst werden müssen
