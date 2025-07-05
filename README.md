# Fast Flights MCP

[![CI](https://github.com/jonzarecki/fast-flights-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/jonzarecki/fast-flights-mcp/actions/workflows/ci.yml)

A Model Context Protocol (MCP) server that exposes the [fast-flights](https://pypi.org/project/fast-flights/) search library.  It provides a tool for searching for one‑way or round‑trip flights in a way that works well with Claude or other MCP clients.

## Installation

```bash
pip install git+https://github.com/jonzarecki/fast-flights-mcp
```

You can also run the server via `npx` without installing it system-wide:

```bash
npx --yes github:jonzarecki/fast-flights-mcp
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

The server exposes one main tool:

- `search_flights(...)`: search for one‑way or round‑trip flights

With FastMCP 2.9+ you can batch tool calls for efficiency using `call_tools_bulk` or `call_tool_bulk` from this package.

See the docstrings in `fast_flights_mcp.flights` for full parameter details.

For more examples see [docs/examples.md](docs/examples.md). A quick Python usage
snippet:

```python
from fast_flights_mcp import search_flights
print(search_flights.fn(from_airport="JFK", to_airport="LAX", date="2025-10-01"))
```

## Development

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for details. After cloning the repository run:

```bash
pip install -e .[test]
```

Install the pre-commit hooks as well:

```bash
pre-commit install
```

Then run the test suite with coverage:

```bash
pytest --cov=fast_flights_mcp --cov-report=term-missing
```

## MCP client configuration

If your MCP client supports automatic server installation, add the following JSON
to your `mcp.json` file. The client will fetch the package via `npx` and launch
the server for you:

```json
{
  "mcpServers": {
    "fast-flights-mcp": {
      "command": "npx --yes github:jonzarecki/fast-flights-mcp",
      "env": {}
    }
  }
}
```

Replace the repo URL with your fork if you wish to make local changes.
