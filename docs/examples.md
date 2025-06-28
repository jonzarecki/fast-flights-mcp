# Usage Examples

Here are a few short examples using the tools provided by the server.

## Search for airports
```python
from fast_flights_mcp import search_airports
print(search_airports.fn("san"))
```

## Search for flights
```python
from fast_flights_mcp import search_flights
print(search_flights.fn("SFO", "LAX", "2025-01-01"))
```

See the `fast_flights_mcp.server` module for full parameter details.

## Bulk tool calls
```python
from fast_flights_mcp import call_tools_bulk

results = call_tools_bulk.fn([
    {"tool": "search_airports", "arguments": {"query": "san"}},
    {"tool": "search_flights", "arguments": {"from_airport": "SFO", "to_airport": "LAX", "date": "2025-01-01"}},
])
print(results)
```
