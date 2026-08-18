# ORION Model Context Protocol (MCP) Server

Production-quality MCP server exposing ORION's deterministic analytics, autonomous multi-agent investigation pipeline, human approval governance, and safe simulation execution.

## Structure

```
orion_mcp/
├── __init__.py
├── server.py             # FastMCP server initialization, tool & resource definitions
├── demo.py               # Complete standalone client verification demo
└── tools/
    ├── __init__.py       # Re-exports all 18 tools & safety classifications
    ├── read_only.py      # 9 Read-only analytics & evidence query tools
    ├── investigation.py  # 3 Multi-agent investigation & business impact tools
    ├── governance.py     # 4 Human recommendation & approval tools
    ├── action.py         # 1 Controlled safe simulation action tool
    └── audit.py          # 1 Immutable operations audit log tool
```

## Running the Server

### Standard Local Execution (stdio transport)
```bash
python -m orion_mcp.server
```
or
```bash
python mcp/run.py
```

### Running the Live Client Demo Scenario
```bash
python -m orion_mcp.demo
```

## Tool Documentation & Architecture

- Tool Specifications & Safety Matrix: [`docs/MCP_TOOLS.md`](../docs/MCP_TOOLS.md)
- External Runtime & Adya Integration Guide: [`docs/ADYA_INTEGRATION.md`](../docs/ADYA_INTEGRATION.md)
