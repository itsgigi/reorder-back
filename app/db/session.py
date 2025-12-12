# app/db/session.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

from app.config import settings

# Per Supabase su Vercel/serverless, DEVI usare il Connection Pooler (porta 6543)
# La Direct Connection (porta 5432) NON funziona su Vercel/serverless a causa di problemi IPv6
database_url = settings.DATABASE_URL

# Pulisci la connection string da parametri non supportati da psycopg2
# Rimuovi SEMPRE pgbouncer=true (psycopg2 non lo riconosce)
# Il pooler funziona comunque senza questo parametro
if "?" in database_url:
    base_url, params = database_url.split("?", 1)
    if params:
        # Rimuovi tutti i parametri pgbouncer (qualsiasi variante)
        # Es: pgbouncer=true, pgbouncer=false, pgbouncer=1, etc.
        filtered_params = []
        for param in params.split("&"):
            param = param.strip()
            if not param:
                continue
            # Rimuovi qualsiasi parametro che inizia con "pgbouncer"
            if param.lower().startswith("pgbouncer"):
                continue  # psycopg2 non supporta pgbouncer
            # Mantieni altri parametri validi
            filtered_params.append(param)
        
        # Ricostruisci la connection string
        if filtered_params:
            database_url = base_url + "?" + "&".join(filtered_params)
        else:
            database_url = base_url

# Se è Supabase e usa la porta 5432 (Direct Connection), converti automaticamente a 6543 (Pooler)
if "supabase.co" in database_url and ":5432/" in database_url:
    # ⚠️ ATTENZIONE: Stai usando Direct Connection (5432) che non funziona su Vercel!
    # Convertiamo automaticamente al Connection Pooler (6543)
    database_url = database_url.replace(":5432/", ":6543/")

# Aggiungi sslmode=require se non presente (per sicurezza)
if database_url.startswith("postgresql") and "sslmode" not in database_url:
    if "?" not in database_url:
        database_url += "?sslmode=require"
    else:
        database_url += "&sslmode=require"

# Configura connect_args per SQLite
connect_args = {}
if database_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}
# Per PostgreSQL, non serve configurare connect_args speciali
# La connection string contiene già tutti i parametri necessari

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
