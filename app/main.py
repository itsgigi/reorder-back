# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.session import engine, Base
from app.api.routes import router as api_router

# CREA LE TABELLE ALLO STARTUP (per ora, prima di Alembic)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Reorder Backend",
    version="0.1.1",
)

# Configurazione CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permette tutte le origini
    allow_credentials=True,
    allow_methods=["*"],  # Permette tutti i metodi
    allow_headers=["*"],  # Permette tutti gli header
)

app.include_router(api_router, prefix="/api")
