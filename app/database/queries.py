import json
from datetime import datetime, timedelta
from app.database.supabase_client import supabase


def save_search(origin, destination, depart_date):
    try:
        supabase.table("search_history").insert({
            "origin_airport": origin,
            "destination_airport": destination,
            "depart_date": depart_date
        }).execute()
    except Exception as e:
        print(f"[WARN] save_search failed (non-critical): {e}")


def search_airports(query):
    response = (
        supabase.table("airports")
        .select("airport_code, airport_name, city, country_code")
        .eq("is_major_airport", True)
        .or_(f"city.ilike.%{query}%,airport_name.ilike.%{query}%")
        .limit(10)
        .execute()
    )
    return response.data


def get_airports_by_city(city):
    # Match city name, city_code (NYC, TYO, LON...), or direct IATA code (JFK, DXB...)
    response = (
        supabase.table("airports")
        .select("airport_code, city_code, city")
        .or_(f"city.ilike.%{city}%,city_code.ilike.%{city}%,airport_code.ilike.%{city}%")
        .eq("is_major_airport", True)
        .execute()
    )
    airports = response.data

    if not airports:
        print(f"[DEBUG] get_airports_by_city: no match for '{city}'")
        return []

    print(f"[DEBUG] get_airports_by_city: '{city}' → {[a['airport_code'] for a in airports]}")

    # Expand grouped cities: NYC → JFK + LGA + EWR, TYO → NRT + HND, etc.
    city_code = airports[0].get("city_code")
    if city_code:
        grouped = (
            supabase.table("airports")
            .select("airport_code")
            .eq("city_code", city_code)
            .eq("is_major_airport", True)
            .execute()
        )
        print(f"[DEBUG] city_code '{city_code}' expands to: {[a['airport_code'] for a in grouped.data]}")
        return grouped.data

    return airports


def get_flight_cache(cache_key):
    """Returns cached flight_data if found and not expired, else None."""
    try:
        response = (
            supabase.table("flight_search_cache")
            .select("flight_data, expires_at")
            .eq("cache_key", cache_key)
            .execute()
        )
        if not response.data:
            return None

        row = response.data[0]

        # Check expiry if expires_at is set
        expires_at = row.get("expires_at")
        if expires_at:
            expiry = datetime.fromisoformat(expires_at.replace("Z", "+00:00"))
            if datetime.now(expiry.tzinfo) > expiry:
                print(f"[DEBUG] Cache EXPIRED for {cache_key}")
                return None

        return row.get("flight_data")

    except Exception as e:
        print(f"[WARN] get_flight_cache failed ({cache_key}): {e}")
        return None


def save_flight_cache(cache_key, origin, destination, depart_date, data, ttl_hours=6):
    """Save flight results to cache. TTL defaults to 6 hours."""
    try:
        now = datetime.utcnow()
        expires = now + timedelta(hours=ttl_hours)

        supabase.table("flight_search_cache").insert({
            "cache_key": cache_key,
            "origin_airport": origin,
            "destination_airport": destination,
            "depart_date": depart_date,
            "cached_at": now.isoformat(),
            "expires_at": expires.isoformat(),
            "flight_data": data          # ← the jsonb column we added
        }).execute()
        print(f"[DEBUG] Cached {origin}→{destination} (expires in {ttl_hours}h)")
    except Exception as e:
        print(f"[WARN] save_flight_cache failed ({cache_key}): {e}")