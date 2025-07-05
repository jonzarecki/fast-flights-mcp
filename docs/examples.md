# Usage Examples

Here are a few short examples using the tools provided by the server.

## Search for flights
```python
from fast_flights_mcp import search_flights
print(search_flights.fn("SFO", "LAX", "2025-01-01"))
```

See the `fast_flights_mcp.flights` module for full parameter details.

## Bulk tool calls
```python
from fast_flights_mcp import call_tools_bulk
from fastmcp.contrib.bulk_tool_caller import CallToolRequest
import asyncio

reqs = [
    CallToolRequest(
        tool="search_flights",
        arguments={"from_airport": "SFO", "to_airport": "LAX", "date": "2025-01-01"},
    ),
    CallToolRequest(
        tool="search_flights",
        arguments={"from_airport": "JFK", "to_airport": "LHR", "date": "2025-01-01"},
    ),
]

results = asyncio.run(call_tools_bulk(reqs))
print(results)
```

You can also call a single tool multiple times in one request with
`call_tool_bulk`:

```python
from fast_flights_mcp import call_tool_bulk
import asyncio

results = asyncio.run(
    call_tool_bulk(
        "search_flights",
        [
            {"from_airport": "SFO", "to_airport": "LAX", "date": "2025-01-01"},
            {"from_airport": "JFK", "to_airport": "LHR", "date": "2025-01-01"},
        ],
    )
)
print(results)
```
