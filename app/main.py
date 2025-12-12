# app/main.py
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging

from app.db.session import engine, Base
from app.api.routes import router as api_router
from app.config import settings

# Configurazione logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# CREA LE TABELLE ALLO STARTUP (per ora, prima di Alembic)
Base.metadata.create_all(bind=engine)

# Configura root_path solo se non vuoto
root_path = settings.ROOT_PATH if hasattr(settings, 'ROOT_PATH') and settings.ROOT_PATH else ""

app = FastAPI(
    title="Reorder Backend",
    version="0.1.1",
    root_path=root_path if root_path else None,  # None invece di stringa vuota
)

# Configurazione CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permette tutte le origini
    allow_credentials=True,
    allow_methods=["*"],  # Permette tutti i metodi
    allow_headers=["*"],  # Permette tutti gli header
)


# Middleware per logging delle richieste (utile per debug)
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"{request.method} {request.url.path} - Headers: {dict(request.headers)}")
    response = await call_next(request)
    logger.info(f"Response status: {response.status_code}")
    return response

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


@app.get("/health")
def health_check_root():
    """Endpoint health check senza prefisso /api per compatibilità"""
    return {"status": "ok", "service": "reorder-backend"}


@app.get("/routes")
def list_routes():
    """Lista tutti i route disponibili per debug"""
    routes = []
    for route in app.routes:
        if hasattr(route, "methods") and hasattr(route, "path"):
            routes.append({
                "path": route.path,
                "methods": list(route.methods) if route.methods else []
            })
    return {"routes": routes}
