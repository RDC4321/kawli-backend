from app.database.supabase_client import supabase

def save_search(origin, destination, depart_date):
    data = {
        "origin_airport": origin,
        "destination_airport": destination,
        "depart_date": depart_date
    }
    response = supabase.table("search_history").insert(data).execute()
    return response.data

def get_cached_flights(origin, destination, depart_date):
    response = (
        supabase.table("flight_search_cache")
        .select("*")
        .eq("origin_airport", origin)
        .eq("destination_airport", destination)
        .eq("depart_date", depart_date)
        .execute()
    )
    return response.data

def get_airports_by_city(city):

    # Step 1: find airports matching city OR city_code
    response = (
        supabase.table("airports")
        .select("airport_code, city_code")
        .or_(f"city.ilike.%{city}%,city_code.ilike.%{city}%")
        .eq("is_major_airport", True)
        .execute()
    )
    airports = response.data
    if not airports:
        return []

    # Step 2: check if airport belongs to a grouped city
    city_code = airports[0].get("city_code")

    if city_code:
        grouped = (
            supabase.table("airports")
            .select("airport_code")
            .eq("city_code", city_code)
            .eq("is_major_airport", True)
            .execute()
        )

        return grouped.data
    return airports

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