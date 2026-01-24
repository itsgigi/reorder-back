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

# CREA LE TABELLE ALLO STARTUP
try:
    Base.metadata.create_all(bind=engine)
    if settings.DATABASE_URL.startswith("postgresql"):
        logger.info("✅ PostgreSQL database tables created/verified successfully")
    elif settings.DATABASE_URL.startswith("sqlite"):
        logger.info("✅ SQLite database tables created successfully")
    else:
        logger.info("✅ Database tables created successfully")
except Exception as e:
    error_msg = str(e).lower()
    if "could not connect" in error_msg or "connection" in error_msg:
        logger.error(f"❌ Cannot connect to database: {e}")
        logger.error("💡 Check your DATABASE_URL connection string")
    else:
        logger.warning(f"⚠️ Could not create database tables: {e}")
        logger.warning("Tables may already exist or database may need initialization")

app = FastAPI(
    title="Reorder Backend",
    version="0.1.1",
)

# Configurazione CORS
# Nota: quando allow_credentials=True, non possiamo usare allow_origins=["*"]
# Dobbiamo specificare esplicitamente le origini permesse
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://reorder-front.vercel.app",  # Produzione frontend
        "http://localhost:5173",  # Sviluppo locale (Vite default)
        "http://localhost:3000",  # Sviluppo locale (alternativo)
        "http://127.0.0.1:5173",  # Sviluppo locale (alternativo)
    ],
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
