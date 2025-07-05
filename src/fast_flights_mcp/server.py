"""MCP server exposing fast-flights search functions."""

import logging
from typing import Annotated, Literal

from fastmcp import FastMCP
from fastmcp.contrib.bulk_tool_caller import BulkToolCaller
from pydantic import Field

from .flights import find_flights as find_flights_impl

logger = logging.getLogger(__name__)

mcp = FastMCP("fast-flights-mcp", dependencies=["fast-flights"])

# Register bulk tool calling utilities
_bulk_tools = BulkToolCaller()
_bulk_tools.register_tools(mcp)


@mcp.tool(
    name="search_flights",
    description="Search for flights between two airports with comprehensive filtering options",
    tags={"flights", "travel", "search"},
    annotations={
        "title": "Flight Search",
        "readOnlyHint": True,
        "idempotentHint": True,
        "openWorldHint": True,
    },
)
def search_flights(
    from_airport: Annotated[
        str,
        Field(
            description="IATA airport code for departure airport (e.g., 'JFK', 'LAX', 'LHR')",
            min_length=3,
            max_length=3,
            pattern=r"^[A-Z]{3}$",
        ),
    ],
    to_airport: Annotated[
        str,
        Field(
            description="IATA airport code for arrival airport (e.g., 'JFK', 'LAX', 'LHR')",
            min_length=3,
            max_length=3,
            pattern=r"^[A-Z]{3}$",
        ),
    ],
    date: Annotated[
        str,
        Field(
            description="Departure date in YYYY-MM-DD format (e.g., '2024-12-25')",
            pattern=r"^\d{4}-\d{2}-\d{2}$",
        ),
    ],
    *,
    trip: Annotated[
        Literal["one-way", "round-trip"],
        Field(
            description="Type of trip: 'one-way' for single direction or 'round-trip' for return journey",
            default="one-way",
        ),
    ] = "one-way",
    return_date: Annotated[
        str | None,
        Field(
            description="Return date in YYYY-MM-DD format. Required for round-trip flights",
            pattern=r"^\d{4}-\d{2}-\d{2}$",
        ),
    ] = None,
    seat: Annotated[
        Literal["economy", "premium", "business", "first"],
        Field(
            description="Seat class preference: 'economy', 'premium', 'business', or 'first'",
            default="economy",
        ),
    ] = "economy",
    adults: Annotated[
        int,
        Field(
            description="Number of adult passengers",
            ge=1,
            le=9,
        ),
    ] = 1,
    max_stops: Annotated[
        int | None,
        Field(
            description="Maximum number of stops allowed (0 for direct flights only, 1 for up to 1 stop)",
            ge=0,
            le=1,
        ),
    ] = None,
    max_price: Annotated[
        int | None,
        Field(
            description="Maximum price per person in the flight's currency (filters out more expensive flights)",
            ge=1,
        ),
    ] = None,
    max_flight_duration_minutes: Annotated[
        int | None,
        Field(
            description="Maximum flight duration in minutes (filters out longer flights)",
            ge=30,
            le=2000,
        ),
    ] = None,
    latest_arrival_time: Annotated[
        str | None,
        Field(
            description="Latest acceptable arrival time in HH:MM format (e.g., '18:30')",
            pattern=r"^(?:[01]\d|2[0-3]):[0-5]\d$",
        ),
    ] = None,
    max_delay_minutes: Annotated[
        int | None,
        Field(
            description="Maximum acceptable delay in minutes (filters out flights with longer delays)",
            ge=0,
            le=300,
        ),
    ] = None,
    target_currency: Annotated[
        Literal["USD", "EUR", "ILS"] | None,
        Field(
            description="Convert all prices to this currency: 'USD', 'EUR', or 'ILS'",
        ),
    ] = None,
) -> str:
    """
    Search for flights between two airports with comprehensive filtering and sorting options.

    This tool searches for flights using the fast-flights library and returns a formatted list
    of available flights with details including:
    - Airline name and flight details
    - Departure and arrival times
    - Flight duration
    - Number of stops (direct/1 stop)
    - Price information
    - Price assessment (lower/typical/higher than usual)

    The results are automatically sorted by relevance and price, with the best options
    marked with a ⭐ symbol.

    Args:
        from_airport: IATA code of departure airport (3-letter code like 'JFK')
        to_airport: IATA code of arrival airport (3-letter code like 'LAX')
        date: Departure date in YYYY-MM-DD format
        trip: Trip type - 'one-way' or 'round-trip'
        return_date: Return date for round-trip flights (YYYY-MM-DD format)
        seat: Seat class preference
        adults: Number of adult passengers (1-9)
        max_stops: Maximum stops allowed (0=direct only, 1=up to 1 stop)
        max_price: Maximum price per person to filter results
        max_flight_duration_minutes: Maximum flight duration to filter results
        latest_arrival_time: Latest acceptable arrival time (HH:MM format)
        max_delay_minutes: Maximum acceptable delay to filter results
        target_currency: Convert prices to this currency

    Returns:
        Formatted string with flight search results, including price assessment
        and up to 10 best matching flights with details.

    Raises:
        ValueError: If parameters are invalid (e.g., past dates, invalid airports)
        RuntimeError: If flight search service is unavailable

    Example:
        search_flights(
            from_airport="JFK",
            to_airport="LAX",
            date="2024-12-25",
            trip="round-trip",
            return_date="2024-12-30",
            adults=2,
            max_stops=1,
            seat="economy"
        )
    """
    # Map max_stops to the expected range (0 or 1)
    if max_stops is None:
        max_stops = 1

    try:
        result = find_flights_impl(
            from_airport=from_airport,
            to_airport=to_airport,
            from_date=date,  # Map 'date' parameter to 'from_date'
            trip=trip,
            return_date=return_date,
            seat=seat,
            adults=adults,
            max_stops=max_stops,
            max_price=max_price,
            max_flight_duration_minutes=max_flight_duration_minutes,
            latest_arrival_time=latest_arrival_time,
            max_delay_minutes=max_delay_minutes,
            target_currency=target_currency,
        )

        if not result or not result.flights:
            return (
                "No flights found matching your criteria. Try adjusting your search parameters "
                "such as dates, airports, or filters."
            )

        return str(result)

    except ValueError as e:
        logger.error(f"Invalid search parameters: {e}")
        return f"Search error: {e}"
    except RuntimeError as e:
        logger.error(f"Flight search service error: {e}")
        return f"Flight search service temporarily unavailable: {e}"
    except Exception as e:
        logger.error(f"Unexpected error during flight search: {e}")
        return "An unexpected error occurred during flight search. Please try again."


def main() -> None:
    """Run the MCP server."""
    logging.basicConfig(level=logging.INFO)
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
