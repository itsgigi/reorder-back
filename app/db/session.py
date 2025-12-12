# app/db/session.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.config import settings

# Pulisci la connection string da parametri non supportati da psycopg2
# Rimuovi pgbouncer=true se presente (psycopg2 non lo riconosce)
database_url = settings.DATABASE_URL
if "?" in database_url:
    base_url, params = database_url.split("?", 1)
    if params:
        # Rimuovi parametri pgbouncer (non supportati da psycopg2)
        filtered_params = [
            p.strip() for p in params.split("&")
            if p.strip() and not p.strip().lower().startswith("pgbouncer")
        ]
        if filtered_params:
            database_url = base_url + "?" + "&".join(filtered_params)
        else:
            database_url = base_url

# Aggiungi sslmode=require se non presente (per sicurezza con Supabase/cloud DB)
if database_url.startswith("postgresql") and "sslmode" not in database_url:
    database_url += ("?" if "?" not in database_url else "&") + "sslmode=require"

# Configura connect_args
connect_args = {}
if database_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

# Crea l'engine con pool settings ottimizzati
engine = create_engine(
    database_url,
    connect_args=connect_args,
    pool_pre_ping=True,  # Verifica connessioni prima di usarle
    pool_recycle=300,     # Ricicla connessioni dopo 5 minuti
    pool_size=5,         # Pool size per applicazioni tradizionali
    max_overflow=10,     # Overflow per picchi di traffico
)

# factory per le sessioni
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base per i modelli ORM
Base = declarative_base()
