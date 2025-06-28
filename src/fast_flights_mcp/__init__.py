"""Fast Flights MCP server."""

from .server import (
    main,
    mcp,
    search_airports,
    search_flights,
    seat_classes,
    plan_trip,
    compare_airports,
    _bulk_tools,
)

__all__ = [
    "main",
    "mcp",
    "search_airports",
    "search_flights",
    "seat_classes",
    "plan_trip",
    "compare_airports",
    "call_tool_bulk",
    "call_tools_bulk",
]

call_tool_bulk = _bulk_tools.call_tool_bulk
call_tools_bulk = _bulk_tools.call_tools_bulk
