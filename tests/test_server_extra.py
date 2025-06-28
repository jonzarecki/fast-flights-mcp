import sys
from pathlib import Path
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from fast_flights_mcp import search_airports, search_flights


def test_search_airports_no_results(monkeypatch):
    monkeypatch.setattr("fast_flights_mcp.server.search_airport", lambda q: [])
    assert search_airports.fn("nowhere") == "No airports found"


def test_search_flights_roundtrip_missing_return(monkeypatch):
    monkeypatch.setattr(
        "fast_flights_mcp.server.get_flights", lambda **kw: None
    )
    with pytest.raises(ValueError):
        search_flights.fn("SFO", "LAX", "2025-01-01", trip="round-trip")
