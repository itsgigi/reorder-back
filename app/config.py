# app/config.py
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # DB
    # Default: SQLite per sviluppo locale
    # Produzione: PostgreSQL (Supabase, Neon, Railway, Render, etc.)
    # Formato PostgreSQL: postgresql://user:password@host:port/dbname
    DATABASE_URL: str = "sqlite:///./reorder.db"

    # OpenAI / Datapizza
    OPENAI_API_KEY: str = "CHANGE_ME"

    class Config:
        env_file = ".env"


settings = Settings()
