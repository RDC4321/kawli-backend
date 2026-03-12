from fastapi import FastAPI
from app.api import utils
from app.api import search

app = FastAPI(
    title="Kawli API",
    description="AI-powered travel discovery and planning platform",
    version="1.0.0"
)

app.include_router(utils.router)
app.include_router(search.router)