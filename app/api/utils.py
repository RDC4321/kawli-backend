from fastapi import APIRouter
import hashlib
from itertools import product

router = APIRouter()

@router.get("/")
def root():
    return {"message": "Kawli API running"}

@router.get("/health")
def health_check():
    return {"status": "Kawli backend running"}

def generate_cache_key(origin, destination, depart_date):

    raw = f"{origin}-{destination}-{depart_date}"
    return hashlib.md5(raw.encode()).hexdigest()

def generate_routes(origins,destinations):
    routes = list(product(origins,destinations))
    return list(set(routes))