# app/config.py
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # DB
    # Default: SQLite per sviluppo locale
    # Produzione: PostgreSQL (Supabase, Neon, Railway, etc.)
    # Formato PostgreSQL: postgresql://user:password@host:port/dbname
    DATABASE_URL: str = "sqlite:///./reorder.db"

    # OpenAI / Datapizza
    OPENAI_API_KEY: str = "CHANGE_ME"
    
    # Deployment
    ROOT_PATH: str = ""  # Per reverse proxy (es: "/api" se deployato su /api)

    class Config:
        env_file = ".env"


settings = Settings()
