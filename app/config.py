# app/config.py
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # DB
    DATABASE_URL: str = "sqlite:///./reorder.db"  # per partire subito

    # OpenAI / Datapizza
    OPENAI_API_KEY: str = "CHANGE_ME"

    class Config:
        env_file = ".env"


settings = Settings()
