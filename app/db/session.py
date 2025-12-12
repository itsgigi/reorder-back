# app/db/session.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os

from app.config import settings

# Per Supabase su Vercel/serverless, DEVI usare il Connection Pooler (porta 6543)
# La Direct Connection (porta 5432) NON funziona su Vercel/serverless a causa di problemi IPv6
database_url = settings.DATABASE_URL

# Se è Supabase e usa la porta 5432 (Direct Connection), converti automaticamente a 6543 (Pooler)
if "supabase.co" in database_url and ":5432/" in database_url:
    # ⚠️ ATTENZIONE: Stai usando Direct Connection (5432) che non funziona su Vercel!
    # Convertiamo automaticamente al Connection Pooler (6543)
    database_url = database_url.replace(":5432/", ":6543/")
    # Rimuovi eventuali parametri problematici
    if "?" in database_url:
        params = database_url.split("?")[1]
        if params:
            # Mantieni solo parametri validi, rimuovi pgbouncer e altri problematici
            valid_params = []
            for p in params.split("&"):
                if p and not p.startswith("pgbouncer") and not p.startswith("sslmode"):
                    valid_params.append(p)
            if valid_params:
                database_url = database_url.split("?")[0] + "?" + "&".join(valid_params)
            else:
                database_url = database_url.split("?")[0]
    
    # Aggiungi sslmode=require per sicurezza
    if "?" not in database_url:
        database_url += "?sslmode=require"
    elif "sslmode" not in database_url:
        database_url += "&sslmode=require"

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
