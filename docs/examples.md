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
