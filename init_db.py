#!/usr/bin/env python3
"""
Script per inizializzare il database PostgreSQL.
Crea tutte le tabelle necessarie per l'applicazione.

Uso:
    python init_db.py

Oppure con DATABASE_URL specificato:
    DATABASE_URL=postgresql://user:pass@host:port/dbname python init_db.py
"""
import os
import sys
import logging
from app.db.session import engine, Base
from app.db.models import Supplier, Product, Invoice, InvoiceLine, ProductPriceHistory
from app.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_database():
    """Inizializza il database creando tutte le tabelle."""
    db_url = settings.DATABASE_URL
    
    logger.info(f"Initializing database: {db_url.split('@')[-1] if '@' in db_url else db_url}")
    
    if db_url.startswith("sqlite"):
        logger.warning("⚠️  Using SQLite. For production, use PostgreSQL!")
    
    try:
        # Crea tutte le tabelle
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables created successfully!")
        
        # Lista delle tabelle create
        tables = [table.name for table in Base.metadata.tables.values()]
        logger.info(f"📋 Created tables: {', '.join(tables)}")
        
        return True
    except Exception as e:
        logger.error(f"❌ Error initializing database: {e}")
        if "could not connect" in str(e).lower():
            logger.error("💡 Check your DATABASE_URL connection string")
            logger.error("   Format: postgresql://user:password@host:port/dbname")
        return False


if __name__ == "__main__":
    success = init_database()
    sys.exit(0 if success else 1)

