"""Baseline-Metrik-Erhebung (V1) – bereinigte Version."""
import os
import json
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 60)
print("BASELINE-METRIK-ERHEBUNG (V1)")
print("=" * 60)

# ============================================================
# BL1: Dep_Out – Manuelle Zaehlung der REALEN Kopplungspunkte
# (nicht automatisch, da AST-basierte Zaehlung Docstrings mitzaehlt)
# ============================================================
print("\n--- BL1: Dep_Out (Ausgehende Abhaengigkeiten) ---")
print("\nREST-Integration – reale Kopplungspunkte:")
rest_coupling = [
    ("config.json",          "base_url = http://127.0.0.1:8000",    "Konfiguration"),
    ("config.json",          "endpoints.get_weather = /api/v1/weather", "Konfiguration"),
    ("config.json",          "endpoints.get_locations = /api/v1/locations", "Konfiguration"),
    ("tool_definitions.py",  "name: 'get_weather'",                 "String-Literal"),
    ("tool_definitions.py",  "parameter: 'location'",               "Schema"),
    ("tool_definitions.py",  "name: 'get_locations'",               "String-Literal"),
    ("rest_client.py",       "HTTP-Methode: GET (hardcoded)",       "Hardcoded"),
    ("response_mapper.py",   "Feldname: 'location'",                "String-Literal"),
    ("response_mapper.py",   "Feldname: 'temp'",                    "String-Literal"),
    ("response_mapper.py",   "Feldname: 'wind_speed'",              "String-Literal"),
    ("response_mapper.py",   "Feldname: 'condition'",               "String-Literal"),
]
for datei, punkt, typ in rest_coupling:
    print(f"  [{typ:15s}] {datei:25s} -> {punkt}")
print(f"  --> Dep_Out(REST) = {len(rest_coupling)}")

print("\nMCP-Integration – reale Kopplungspunkte:")
mcp_coupling = [
    ("config.json",   "server.command = .venv/Scripts/python",  "Konfiguration"),
    ("config.json",   "server.args = provider/mcp_server.py",   "Konfiguration"),
]
for datei, punkt, typ in mcp_coupling:
    print(f"  [{typ:15s}] {datei:25s} -> {punkt}")
print(f"  --> Dep_Out(MCP) = {len(mcp_coupling)}")

# ============================================================
# BL2: Dep_In
# ============================================================
print("\n--- BL2: Dep_In (Eingehende Abhaengigkeiten) ---")
print("  Dep_In(REST) = 1 (nur main_rest.py)")
print("  Dep_In(MCP)  = 1 (nur main_mcp.py)")

# ============================================================
# BL3: H
# ============================================================
print("\n--- BL3: H (Relationale Kohaesion) ---")
# REST: rest_client importiert tool_definitions + response_mapper
rest_modules = 4
rest_internal = 2
h_rest = rest_internal / (rest_modules - 1)
print(f"  REST: {rest_internal} interne Imports / ({rest_modules}-1) Module = H = {h_rest:.2f}")

# MCP: mcp_client hat keine internen Python-Imports
mcp_modules = 2
mcp_internal = 0
h_mcp = mcp_internal / (mcp_modules - 1)
print(f"  MCP:  {mcp_internal} interne Imports / ({mcp_modules}-1) Module = H = {h_mcp:.2f}")

# ============================================================
# BI
# ============================================================
print("\n--- BI (Baseline Index = Dep_Out + 1/H) ---")
bi_rest = len(rest_coupling) + (1 / h_rest)
print(f"  BI(REST) = {len(rest_coupling)} + {1/h_rest:.2f} = {bi_rest:.2f}")
print(f"  BI(MCP)  = {len(mcp_coupling)} + 1/0 = n/a (H=0, Division undefiniert)")
print("  -> BI dient als erklaerende Kontextmetrik (nicht im WES)")

# ============================================================
# LOC
# ============================================================
print("\n--- LOC (ohne __init__.py, Kommentare, Leerzeilen) ---")
for name, d in [("integration_rest", "integration_rest"), ("integration_mcp", "integration_mcp")]:
    total = 0
    for root, dirs, files in os.walk(d):
        for fname in files:
            if fname == "__init__.py":
                continue
            fpath = os.path.join(root, fname)
            try:
                with open(fpath, "r", encoding="utf-8", errors="replace") as f:
                    lines = [l for l in f.readlines()
                             if l.strip()
                             and not l.strip().startswith("#")
                             and not l.strip().startswith('"""')
                             and not l.strip().startswith("'''")]
                total += len(lines)
            except Exception:
                pass
    print(f"  LOC({name}) = {total}")

# ============================================================
# Dateienanzahl
# ============================================================
print("\n--- Dateienanzahl (ohne __init__.py) ---")
for name, d in [("integration_rest", "integration_rest"), ("integration_mcp", "integration_mcp")]:
    count = sum(1 for _, _, files in os.walk(d) for f in files if f != "__init__.py")
    print(f"  Dateien({name}) = {count}")

# ============================================================
# Zusammenfassung
# ============================================================
print("\n" + "=" * 60)
print("ZUSAMMENFASSUNG V1 BASELINE")
print("=" * 60)
print(f"""
  Metrik          | REST  | MCP   | Differenz
  ----------------+-------+-------+----------
  Dep_Out (BL1)   | {len(rest_coupling):5d} | {len(mcp_coupling):5d} | {len(rest_coupling)-len(mcp_coupling):+d}
  Dep_In  (BL2)   |     1 |     1 |  0
  H       (BL3)   |  {h_rest:.2f} |  {h_mcp:.2f} | {h_rest-h_mcp:+.2f}
  Dateien         |     4 |     2 | -2
""")
print("=" * 60)
