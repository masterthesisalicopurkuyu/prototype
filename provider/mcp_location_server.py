"""
MCP-Provider: LocationService – Szenario D (strukturelles Refactoring).

Registriert nur get_locations als Tool; Wetter-Tools liegen auf mcp_server.py.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp.server.fastmcp import FastMCP
from provider.weather_service import get_locations

mcp = FastMCP(
    name="Location MCP",
    instructions="List available weather locations.",
)


@mcp.tool(
    name="get_locations",
    description="List all available weather locations.",
)
def get_locations_tool() -> str:
    return get_locations().model_dump_json()


if __name__ == "__main__":
    mcp.run()
