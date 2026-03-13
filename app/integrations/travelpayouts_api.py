import requests
from app.core.config import settings

MONTH_MATRIX_URL = "https://api.travelpayouts.com/v2/prices/month-matrix"
BOOKING_BASE = "https://www.aviasales.com/search"

def search_flights_api(origin: str, destination: str, date: str) -> dict:
    month_start = date[:7] + "-01"
    params = {
        "origin":             origin,
        "destination":        destination,
        "month":              month_start,
        "currency":           "USD",
        "show_to_affiliates": "true",   # only show prices found via affiliate searches
    }
    headers = {
        "X-Access-Token": settings.TRAVELPAYOUTS_TOKEN,
    }
    print(f"[INFO] Travelpayouts month-matrix: {origin} -> {destination} ({month_start})")

    try:
        response = requests.get(
            MONTH_MATRIX_URL,
            params=params,
            headers=headers,
            timeout=10
        )
        response.raise_for_status()
        raw = response.json()
 
    except requests.exceptions.Timeout:
        print(f"[WARN] Travelpayouts timed out for {origin}-{destination}")
        return _error_response(origin, destination, date, "API timeout")
 
    except requests.exceptions.HTTPError as e:
        print(f"[WARN] Travelpayouts HTTP error: {e}")
        return _error_response(origin, destination, date, str(e))
 
    except Exception as e:
        print(f"[WARN] Travelpayouts unexpected error: {e}")
        return _error_response(origin, destination, date, str(e))
    
    if not raw.get("success") or not raw.get("data"):
        print(f"[WARN] No data returned for {origin}-{destination} ({month_start})")
        return _error_response(origin, destination, date, "No flights found for this route/month")
 
    flights = []
    for entry in raw["data"]:
        depart_date = entry.get("depart_date", date)
        booking_url = _build_booking_url(origin, destination, depart_date)
 
        flights.append({
            "origin":           entry.get("origin", origin),
            "destination":      destination,
            "depart_date":      depart_date,
            "price_usd":        entry.get("value"),
            "stops":            entry.get("number_of_changes", 0),
            "found_at":         entry.get("found_at"),
            "actual":           entry.get("actual", False),
            "booking_url":      booking_url,
        })
    # Sort cheapest first
    flights.sort(key=lambda f: f["price_usd"] or 9999)
 
    print(f"[INFO] Found {len(flights)} fare(s) for {origin}→{destination}")
 
    return {
        "route":    f"{origin}-{destination}",
        "date":     date,
        "month":    month_start,
        "flights":  flights,
        "count":    len(flights),
    }
 
def _build_booking_url(origin: str, destination: str, depart_date: str) -> str:
    try:
        parts      = depart_date[:10].split("-")   # ["2026", "06", "03"]
        day_month  = parts[2] + parts[1]            # "0306"
    except Exception:
        day_month = "0101"
 
    path = f"{origin}{day_month}{destination}1"
    return f"{BOOKING_BASE}/{path}?marker={settings.TRAVELPAYOUTS_MARKER}"
 
def _error_response(origin: str, destination: str, date: str, reason: str) -> dict:
    return {
        "route":   f"{origin}-{destination}",
        "date":    date,
        "flights": [],
        "count":   0,
        "error":   reason,
    }