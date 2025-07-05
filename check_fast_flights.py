import logging
import time
from datetime import datetime, timedelta
from typing import Optional
from decimal import Decimal

from fast_flights import FlightData, Passengers, Result, get_flights
from flight_processing import parse_flight_results
from moneyed import Money, CURRENCIES
import requests

SUPPORTED_CURRENCIES = {"USD", "EUR", "ILS"}

def get_exchange_rate(from_currency: str, to_currency: str) -> Optional[float]:
    """Fetches the exchange rate between two currencies."""
    if from_currency == to_currency:
        return 1.0
    try:
        response = requests.get(f"https://api.frankfurter.app/latest?from={from_currency}&to={to_currency}")
        response.raise_for_status()
        data = response.json()
        return data["rates"][to_currency]
    except requests.RequestException as e:
        logging.error(f"Failed to fetch exchange rate: {e}")
        return None


def find_flights(
    from_airport: str,
    to_airport: str,
    from_date: str,
    return_date: Optional[str] = None,
    adults: int = 1,
    seat: str = "economy",
    trip: str = "round-trip",
    max_stops: int = 1,
    max_price: Optional[int] = None,
    max_flight_duration_minutes: Optional[int] = None,
    latest_arrival_time: Optional[str] = None,
    max_delay_minutes: Optional[int] = None,
    target_currency: Optional[str] = None,
):
    if target_currency and target_currency.upper() not in SUPPORTED_CURRENCIES:
        raise ValueError(f"Unsupported target currency: {target_currency}. Supported currencies are {SUPPORTED_CURRENCIES}")

    if trip not in ["one-way", "round-trip"]:
        raise ValueError("Trip type must be 'one-way' or 'round-trip'.")

    if max_stops not in [0, 1]:
        raise ValueError("max_stops can only be 0 or 1.")

    from_date_obj = datetime.strptime(from_date, "%Y-%m-%d").date()
    if from_date_obj < datetime.now().date():
        raise ValueError("Departure date cannot be in the past.")

    flight_data_list = [
        FlightData(
            date=from_date,
            from_airport=from_airport,
            to_airport=to_airport,
            max_stops=max_stops,
        )
    ]

    if trip == "round-trip":
        if not return_date:
            raise ValueError("Return date is required for a round-trip.")
        return_date_obj = datetime.strptime(return_date, "%Y-%m-%d").date()
        if return_date_obj < from_date_obj:
            raise ValueError("Return date cannot be before the departure date.")
        flight_data_list.append(
            FlightData(
                date=return_date,
                from_airport=to_airport,
                to_airport=from_airport,
                max_stops=max_stops,
            )
        )

    raw_result = None
    for attempt in range(3):
        try:
            raw_result: Result = get_flights(
                flight_data=flight_data_list,
                trip=trip,
                seat=seat,
                passengers=Passengers(
                    adults=adults, children=0, infants_in_seat=0, infants_on_lap=0
                ),
                fetch_mode="common",
            )
            logging.info(f"Successfully fetched flights on attempt {attempt + 1}.")
            break
        except RuntimeError as e:
            logging.warning(f"Attempt {attempt + 1}/3 failed: {e}")
            if attempt < 2:
                time.sleep(2)
                logging.info("Retrying...")
            else:
                logging.error("All retries failed.")
                return None

    if not raw_result:
        logging.warning("No flights found that matched the initial criteria.")

        return None

    parsed_results = parse_flight_results(raw_result, from_date_obj)

    if target_currency:
        target_currency = target_currency.upper()
        logging.info(f"Converting prices to {target_currency}")
        for flight in parsed_results.flights:
            if flight.price and flight.price.currency.code != target_currency:
                rate = get_exchange_rate(flight.price.currency.code, target_currency)
                if rate:
                    converted_amount = flight.price.amount * Decimal(str(rate))
                    flight.price = Money(converted_amount, CURRENCIES[target_currency])
                else:
                    logging.warning(f"Could not convert price for flight {flight.name}")

    original_flight_count = len(parsed_results.flights)
    filtered_flights = []

    latest_arrival_time_obj = (
        datetime.strptime(latest_arrival_time, "%H:%M").time()
        if latest_arrival_time
        else None
    )

    for flight in parsed_results.flights:
        if max_price is not None:
            if flight.price:
                max_price_money = Money(max_price, flight.price.currency)
                if flight.price > max_price_money:
                    logging.info(
                        f"Filtering out flight {flight.name} due to price: {flight.price} > {max_price_money}"
                    )
                    continue
            else:
                logging.info(
                    f"Filtering out flight {flight.name} due to missing price."
                )
                continue

        if max_flight_duration_minutes is not None and (
            flight.duration_minutes is None or flight.duration_minutes > max_flight_duration_minutes
        ):
            logging.info(
                f"Filtering out flight {flight.name} due to duration: {flight.duration_minutes}m > {max_flight_duration_minutes}m"
            )
            continue

        if latest_arrival_time_obj is not None and flight.arrival.time() > latest_arrival_time_obj:
            logging.info(
                f"Filtering out flight {flight.name} due to arrival time: {flight.arrival.time()} > {latest_arrival_time_obj}"
            )
            continue

        if max_delay_minutes is not None and flight.delay_minutes is not None:
            if flight.delay_minutes > max_delay_minutes:
                logging.info(
                    f"Filtering out flight {flight.name} due to delay: {flight.delay_minutes}m > {max_delay_minutes}m"
                )
                continue

        filtered_flights.append(flight)

    logging.info(
        f"Finished filtering flights. Original count: {original_flight_count}, Filtered count: {len(filtered_flights)}"
    )

    parsed_results.flights = filtered_flights
    return parsed_results


def main():
    today = datetime.now().date()
    from_date = today + timedelta(days=30)
    return_date = from_date + timedelta(days=10)

    try:
        result = find_flights(
            from_airport="JFK",
            to_airport="LAX",
            from_date=from_date.strftime("%Y-%m-%d"),
            return_date=return_date.strftime("%Y-%m-%d"),
            max_stops=1,
            max_price=2000,
            max_flight_duration_minutes=600,
            latest_arrival_time="22:00",
            max_delay_minutes=60,
            target_currency="ILS",
        )
        if result:
            print(result)
    except (ValueError, RuntimeError) as e:
        logging.error(f"Error finding flights: {e}")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )
    main()
