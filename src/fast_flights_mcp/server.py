"""MCP server exposing fast-flights search functions."""

import logging
from typing import Optional

from fastmcp import FastMCP
from fastmcp.contrib.bulk_tool_caller import BulkToolCaller
from fast_flights import (
    search_airport,
    get_flights,
    FlightData,
    Passengers,
)

logger = logging.getLogger(__name__)

mcp = FastMCP("fast-flights-mcp", dependencies=["fast-flights"])

# Register bulk tool calling utilities
_bulk_tools = BulkToolCaller()
_bulk_tools.register_tools(mcp)


@mcp.tool()
def search_airports(query: str) -> str:
    """Return a list of airports matching ``query``."""
    query = query.lower()
    matches = [
        a for a in search_airport("")
        if query in a.name.lower() or query in a.value.lower()
    ]
    if not matches:
        return "No airports found"
    lines = [f"{a.name.replace('_', ' ').title()} ({a.value})" for a in matches[:20]]
    if len(matches) > 20:
        lines.append(f"...and {len(matches) - 20} more results")
    return "\n".join(lines)
search_airports_unwrapped = search_airports


@mcp.resource("flights://seat-classes")
def seat_classes() -> str:
    """List the available seat classes."""
    return "\n".join(["economy", "premium_economy", "business", "first"])


@mcp.prompt()
def plan_trip(destination: str) -> str:
    """Prompt text to help plan a trip."""
    return (
        f"Provide travel tips for visiting {destination}. "
        "What is the best time to go and approximate costs?"
    )


@mcp.prompt()
def compare_airports(code1: str, code2: str) -> str:
    """Prompt to compare flights between two airports."""
    return (
        f"Compare flights from {code1} to {code2}. "
        "Mention airlines, costs and duration."
    )


@mcp.tool()
def search_flights(
    from_airport: str,
    to_airport: str,
    date: str,
    *,
    trip: str = "one-way",
    return_date: Optional[str] = None,
    seat: str = "economy",
    adults: int = 1,
    children: int = 0,
    infants_in_seat: int = 0,
    infants_on_lap: int = 0,
    max_stops: Optional[int] = None,
    fetch_mode: str = "common",
) -> str:
    """Search for flights using :mod:`fast_flights`."""
    if trip == "round-trip" and not return_date:
        raise ValueError("return_date required for round-trip")

    flight_data = [
        FlightData(
            date=date,
            from_airport=from_airport,
            to_airport=to_airport,
            max_stops=max_stops,
        )
    ]
    if trip == "round-trip" and return_date:
        flight_data.append(
            FlightData(
                date=return_date,
                from_airport=to_airport,
                to_airport=from_airport,
                max_stops=max_stops,
            )
        )

    passengers = Passengers(
        adults=adults,
        children=children,
        infants_in_seat=infants_in_seat,
        infants_on_lap=infants_on_lap,
    )

    result = get_flights(
        flight_data=flight_data,
        trip=trip,
        passengers=passengers,
        seat=seat,
        fetch_mode=fetch_mode,
    )

    if not result.flights:
        return "No flights found."

    return str(result)
search_flights_unwrapped = search_flights


def main() -> None:
    """Run the MCP server."""
    logging.basicConfig(level=logging.INFO)
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
