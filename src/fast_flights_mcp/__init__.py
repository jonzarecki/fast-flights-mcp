"""Fast Flights MCP server."""

from .server import _bulk_tools, main, mcp, search_flights

__all__ = [
    "main",
    "mcp",
    "search_flights",
    "call_tool_bulk",
    "call_tools_bulk",
]

call_tool_bulk = _bulk_tools.call_tool_bulk
call_tools_bulk = _bulk_tools.call_tools_bulk
