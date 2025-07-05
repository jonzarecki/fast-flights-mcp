import logging
import re
from dataclasses import dataclass
from datetime import datetime, time, timedelta
from typing import List, Optional

import moneyed
from fast_flights import Flight as RawFlight
from fast_flights import Result as RawResult
from moneyed import Money

@dataclass(frozen=True)
class FlightInfo:
    """A strictly-typed dataclass for processed flight information."""
    is_best: bool
    name: str
    departure: datetime
    arrival: datetime
    duration: Optional[timedelta]
    stops: int
    price: Optional[Money]
    delay: Optional[timedelta]

@dataclass
class FlightResults:
    """A dataclass to hold the final list of processed and filtered flights."""
    current_price_indicator: str
    flights: List[FlightInfo]

def _parse_price(price_str: str) -> Optional[Money]:
    """Parses a price string like '₪908' into a Money object."""
    if not price_str:
        return None
    
    currency_symbol_map = {'₪': 'ILS', '$': 'USD', '€': 'EUR'}
    currency_code = 'XXX'  # Default for unknown currency
    
    for symbol, code in currency_symbol_map.items():
        if symbol in price_str:
            currency_code = code
            break
            
    amount_str = re.sub(r'[^\d.]', '', price_str)
    if not amount_str:
        return None
        
    return moneyed.Money(amount=float(amount_str), currency=currency_code)

def _parse_duration(duration_str: Optional[str]) -> Optional[timedelta]:
    """Parses a duration string like '6 hr 14 min' into a timedelta."""
    if not duration_str:
        return None
    
    hours, minutes = 0, 0
    if 'hr' in duration_str:
        hours = int(re.search(r'(\d+)\s*hr', duration_str).group(1))
    if 'min' in duration_str:
        minutes = int(re.search(r'(\d+)\s*min', duration_str).group(1))
        
    return timedelta(hours=hours, minutes=minutes)

def _parse_datetime(dt_str: str, reference_date: datetime.date) -> datetime:
    """Parses a flight datetime string like '10:10 PM on Mon, Aug 4' into a datetime object."""
    time_str, date_part = dt_str.split(" on ")
    # We need to add the year to the date string to parse it.
    # We'll use the year from the reference (departure) date.
    full_date_str = f"{date_part}, {reference_date.year}"
    return datetime.strptime(f"{full_date_str} {time_str}", "%a, %b %d, %Y %I:%M %p")


def parse_flight_results(raw_result: RawResult, departure_date: datetime.date) -> FlightResults:
    """Converts a raw Result object from fast_flights into a structured FlightResults dataclass."""
    if not raw_result or not raw_result.flights:
        return FlightResults(current_price_indicator="unknown", flights=[])

    parsed_flights = []
    for raw_flight in raw_result.flights:
        try:
            departure_dt = _parse_datetime(raw_flight.departure, departure_date)
            arrival_dt = _parse_datetime(raw_flight.arrival, departure_date)

            if raw_flight.arrival_time_ahead == '+1' or arrival_dt < departure_dt:
                arrival_dt += timedelta(days=1)

            flight_info = FlightInfo(
                is_best=raw_flight.is_best,
                name=raw_flight.name,
                departure=departure_dt,
                arrival=arrival_dt,
                duration=_parse_duration(raw_flight.duration),
                stops=raw_flight.stops,
                price=_parse_price(raw_flight.price),
                delay=_parse_duration(raw_flight.delay)
            )
            parsed_flights.append(flight_info)
        except Exception as e:
            logging.warning(f"Skipping flight due to parsing error: {e}. Raw data: {raw_flight}")
            continue
            
    return FlightResults(
        current_price_indicator=raw_result.current_price,
        flights=parsed_flights
    ) 