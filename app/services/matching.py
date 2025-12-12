# app/services/matching.py
import re
from typing import Optional
from sqlalchemy.orm import Session

from app.db.models import Supplier, Product  # per ora solo Product
from app.schemas.invoice import (
    InvoiceExtraction,
    InvoiceLineWithMatch,
    LineMatchStatus,
)


def get_or_create_supplier(db: Session, supplier_name: str) -> Supplier:
    supplier = db.query(Supplier).filter(Supplier.name == supplier_name).first()
    if supplier:
        return supplier
    supplier = Supplier(name=supplier_name)
    db.add(supplier)
    db.commit()
    db.refresh(supplier)
    return supplier


def normalize_description(description: str) -> str:
    """
    Normalizza una descrizione prodotto per il matching:
    - Rimuove parti variabili come "Tipo dato:XXX", "Rif. testo:YYY"
    - Rimuove spazi multipli
    - Converti in lowercase
    - Rimuove caratteri speciali ai margini
    """
    if not description:
        return ""
    
    # Rimuovi parti variabili comuni che cambiano tra fatture diverse
    # Es: "Tipo dato:PDC Rif. testo:3145HOTEL OLIMPIA SRL"
    cleaned = description
    cleaned = re.sub(r'\s*Tipo\s+dato\s*:.*?(\s|$)', ' ', cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r'\s*Rif\.?\s*testo\s*:.*?(\s|$)', ' ', cleaned, flags=re.IGNORECASE)
    
    # Rimuovi spazi multipli e normalizza
    normalized = re.sub(r'\s+', ' ', cleaned.strip())
    return normalized.lower()


def extract_product_code(description: str) -> str:
    """
    Estrae il codice prodotto dalla descrizione.
    Cerca pattern comuni come numeri all'inizio (es: "0025650.01" o "12345")
    """
    if not description:
        return ""
    
    # Cerca pattern tipo: numero con punto opzionale (es: "0025650.01" o "12345")
    # Match all'inizio della stringa
    match = re.match(r'^(\d+(?:\.\d+)?)', description.strip())
    if match:
        return match.group(1)
    return ""


def find_matching_product(db: Session, raw_description: str, product_code: Optional[str] = None) -> Optional[Product]:
    """
    Cerca un prodotto esistente che matcha la descrizione.
    Usa più criteri di matching con priorità:
    1. Match deterministico su codice prodotto (se fornito) - PRIORITARIO
       - Cerca prima sul campo product_code del prodotto
       - Fallback sul nome se product_code non è presente nel DB
    2. Match esatto sul nome (case-insensitive)
    3. Match su codice prodotto estratto dalla descrizione (se presente)
    4. Match su parte iniziale normalizzata (primi 50 caratteri)
    """
    if not raw_description and not product_code:
        return None
    
    # 1. Match deterministico su codice prodotto (se fornito esplicitamente)
    # Questo è il check deterministico più affidabile
    if product_code:
        # PRIORITÀ 1: Match esatto sul campo product_code del prodotto
        product = db.query(Product).filter(
            Product.product_code == product_code
        ).first()
        
        if product:
            return product
        
        # PRIORITÀ 2: Fallback - cerca prodotti che iniziano con lo stesso codice nel nome
        # (per retrocompatibilità con prodotti vecchi che hanno il codice nel nome)
        products = db.query(Product).filter(
            Product.name.ilike(f"{product_code}%")
        ).all()
        
        if products:
            # Se c'è più di un match, preferisci quello con descrizione più simile
            # Per ora prendi il primo, ma potresti implementare un algoritmo di similarità
            return products[0]
    
    # Normalizza la descrizione
    normalized = normalize_description(raw_description) if raw_description else ""
    extracted_code = extract_product_code(raw_description) if raw_description else None
    
    # 2. Match esatto sul nome (case-insensitive)
    if raw_description:
        product = db.query(Product).filter(
            Product.name.ilike(raw_description)
        ).first()
        
        if product:
            return product
    
    # 3. Match su codice prodotto estratto dalla descrizione (se presente e non già usato)
    if extracted_code and extracted_code != product_code:
        # Prova prima sul campo product_code
        product = db.query(Product).filter(
            Product.product_code == extracted_code
        ).first()
        
        if product:
            return product
        
        # Fallback sul nome
        products = db.query(Product).filter(
            Product.name.ilike(f"{extracted_code}%")
        ).all()
        
        if products:
            return products[0]
    
    # 4. Match su parte iniziale normalizzata (primi caratteri significativi)
    # Rimuove codici e parti comuni, prende i primi 100 caratteri per il matching
    if normalized:
        significant_part = normalized[:100] if len(normalized) > 100 else normalized
        if len(significant_part) > 20:  # Almeno 20 caratteri per evitare match troppo generici
            # Cerca prodotti che contengono questa parte significativa
            # o che hanno una parte iniziale simile
            products = db.query(Product).all()
            for prod in products:
                prod_normalized = normalize_description(prod.name)
                # Se la parte significativa è contenuta nel prodotto esistente o viceversa
                if significant_part in prod_normalized or prod_normalized in significant_part:
                    # Verifica che non sia un match troppo generico (almeno 20 caratteri comuni)
                    common_length = min(len(significant_part), len(prod_normalized))
                    if common_length >= 20:
                        return prod
    
    return None


def deterministic_match_line(db: Session, line: InvoiceLineWithMatch) -> InvoiceLineWithMatch:
    """
    Cerca di matchare una riga fattura con un prodotto esistente.
    Usa criteri multipli con priorità:
    1. Match deterministico su codice prodotto (se presente) - PRIORITARIO
    2. Match esatto, codice prodotto estratto, parte iniziale normalizzata
    """
    # Usa il codice articolo se disponibile per un match deterministico più affidabile
    product = find_matching_product(db, line.raw_description, product_code=line.product_code)

    if product:
        line.deterministic_product_id = product.id
        line.deterministic_product_label = product.name
        line.match_status = LineMatchStatus.matched
    else:
        line.match_status = LineMatchStatus.unmatched

    return line


def deterministic_match_all_lines(db: Session, extraction: InvoiceExtraction):
    """
    Trasforma le InvoiceLineBase in InvoiceLineWithMatch e applica il matching.
    """
    lines_with_match: list[InvoiceLineWithMatch] = []

    for l in extraction.lines:
        line = InvoiceLineWithMatch(**l.dict())
        line = deterministic_match_line(db, line)
        lines_with_match.append(line)

    return lines_with_match
