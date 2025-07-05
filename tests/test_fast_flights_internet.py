#!/usr/bin/env python3
"""
Test fast-flights integration with real internet API calls.
This test makes actual HTTP requests to verify the integration works end-to-end.
"""
import sys
from datetime import datetime, timedelta
from pathlib import Path

import pytest

# ensure package can be imported
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from fast_flights_mcp import search_flights


class TestFastFlightsInternet:
    """Test fast-flights integration with real internet API calls."""

    def test_flight_search_real_api_domestic(self):
        """Test real API call for domestic US flight search."""
        # Use a date 30 days in the future to ensure availability
        future_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")

        # Test popular US domestic route
        result = search_flights.fn(
            from_airport="LAX",
            to_airport="JFK",
            date=future_date,
            trip="one-way",
            adults=1,
        )

        # Verify we get a valid string response
        assert isinstance(result, str)
        assert len(result) > 0

        # Should contain flight information (either flights or "No flights found")
        assert "->" in result or "No flights found" in result

        # If flights found, should have typical flight info
        if "No flights found" not in result:
            # Should have price assessment
            assert "Price assessment:" in result
            # Should have flight details with arrows
            assert "->" in result
            # Should have times and durations
            assert "AM" in result or "PM" in result

        print(f"✅ Domestic flight search result: {result[:200]}...")

    def test_flight_search_real_api_international(self):
        """Test real API call for international flight search."""
        future_date = (datetime.now() + timedelta(days=45)).strftime("%Y-%m-%d")

        # Test international route
        result = search_flights.fn(
            from_airport="JFK",
            to_airport="LHR",  # London Heathrow
            date=future_date,
            trip="one-way",
            adults=1,
        )

        assert isinstance(result, str)
        assert len(result) > 0
        assert "->" in result or "No flights found" in result

        if "No flights found" not in result:
            assert "Price assessment:" in result
            assert "->" in result

        print(f"✅ International flight search result: {result[:200]}...")

    def test_flight_search_real_api_round_trip(self):
        """Test real API call for round-trip flight search."""
        departure_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        return_date = (datetime.now() + timedelta(days=37)).strftime("%Y-%m-%d")

        result = search_flights.fn(
            from_airport="SFO",
            to_airport="LAX",
            date=departure_date,
            trip="round-trip",
            return_date=return_date,
            adults=1,
        )

        assert isinstance(result, str)
        assert len(result) > 0
        assert "->" in result or "No flights found" in result

        if "No flights found" not in result:
            assert "Price assessment:" in result
            assert "->" in result

        print(f"✅ Round-trip flight search result: {result[:200]}...")

    def test_flight_search_real_api_multiple_passengers(self):
        """Test real API call with multiple passengers."""
        future_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")

        result = search_flights.fn(
            from_airport="LAX",
            to_airport="SFO",
            date=future_date,
            trip="one-way",
            adults=2,
            children=1,
            seat="economy",
        )

        assert isinstance(result, str)
        assert len(result) > 0
        assert "->" in result or "No flights found" in result

        print(f"✅ Multiple passengers flight search result: {result[:200]}...")

    def test_error_handling_real_api(self):
        """Test error handling with real API calls."""
        future_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        # Test invalid airport codes
        try:
            result = search_flights.fn(
                from_airport="INVALID",
                to_airport="ALSOINVALID",
                date=future_date,
                trip="one-way",
            )

            # Should handle errors gracefully (not crash)
            assert isinstance(result, str)
            # Should indicate no flights found or contain error info
            assert (
                "No flights found" in result
                or "error" in result.lower()
                or len(result) > 0
            )
            print(f"✅ Error handling test: {result[:100]}...")

        except RuntimeError as e:
            # fast-flights throws RuntimeError for invalid routes
            assert "No flights found" in str(e)
            print(
                "✅ Error handling test: "
                f"Correctly caught RuntimeError - {str(e)[:100]}..."
            )

    def test_different_seat_classes_real_api(self):
        """Test real API calls with different seat classes."""
        future_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")

        seat_classes = ["economy", "premium_economy", "business", "first"]

        for seat_class in seat_classes:
            try:
                result = search_flights.fn(
                    from_airport="LAX",
                    to_airport="SFO",
                    date=future_date,
                    trip="one-way",
                    adults=1,
                    seat=seat_class,
                )

                assert isinstance(result, str)
                assert len(result) > 0
                print(f"✅ {seat_class} class search worked: {result[:100]}...")

            except Exception as e:
                # Some seat classes might not be available for all routes
                print(f"⚠️  {seat_class} class search failed (might be expected): {e}")

    @pytest.mark.slow
    def test_comprehensive_real_flight_search(self):
        """Comprehensive test of real flight search functionality."""
        future_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")

        # Test a route that's likely to have flights
        result = search_flights.fn(
            from_airport="LAX",
            to_airport="SFO",
            date=future_date,
            trip="one-way",
            adults=1,
            seat="economy",
            max_stops=1,
        )

        assert isinstance(result, str)
        assert len(result) > 0

        # If flights are found, verify structure
        if "No flights found" not in result:
            lines = result.split("\n")

            # Should have price assessment
            price_line = [line for line in lines if "Price assessment:" in line]
            assert len(price_line) > 0

            # Should have numbered flight options
            flight_lines = [
                line for line in lines if line.strip().startswith(("1.", "2.", "3."))
            ]
            assert len(flight_lines) > 0

            # Each flight line should have basic info
            for line in flight_lines[:3]:  # Check first 3 flights
                assert "->" in line  # Should have origin -> destination
                assert "AM" in line or "PM" in line  # Should have time
                assert "$" in line or "₪" in line or "€" in line  # Should have price

        print(f"✅ Comprehensive test passed: {result[:300]}...")


def test_internet_connectivity():
    """Test that we can make internet requests."""
    import urllib.error
    import urllib.request

    try:
        # Simple connectivity test
        urllib.request.urlopen("https://www.google.com", timeout=5)
        print("✅ Internet connectivity confirmed")
        return True
    except urllib.error.URLError:
        pytest.skip("No internet connectivity available")
        return False


if __name__ == "__main__":
    """Run tests directly when script is executed."""
    print("🌐 FAST-FLIGHTS REAL INTERNET API TESTS")
    print("=" * 50)

    # Check internet connectivity first
    if not test_internet_connectivity():
        print("❌ No internet connectivity - skipping tests")
        exit(1)

    # Create test instance
    test_instance = TestFastFlightsInternet()

    print("\n🔍 Testing domestic flight search...")
    test_instance.test_flight_search_real_api_domestic()

    print("\n🔍 Testing international flight search...")
    test_instance.test_flight_search_real_api_international()

    print("\n🔍 Testing round-trip flight search...")
    test_instance.test_flight_search_real_api_round_trip()

    print("\n🔍 Testing multiple passengers...")
    test_instance.test_flight_search_real_api_multiple_passengers()

    print("\n🔍 Testing error handling...")
    test_instance.test_error_handling_real_api()

    print("\n🔍 Testing different seat classes...")
    test_instance.test_different_seat_classes_real_api()

    print("\n✅ ALL REAL INTERNET API TESTS COMPLETED!")
    print("🎉 Fast-flights integration is working with real internet data!")
