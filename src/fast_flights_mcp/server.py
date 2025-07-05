"""MCP server exposing fast-flights search functions."""

import logging

from fastmcp import FastMCP
from fastmcp.contrib.bulk_tool_caller import BulkToolCaller

from .flights import find_flights as find_flights_impl

logger = logging.getLogger(__name__)

mcp = FastMCP("fast-flights-mcp", dependencies=["fast-flights"])

# Register bulk tool calling utilities
_bulk_tools = BulkToolCaller()
_bulk_tools.register_tools(mcp)


@mcp.tool()
def search_flights(
    from_airport: str,
    to_airport: str,
    date: str,
    *,
    trip: str = "one-way",
    return_date: str | None = None,
    seat: str = "economy",
    adults: int = 1,
    children: int = 0,
    max_stops: int | None = None,
) -> str:
    """Search for flights using :mod:`fast_flights`."""
    # Map max_stops to the expected range (0 or 1)
    if max_stops is None:
        max_stops = 1

    result = find_flights_impl(
        from_airport=from_airport,
        to_airport=to_airport,
        from_date=date,  # Map 'date' parameter to 'from_date'
        trip=trip,
        return_date=return_date,
        seat=seat,
        adults=adults,
        children=children,
        max_stops=max_stops,
    )

    if not result or not result.flights:
        return "No flights found."

    return str(result)


def main() -> None:
    """Run the MCP server."""
    logging.basicConfig(level=logging.INFO)
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
