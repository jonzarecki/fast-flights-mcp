import json
from fast_flights import get_flights, FlightData, Passengers
from fast_flights import FlightData, Passengers, Result, get_flights

def main():
    result: Result = get_flights(
        flight_data=[
            FlightData(date="2025-10-01", from_airport="TLV", to_airport="HND",
    max_stops=2  # optional
    ),
            FlightData(date="2025-10-20", from_airport="HND", to_airport="TLV",
    max_stops=2  # optional
    )

        ],
        trip="round-trip",
        seat="economy",
        passengers=Passengers(adults=1, children=0, infants_in_seat=0, infants_on_lap=0),
        fetch_mode="common",
    )

    print(result)

if __name__ == "__main__":
    main() 