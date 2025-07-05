import logging
import re
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Optional

import moneyed
import requests
from fast_flights import Flight as RawFlight
from fast_flights import FlightData
from fast_flights import Passengers
from fast_flights import Result as RawResult
from fast_flights import get_flights, search_airport
from moneyed import CURRENCIES, Money


@dataclass
class FlightInfo:
    """A strictly-typed dataclass for processed flight information."""

    is_best: bool
    name: str
    departure: datetime
    arrival: datetime
    duration_minutes: Optional[int]
    stops: int
    price: Optional[Money]
    delay_minutes: Optional[int]


@dataclass
class FlightResults:
    """A dataclass to hold the final list of processed and filtered flights."""

    current_price_indicator: str
    flights: List[FlightInfo]


SUPPORTED_CURRENCIES = {"USD", "EUR", "ILS"}


def get_exchange_rate(from_currency: str, to_currency: str) -> Optional[float]:
    """Fetches the exchange rate between two currencies."""
    if from_currency == to_currency:
        return 1.0
    try:
        response = requests.get(
            f"https://api.frankfurter.app/latest?from={from_currency}&to={to_currency}"
        )
        response.raise_for_status()
        data = response.json()
        return data["rates"][to_currency]
    except requests.RequestException as e:
        logging.error(f"Failed to fetch exchange rate: {e}")
        return None


def _parse_price(price_str: str) -> Optional[Money]:
    """Parses a price string like '₪908' into a Money object."""
    if not price_str:
        return None

    currency_symbol_map = {"₪": "ILS", "$": "USD", "€": "EUR"}
    currency_code = "XXX"  # Default for unknown currency

    for symbol, code in currency_symbol_map.items():
        if symbol in price_str:
            currency_code = code
            break

    amount_str = re.sub(r"[^\d.]", "", price_str)
    if not amount_str:
        return None

    return moneyed.Money(amount=Decimal(amount_str), currency=currency_code)


def _parse_duration(duration_str: Optional[str]) -> Optional[int]:
    """Parses a duration string like '6 hr 14 min' into total minutes."""
    if not duration_str:
        return None

    hours, minutes = 0, 0
    if "hr" in duration_str:
        hours_match = re.search(r"(\d+)\s*hr", duration_str)
        if hours_match:
            hours = int(hours_match.group(1))
    if "min" in duration_str:
        minutes_match = re.search(r"(\d+)\s*min", duration_str)
        if minutes_match:
            minutes = int(minutes_match.group(1))

    return hours * 60 + minutes


def _parse_datetime(dt_str: str, reference_date: datetime.date) -> datetime:
    """Parses a flight datetime string like '10:10 PM on Mon, Aug 4' into a datetime object."""
    time_str, date_part = dt_str.split(" on ")
    # We need to add the year to the date string to parse it.
    # We'll use the year from the reference (departure) date.
    full_date_str = f"{date_part}, {reference_date.year}"
    return datetime.strptime(f"{full_date_str} {time_str}", "%a, %b %d, %Y %I:%M %p")


def parse_flight_results(
    raw_result: RawResult, departure_date: datetime.date
) -> FlightResults:
    """Converts a raw Result object from fast_flights into a structured FlightResults dataclass."""
    if not raw_result or not raw_result.flights:
        return FlightResults(current_price_indicator="unknown", flights=[])

    parsed_flights = []
    for raw_flight in raw_result.flights:
        try:
            departure_dt = _parse_datetime(raw_flight.departure, departure_date)
            arrival_dt = _parse_datetime(raw_flight.arrival, departure_date)

            if raw_flight.arrival_time_ahead == "+1" or arrival_dt < departure_dt:
                arrival_dt += timedelta(days=1)

            flight_info = FlightInfo(
                is_best=raw_flight.is_best,
                name=raw_flight.name,
                departure=departure_dt,
                arrival=arrival_dt,
                duration_minutes=_parse_duration(raw_flight.duration),
                stops=raw_flight.stops,
                price=_parse_price(raw_flight.price),
                delay_minutes=_parse_duration(raw_flight.delay),
            )
            parsed_flights.append(flight_info)
        except Exception as e:
            logging.warning(
                f"Skipping flight due to parsing error: {e}. Raw data: {raw_flight}"
            )
            continue

    return FlightResults(
        current_price_indicator=raw_result.current_price, flights=parsed_flights
    )


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
        raise ValueError(
            f"Unsupported target currency: {target_currency}. Supported currencies are {SUPPORTED_CURRENCIES}"
        )

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
            raw_result: RawResult = get_flights(
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
                    logging.warning(
                        f"Could not convert price for flight {flight.name}"
                    )

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
            flight.duration_minutes is None
            or flight.duration_minutes > max_flight_duration_minutes
        ):
            logging.info(
                f"Filtering out flight {flight.name} due to duration: {flight.duration_minutes}m > {max_flight_duration_minutes}m"
            )
            continue

        if (
            latest_arrival_time_obj is not None
            and flight.arrival.time() > latest_arrival_time_obj
        ):
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


def search_airports(query: str) -> str:
    """Return a list of airports matching ``query``."""
    query = query.lower()
    matches = [
        a
        for a in search_airport("")
        if query in a.name.lower() or query in a.value.lower()
    ]
    if not matches:
        return "No airports found"
    lines = [f"{a.name.replace('_', ' ').title()} ({a.value})" for a in matches[:20]]
    if len(matches) > 20:
        lines.append(f"...and {len(matches) - 20} more results")
    return "\n".join(lines)


def main():
    """Main function for testing flight search functionality."""
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