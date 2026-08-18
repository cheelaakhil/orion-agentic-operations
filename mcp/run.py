"""
ORION MCP Runner Script

Runs the ORION Model Context Protocol server.
"""

from orion_mcp.server import mcp

if __name__ == "__main__":
    mcp.run()
