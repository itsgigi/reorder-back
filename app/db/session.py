# app/db/session.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

from app.config import settings

# Per Supabase su Vercel/serverless, usa il connection pooler invece della connessione diretta
# Il pooler risolve problemi IPv6 e migliora le performance
database_url = settings.DATABASE_URL

# Se è Supabase e non usa già il pooler, converti alla porta del pooler (6543)
# Il pooler risolve problemi IPv6 e migliora le performance su serverless
if "supabase.co" in database_url and ":5432/" in database_url:
    # Sostituisci la porta 5432 con 6543 (Supabase connection pooler)
    database_url = database_url.replace(":5432/", ":6543/")
    # Rimuovi eventuali parametri pgbouncer (psycopg2 non li riconosce)
    # Il pooler funziona comunque senza parametri espliciti
    if "?" in database_url:
        params = database_url.split("?")[1]
        if params:
            # Rimuovi solo pgbouncer, mantieni altri parametri
            param_list = [p for p in params.split("&") if not p.startswith("pgbouncer")]
            if param_list:
                database_url = database_url.split("?")[0] + "?" + "&".join(param_list)
            else:
                database_url = database_url.split("?")[0]

# Configura connect_args per SQLite e PostgreSQL
connect_args = {}
if database_url.startswith("sqlite"):
    connect_args = {"check_same_thread": False}
elif database_url.startswith("postgresql"):
    # Forza IPv4 per evitare problemi su Vercel/serverless che non supporta IPv6
    # Risolvi il dominio a IPv4 prima della connessione
    import socket
    try:
        # Estrai l'host dalla connection string
        if "@" in database_url and ":" in database_url.split("@")[1]:
            host_part = database_url.split("@")[1].split(":")[0].split("/")[0]
            # Risolvi a IPv4
            ipv4 = socket.gethostbyname(host_part)
            # Sostituisci l'host con l'IP IPv4 nella connection string
            if host_part in database_url:
                database_url = database_url.replace(f"@{host_part}", f"@{ipv4}")
                # Aggiungi il parametro hostname per mantenere il SNI
                if "?" not in database_url:
                    database_url += f"?host={host_part}"
                else:
                    database_url += f"&host={host_part}"
    except Exception as e:
        # Se la risoluzione fallisce, continua con il dominio originale
        # e aggiungi parametri per forzare IPv4
        pass
    
    # Aggiungi parametri per forzare IPv4 se non già presenti
    if "?" not in database_url:
        database_url += "?connect_timeout=10"
    elif "connect_timeout" not in database_url:
        database_url += "&connect_timeout=10"

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
