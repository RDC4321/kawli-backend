from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Supabase
    SUPABASE_URL: str
    SUPABASE_KEY: str
    # Travelpayouts / Aviasales
    TRAVELPAYOUTS_TOKEN: str = ""
    TRAVELPAYOUTS_MARKER: str = ""
    # OpenAI (for AI trip planner)
    OPENAI_API_KEY: str = ""
    # Google Places
    GOOGLE_PLACES_API_KEY: str = ""
    # OpenWeather
    OPENWEATHER_API_KEY: str = ""
    # Sherpa (visa info)
    SHERPA_API_KEY: str = ""
    # Resend (email)
    RESEND_API_KEY: str = ""
    # Redis (caching)
    REDIS_URL: str = "redis://localhost:6379"
    # App
    APP_ENV: str = "development" #"development" or "production"
    DEBUG: bool = True

    class Config:
        env_file = ".env"
        extra = "ignore"
settings = Settings()
