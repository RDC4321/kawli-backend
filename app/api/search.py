from fastapi import APIRouter, Query
from app.database.queries import save_search, get_cached_flights, get_airports_by_city, search_airports
from app.api.utils import generate_cache_key, generate_routes
from app.database.supabase_client import supabase

router = APIRouter(prefix="/search", tags=["search"])

@router.get("/flights")
def search_flights(origin: str, destination: str, depart_date: str):

    # convert city → airport
    origin_airports = get_airports_by_city(origin)
    destination_airports = get_airports_by_city(destination)

    if not origin_airports or not destination_airports:
        return {"error": "City not found in airport database"}

    origin_codes = [a["airport_code"] for a in origin_airports]
    destination_codes = [a["airport_code"] for a in destination_airports]
    routes = generate_routes(origin_codes, destination_codes)

    #generate cache key
    cache_key = generate_cache_key(origin_codes,destination_codes,depart_date)

    #check cache
    cached = (
        supabase.table("flight_search_cache")
        .select("*")
        .eq("cache_key",cache_key)
        .execute()
    )
    if cached.data:
        return{
            "source": "cache",
            "origin": origin_codes,
            "destination": destination_codes,
            "results": cached.data
        }

    # save search
    save_search(origin_codes, destination_codes, depart_date)

    return {
        "source": "api",
        "origin": origin_codes,
        "destination": destination_codes,
        "routes": routes,
        "message": "No cached flights yet"
    }

@router.get("/airports")
def airport_autocomplete(q: str):

    airports = search_airports(q)

    results = []

    for a in airports:
        city = a["city"] or "Unknown city"

        results.append({
            "code": a["airport_code"],
            "name": a["airport_name"],
            "city": city,
            "country": a["country_code"],
            "display": f"{city} - {a['airport_name']} ({a['airport_code']})"
        })
    
    return {"results": results}