# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.db.session import engine, Base
from app.api.routes import router as api_router
from app.config import settings

# CREA LE TABELLE ALLO STARTUP (per ora, prima di Alembic)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Reorder Backend",
    version="0.1.1",
    root_path=settings.ROOT_PATH if hasattr(settings, 'ROOT_PATH') else "",
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


@app.get("/")
def root():
    """Endpoint root per verificare che l'applicazione sia attiva"""
    return JSONResponse({
        "status": "ok",
        "message": "Reorder Backend API",
        "version": "0.1.1",
        "docs": "/docs",
        "health": "/api/health"
    })
