from app.integrations.travelpayouts_api import search_flights_api as _travelpayouts_search
 
 
def search_flights_api(origin: str, destination: str, date: str) -> dict:
    return _travelpayouts_search(origin, destination, date)