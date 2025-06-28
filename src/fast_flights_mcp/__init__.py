"""Fast Flights MCP server."""

from .server import (
    main,
    mcp,
    search_airports,
    search_flights,
    seat_classes,
    plan_trip,
    compare_airports,
)

__all__ = [
    "main",
    "mcp",
    "search_airports",
    "search_flights",
    "seat_classes",
    "plan_trip",
    "compare_airports",
]
