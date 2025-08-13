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

### Fetch Modes

The package supports different fetch modes for flight data:

- **`common`** (default): Uses serverless functions (fastest)
- **`local`**: Uses local Playwright browser (slower, but more reliable in some regions)  
- **`fallback`**: Tries serverless first, falls back to local on failure (recommended)
- **`force-fallback`**: Always uses the fallback method

### Alternative Fetch Modes

If you're experiencing connection issues with the default mode, you have several options:

#### Quick Fix: Use Fallback Mode
```bash
npx --yes github:jonzarecki/fast-flights-mcp --fetch-mode=fallback
```
*This tries the fast serverless method first, automatically falls back to local if needed*

#### Full Local Mode Setup

**Option 1: Install with Local Dependencies**
```bash
# Install with local dependencies (includes playwright)
pip install -e ".[local]"

# Install Playwright browser (required for local mode)
python -m playwright install chromium

# Run with local mode
FAST_FLIGHTS_FETCH_MODE=local fast-flights-mcp
```

**Option 2: Command Line Parameter**
```bash
# Note: Requires playwright browser to be installed separately
npx --yes github:jonzarecki/fast-flights-mcp --fetch-mode=local
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

## MCP Client Configuration

If your MCP client supports automatic server installation, add the following JSON
to your `mcp.json` file. The client will fetch the package via `npx` and launch
the server for you:

### Standard Mode (Default)
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

### Local Mode
*Requires local installation with playwright dependencies*
```json
{
  "mcpServers": {
    "fast-flights-mcp": {
      "command": "fast-flights-mcp",
      "env": {
        "FAST_FLIGHTS_FETCH_MODE": "local"
      }
    }
  }
}
```

### Fallback Mode (Best of Both)
```json
{
  "mcpServers": {
    "fast-flights-mcp": {
      "command": "npx --yes github:jonzarecki/fast-flights-mcp",
      "env": {
        "FAST_FLIGHTS_FETCH_MODE": "fallback"
      }
    }
  }
}
```

Replace the repo URL with your fork if you wish to make local changes.
