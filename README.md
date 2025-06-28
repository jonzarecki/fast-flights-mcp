# Fast Flights MCP

A Model Context Protocol (MCP) server that exposes the [fast-flights](https://pypi.org/project/fast-flights/) search library.  It provides tools for searching airports and retrieving flight information in a way that works well with Claude or other MCP clients.

## Installation

```bash
pip install fast-flights-mcp
```

or clone the repository and install in editable mode:

```bash
git clone <repo-url>
cd fast-flights-mcp
pip install -e .
```

## Usage

Run the server directly (stdout/stdin transport):

```bash
fast-flights-mcp
```

The server exposes two tools:

- `search_airports(query)`: search for airport codes by name
- `search_flights(...)`: search for one‑way or round‑trip flights

See the docstrings in `fast_flights_mcp.server` for full parameter details.

## Development

Contributions are welcome!  After cloning the repository run:

```bash
pip install -e .[test]
```

Install the pre-commit hooks as well:

```bash
pre-commit install
```

Then run the test suite:

```bash
pytest
```
