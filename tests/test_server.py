import sys
from datetime import datetime, timedelta
from pathlib import Path

from moneyed import Money

# ensure package can be imported
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from src.fast_flights_mcp.server import search_flights
from src.fast_flights_mcp.flights import FlightInfo, FlightResults


def test_search_flights(monkeypatch):
    def fake_find_flights(*args, **kwargs):
        flight = FlightInfo(
            is_best=True,
            name="Test Airline",
            departure=datetime.now(),
            arrival=datetime.now(),
            duration_minutes=90,
            stops=0,
            delay_minutes=None,
            price=Money("100", "USD"),
        )
        return FlightResults(current_price_indicator="low", flights=[flight])

    # Mock the function as imported by the server module
    monkeypatch.setattr("src.fast_flights_mcp.server.find_flights_impl", fake_find_flights)

    # Use a future date
    future_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
    resp = search_flights.fn("SFO", "LAX", future_date)
    assert "Test Airline" in resp
    assert "Money('100', 'USD')" in resp
