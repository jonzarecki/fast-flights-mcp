import sys
from pathlib import Path
import asyncio

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from fast_flights_mcp import call_tools_bulk, call_tool_bulk
from fastmcp.contrib.bulk_tool_caller.bulk_tool_caller import CallToolRequest
from fast_flights import Airport, Flight, Result


def _fake_search(query: str):
    return [Airport.SAN_FRANCISCO_INTERNATIONAL_AIRPORT]


flight = Flight(
    is_best=True,
    name="Test Airline",
    departure="SFO 10:00",
    arrival="LAX 11:30",
    arrival_time_ahead="",
    duration="1h30m",
    stops=0,
    delay=None,
    price="$100",
)
_result = Result(current_price="low", flights=[flight])


def _fake_get_flights(**kwargs):
    return _result


def test_call_tools_bulk(monkeypatch):
    monkeypatch.setattr("fast_flights_mcp.server.search_airport", _fake_search)
    monkeypatch.setattr("fast_flights_mcp.server.get_flights", _fake_get_flights)
    reqs = [
        CallToolRequest(tool="search_airports", arguments={"query": "san"}),
        CallToolRequest(
            tool="search_flights",
            arguments={
                "from_airport": "SFO",
                "to_airport": "LAX",
                "date": "2025-01-01",
            },
        ),
    ]
    results = asyncio.run(call_tools_bulk(reqs))
    assert len(results) == 2
    assert "SFO" in results[0].content[0].text
    assert "Test Airline" in results[1].content[0].text


def test_call_tool_bulk(monkeypatch):
    monkeypatch.setattr("fast_flights_mcp.server.search_airport", _fake_search)
    reqs = [{"query": "san"}, {"query": "foo"}]
    results = asyncio.run(call_tool_bulk("search_airports", reqs))
    assert len(results) == 2
    assert all(not r.isError for r in results)
