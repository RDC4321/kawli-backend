import traceback
from fastapi import APIRouter, HTTPException
from app.database.queries import (
    save_search, get_airports_by_city, search_airports,
    save_flight_cache, get_flight_cache
)
from app.api.utils import generate_cache_key, generate_routes
from app.services.flight_service import search_flights_api

router = APIRouter(prefix="/search", tags=["search"])


@router.get("/flights")
def search_flights(origin: str, destination: str, depart_date: str):
    try:
        print(f"[INFO] /search/flights → origin={origin}, dest={destination}, date={depart_date}")

        origin_airports = get_airports_by_city(origin)
        destination_airports = get_airports_by_city(destination)

        if not origin_airports:
            return {"error": f"Origin '{origin}' not found. Try a city name or IATA code (e.g. 'New York' or 'JFK')."}
        if not destination_airports:
            return {"error": f"Destination '{destination}' not found. Try a city name or IATA code (e.g. 'Tokyo' or 'NRT')."}

        origin_codes = [a["airport_code"] for a in origin_airports]
        destination_codes = [a["airport_code"] for a in destination_airports]

        print(f"[INFO] Routes: {origin_codes} → {destination_codes}")

        routes = generate_routes(origin_codes, destination_codes)
        results = []

        for origin_code, destination_code in routes:
            cache_key = generate_cache_key(origin_code, destination_code, depart_date)
            cached = get_flight_cache(cache_key)

            if cached:
                print(f"[INFO] Cache HIT: {origin_code}-{destination_code}")
                results.append({
                    "route": f"{origin_code}-{destination_code}",
                    "source": "cache",
                    "data": cached
                })
            else:
                print(f"[INFO] Cache MISS: {origin_code}-{destination_code}")
                flight_data = search_flights_api(origin_code, destination_code, depart_date)
                save_flight_cache(cache_key, origin_code, destination_code, depart_date, flight_data)
                results.append({
                    "route": f"{origin_code}-{destination_code}",
                    "source": "api",
                    "data": flight_data
                })
        all_flights = []
        for r in results:
            flights = r.get("data", {}).get("flights", [])
            all_flights.extend(flights)
        requested_date_flights = []
        cheapest_other_dates = []

        for f in all_flights:
            if f.get("depart_date") == depart_date:
                requested_date_flights.append(f)
            else:
                cheapest_other_dates.append(f)
        requested_date_flights.sort(key=lambda x: x.get("price_usd", 9999))
        cheapest_other_dates.sort(key=lambda x: x.get("price_usd", 9999))
        
        cheapest_other_dates = cheapest_other_dates[:5]
        save_search(origin, destination, depart_date)

        return {
            "origin_input": origin,
            "destination_input": destination,
            "requested_date_flights": requested_date_flights,
            "cheapest_other_dates": cheapest_other_dates,
                "routes_checked": len(routes)
        }

    except Exception as e:
        print(f"[ERROR] /search/flights crashed:\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/airports")
def airport_autocomplete(q: str):
    try:
        airports = search_airports(q)
        results = []
        for a in airports:
            city = a.get("city") or "Unknown city"
            results.append({
                "code": a["airport_code"],
                "name": a["airport_name"],
                "city": city,
                "country": a["country_code"],
                "display": f"{city} - {a['airport_name']} ({a['airport_code']})"
            })
        return {"results": results}

    except Exception as e:
        print(f"[ERROR] /search/airports crashed:\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))