from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import utils
from app.api import search

app = FastAPI(
    title="Kawli API",
    description="AI-powered travel discovery and planning platform",
    version="1.0.0"
)

# CORS middleware (must be early)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow Framer frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(utils.router)
app.include_router(search.router)