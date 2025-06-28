import sys
from pathlib import Path

# ensure package can be imported
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from fast_flights_mcp import (
    search_airports,
    search_flights,
    seat_classes,
    plan_trip,
    compare_airports,
)
from fast_flights import Airport, Flight, Result
import asyncio


def test_search_airports(monkeypatch):
    def fake_search(query: str):
        return [Airport.SAN_FRANCISCO_INTERNATIONAL_AIRPORT]

    monkeypatch.setattr("fast_flights_mcp.server.search_airport", fake_search)
    resp = search_airports.fn("san")
    assert "SFO" in resp


def test_search_flights(monkeypatch):
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
    result = Result(current_price="low", flights=[flight])

    def fake_get_flights(**kwargs):
        return result

    monkeypatch.setattr("fast_flights_mcp.server.get_flights", fake_get_flights)

    resp = search_flights.fn("SFO", "LAX", "2025-01-01")
    assert "Test Airline" in resp
    assert "$100" in resp


def test_resources_and_prompts():
    assert "economy" in asyncio.run(seat_classes.read())
    msg1 = asyncio.run(compare_airports.render({"code1": "SFO", "code2": "LAX"}))
    assert "SFO" in msg1[0].content.text
    msg2 = asyncio.run(plan_trip.render({"destination": "Tokyo"}))
    assert "Tokyo" in msg2[0].content.text
