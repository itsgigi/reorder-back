# app/db/session.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

from app.config import settings

# Per Supabase su Vercel/serverless, usa il connection pooler invece della connessione diretta
# Il pooler risolve problemi IPv6 e migliora le performance
database_url = settings.DATABASE_URL

# Se è Supabase e non usa già il pooler, converti alla porta del pooler (6543)
if "supabase.co" in database_url and ":5432/" in database_url:
    # Sostituisci la porta 5432 con 6543 (Supabase connection pooler)
    database_url = database_url.replace(":5432/", ":6543/")
    # Aggiungi ?pgbouncer=true per indicare che stiamo usando il pooler
    if "?" not in database_url:
        database_url += "?pgbouncer=true"
    elif "pgbouncer" not in database_url:
        database_url += "&pgbouncer=true"

# Configura connect_args per SQLite
connect_args = {}
if database_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

# Crea l'engine con pool settings ottimizzati per serverless
engine = create_engine(
    database_url,
    connect_args=connect_args,
    # Pool settings per serverless (connessioni brevi)
    pool_pre_ping=True,  # Verifica connessioni prima di usarle
    pool_recycle=300,     # Ricicla connessioni dopo 5 minuti
    pool_size=1,         # Pool minimo per serverless
    max_overflow=0,       # Nessun overflow per serverless
)

# factory per le sessioni
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base per i modelli ORM
Base = declarative_base()
