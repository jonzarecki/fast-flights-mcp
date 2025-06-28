# Fast Flights MCP

[![CI](https://github.com/example/fast-flights-mcp/actions/workflows/ci.yml/badge.svg)](https://github.com/example/fast-flights-mcp/actions/workflows/ci.yml)

A Model Context Protocol (MCP) server that exposes the [fast-flights](https://pypi.org/project/fast-flights/) search library.  It provides tools for searching airports and retrieving flight information in a way that works well with Claude or other MCP clients.

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

The server exposes two tools:

- `search_airports(query)`: search for airport codes by name
- `search_flights(...)`: search for one‑way or round‑trip flights

See the docstrings in `fast_flights_mcp.server` for full parameter details.

For more examples see [docs/examples.md](docs/examples.md). A quick Python usage
snippet:

```python
from fast_flights_mcp import search_airports
print(search_airports.fn("san"))
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
