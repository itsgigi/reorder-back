#!/usr/bin/env python3
"""
Script di migrazione per aggiungere la colonna product_code alla tabella invoice_lines.
Esegui questo script una volta per aggiornare il database esistente.
"""
import sqlite3
from pathlib import Path

# Path al database
db_path = Path(__file__).parent / "reorder.db"

if not db_path.exists():
    print(f"Database non trovato: {db_path}")
    exit(1)

print(f"Connessione al database: {db_path}")
conn = sqlite3.connect(str(db_path))
cursor = conn.cursor()

# Verifica se la colonna esiste già
cursor.execute("PRAGMA table_info(invoice_lines)")
columns = [col[1] for col in cursor.fetchall()]

if "product_code" in columns:
    print("La colonna product_code esiste già. Migrazione non necessaria.")
    conn.close()
    exit(0)

# Aggiungi la colonna product_code
print("Aggiunta colonna product_code alla tabella invoice_lines...")
try:
    cursor.execute("""
        ALTER TABLE invoice_lines 
        ADD COLUMN product_code VARCHAR(100)
    """)
    
    # Crea un indice per migliorare le performance del matching
    print("Creazione indice su product_code...")
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS ix_invoice_lines_product_code 
        ON invoice_lines(product_code)
    """)
    
    conn.commit()
    print("✓ Migrazione completata con successo!")
    print("  - Colonna product_code aggiunta")
    print("  - Indice creato su product_code")
    
except sqlite3.Error as e:
    conn.rollback()
    print(f"✗ Errore durante la migrazione: {e}")
    exit(1)
finally:
    conn.close()

