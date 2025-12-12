from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from typing import List
from app.schemas.product import Product as ProductSchema, ProductDetail, PriceHistoryEntry, MergeProductRequest, MergeProductResponse, PriceVariation
from app.schemas.invoice import InvoiceListItem, InvoiceImportResponse, DashboardSummary, InvoiceDetail, InvoiceLineDetail, SupplierInfo
from app.db.models import Invoice, InvoiceLine, Product, Supplier, ProductPriceHistory
from datetime import date
from app.schemas.confirm_invoice import (
    ConfirmInvoiceRequest,
    ConfirmInvoiceResponse,
)
from app.deps import get_db
from app.services.invoice_extractor import DatapizzaInvoiceExtractor
from app.services.matching import (
    get_or_create_supplier,
    deterministic_match_all_lines,
    find_matching_product,
)
from sqlalchemy import func


router = APIRouter()

extractor = DatapizzaInvoiceExtractor()


@router.get("/health")
def health_check():
    return {"status": "ok"}


@router.post("/invoices/import", response_model=InvoiceImportResponse)
async def import_invoice(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    """
    1) Riceve una fattura (PDF/immagine)
    2) Usa Datapizza per estrarre dati strutturati
    3) Fa un primo matching deterministico con i prodotti a DB
    4) Ritorna al frontend i dati + info di match
    """
    file_bytes = await file.read()
    # estensione dal nome file, es "fattura.pdf" -> "pdf"
    mime_ext = file.filename.split(".")[-1].lower()

    # 2) Estrazione AI
    extraction = extractor.extract_from_bytes(file_bytes, mime_ext)

    # 3) Fornitore
    supplier = get_or_create_supplier(db, extraction.supplier.name)

    # 4) Matching deterministico sulle righe
    lines_with_match = deterministic_match_all_lines(db, extraction)

    # 5) Costruisci risposta
    response = InvoiceImportResponse(
        invoice_id=None,  # in futuro potrai salvare subito un draft
        supplier_id=supplier.id,  # ID del fornitore creato/trovato
        supplier=extraction.supplier,
        invoice_number=extraction.invoice_number,
        invoice_date=extraction.invoice_date,
        currency=extraction.currency,
        total_amount=extraction.total_amount,  # Totale documento dall'estrazione
        lines=lines_with_match,
    )

    return response

@router.post("/invoices/confirm", response_model=ConfirmInvoiceResponse)
def confirm_invoice(
    payload: ConfirmInvoiceRequest,
    db: Session = Depends(get_db),
):
    """
    Salva in DB una fattura confermata dall'utente (dopo il refine sul frontend).
    """
    # Usa il totale documento se fornito, altrimenti calcola dalla somma delle righe
    # Nota: in futuro il total_amount potrebbe venire dal payload stesso
    total_amount = sum(line.total for line in payload.lines)

    inv = Invoice(
        supplier_id=payload.supplier_id,
        invoice_number=payload.invoice_number,
        invoice_date=date.fromisoformat(payload.invoice_date),
        currency=payload.currency,
        total_amount=total_amount,
        file_path=payload.file_path,
    )
    db.add(inv)
    db.flush()  # così otteniamo inv.id senza commit

    for line in payload.lines:
        # Estrai il product_code dalla riga (se presente)
        product_code = line.product_code
        
        # Usa il product_id se fornito (dalla fase di matching/refinement frontend)
        final_product_id = line.product_id
        
        # Se c'è un product_id, verifica se il prodotto esiste e aggiorna il product_code se necessario
        if final_product_id:
            existing_prod = db.query(Product).filter(Product.id == final_product_id).first()
            if existing_prod:
                # Aggiorna il product_code se presente nella riga fattura e mancante nel prodotto
                if product_code and (not existing_prod.product_code or existing_prod.product_code.strip() == ""):
                    existing_prod.product_code = product_code
                    db.flush()
        
        # Se non c'è product_id, cerca un prodotto esistente con matching intelligente
        # Questo evita la creazione di duplicati quando le descrizioni sono simili
        if final_product_id is None and line.raw_description:
            # Usa product_code se disponibile per un match più affidabile
            existing_prod = find_matching_product(db, line.raw_description, product_code=product_code)
            if existing_prod:
                # Trovato un prodotto esistente che matcha
                final_product_id = existing_prod.id
                # Aggiorna il product_code se presente nella riga fattura e mancante nel prodotto
                # Questo assicura che i prodotti esistenti vengano arricchiti con il codice quando disponibile
                if product_code and (not existing_prod.product_code or existing_prod.product_code.strip() == ""):
                    existing_prod.product_code = product_code
                    db.flush()
                # Opzionale: aggiorna prezzo/UM se mancanti? Per ora no.
            else:
                # Nessun match trovato, crea un nuovo prodotto
                new_prod = Product(
                    product_code=product_code,
                    name=line.raw_description,
                    unit_price=line.unit_price,
                    unit_measure=line.unit_measure,
                )
                db.add(new_prod)
                db.flush()
                final_product_id = new_prod.id

        db_line = InvoiceLine(
            invoice_id=inv.id,
            raw_description=line.raw_description,
            product_code=product_code,
            quantity=line.quantity,
            unit_price=line.unit_price,
            total=line.total,
            vat_rate=line.vat_rate,
            unit_measure=line.unit_measure,
            product_id=final_product_id,
            cost_center_id=line.cost_center_id,
        )
        db.add(db_line)

        # Salva lo storico dei prezzi se il prodotto è stato matchato
        if final_product_id is not None and line.unit_price is not None:
            price_history = ProductPriceHistory(
                product_id=final_product_id,
                invoice_id=inv.id,
                price_date=inv.invoice_date,
                unit_price=line.unit_price,
                quantity=line.quantity,
                unit_measure=line.unit_measure,
                total=line.total,
                currency=inv.currency,
            )
            db.add(price_history)

    db.commit()
    db.refresh(inv)

    return ConfirmInvoiceResponse(invoice_id=inv.id)

@router.get("/invoices", response_model=List[InvoiceListItem])
def list_invoices(db: Session = Depends(get_db)):
    """
    Ritorna la lista delle fatture salvate, per la dashboard.
    """
    rows = (
        db.query(Invoice, Supplier)
        .join(Supplier, Invoice.supplier_id == Supplier.id)
        .order_by(Invoice.invoice_date.desc().nullslast(), Invoice.id.desc())
        .all()
    )

    result: list[InvoiceListItem] = []
    for inv, sup in rows:
        result.append(
            InvoiceListItem(
                id=inv.id,
                supplier_name=sup.name,
                invoice_number=inv.invoice_number,
                invoice_date=inv.invoice_date.isoformat() if inv.invoice_date else None,
                currency=inv.currency,
                total_amount=inv.total_amount,
            )
        )

    return result

@router.get("/dashboard/summary", response_model=DashboardSummary)
def dashboard_summary(db: Session = Depends(get_db)):
    """
    Stats base per la dashboard.
    """
    total_invoices = db.query(func.count(Invoice.id)).scalar() or 0
    total_amount = db.query(func.coalesce(func.sum(Invoice.total_amount), 0)).scalar() or 0.0
    total_products = db.query(func.count(Product.id)).scalar() or 0

    return DashboardSummary(
        total_invoices=total_invoices,
        total_amount=total_amount,
        total_products=total_products,
    )

@router.get("/products", response_model=List[ProductSchema])
def list_products(db: Session = Depends(get_db)):
    """
    Ritorna la lista completa di tutti i prodotti registrati.
    Include l'ultima variazione di prezzo se presente.
    """
    products = (
        db.query(Product)
        .options(joinedload(Product.price_history))
        .order_by(Product.id)
        .all()
    )
    
    result: list[ProductSchema] = []
    for product in products:
        # Calcola la variazione di prezzo se ci sono almeno 2 prezzi nello storico
        variazione = None
        if product.price_history and len(product.price_history) >= 2:
            # Ordina lo storico per data (più recente prima)
            sorted_history = sorted(
                product.price_history,
                key=lambda x: x.price_date if x.price_date else date.min,
                reverse=True
            )
            
            # Prendi gli ultimi due prezzi
            current_price_entry = sorted_history[0]
            previous_price_entry = sorted_history[1]
            
            current_price = current_price_entry.unit_price
            previous_price = previous_price_entry.unit_price
            
            if current_price is not None and previous_price is not None and previous_price != 0:
                absolute_change = current_price - previous_price
                percentage_change = (absolute_change / previous_price) * 100
                
                variazione = PriceVariation(
                    previous_price=previous_price,
                    current_price=current_price,
                    absolute_change=absolute_change,
                    percentage_change=percentage_change,
                    variation_date=current_price_entry.price_date.isoformat() if current_price_entry.price_date else ""
                )
        
        result.append(
            ProductSchema(
                id=product.id,
                product_code=product.product_code,
                name=product.name,
                unit_price=product.unit_price,
                variazione=variazione
            )
        )
    
    return result


@router.get("/products/{product_id}", response_model=ProductDetail)
def get_product_detail(product_id: int, db: Session = Depends(get_db)):
    """
    Recupera i dettagli completi di un prodotto specifico, inclusa la storia dei prezzi.
    Mostra l'andamento del prezzo nel tempo per permettere l'analisi delle variazioni.
    """
    product = (
        db.query(Product)
        .options(
            joinedload(Product.price_history)
        )
        .filter(Product.id == product_id)
        .first()
    )

    if not product:
        raise HTTPException(status_code=404, detail="Prodotto non trovato")

    # Ordina lo storico per data (più recente prima)
    price_history = sorted(
        product.price_history,
        key=lambda x: x.price_date if x.price_date else date.min,
        reverse=True
    )

    # Converti lo storico in schema Pydantic
    history_entries = [
        PriceHistoryEntry(
            id=h.id,
            invoice_id=h.invoice_id,
            price_date=h.price_date.isoformat() if h.price_date else "",
            unit_price=h.unit_price,
            quantity=h.quantity,
            unit_measure=h.unit_measure,
            total=h.total,
            currency=h.currency,
        )
        for h in price_history
    ]

    return ProductDetail(
        id=product.id,
        name=product.name,
        unit_price=product.unit_price,
        unit_measure=product.unit_measure,
        price_history=history_entries,
    )


@router.get("/invoices/{invoice_id}", response_model=InvoiceDetail)
def get_invoice_detail(invoice_id: int, db: Session = Depends(get_db)):
    """
    Recupera i dettagli completi di una fattura specifica.
    Include informazioni fornitore, dati fattura e tutte le righe con dettagli prodotto se collegato.
    """
    # Recupera la fattura con supplier e lines (eager loading per evitare query N+1)
    invoice = (
        db.query(Invoice)
        .options(
            joinedload(Invoice.supplier),
            joinedload(Invoice.lines).joinedload(InvoiceLine.product)
        )
        .filter(Invoice.id == invoice_id)
        .first()
    )

    if not invoice:
        raise HTTPException(status_code=404, detail="Fattura non trovata")

    # Carica esplicitamente supplier e lines se non già caricati
    supplier = invoice.supplier
    lines = invoice.lines

    # Costruisci le righe dettagliate
    detail_lines: List[InvoiceLineDetail] = []
    for line in lines:
        product_name = None
        product_internal_code = None
        
        # Se la riga ha un prodotto collegato, recupera le informazioni
        if line.product_id and line.product:
            product_name = line.product.name
            # Nota: product_internal_code non esiste nel modello Product attuale
            # Restituiamo None per ora
            product_internal_code = None
        
        # Unità di misura: preferisci quella della riga, altrimenti quella del prodotto
        um = line.unit_measure
        if not um and line.product_id and line.product:
            um = line.product.unit_measure

        detail_lines.append(
            InvoiceLineDetail(
                id=line.id,
                raw_description=line.raw_description,
                product_code=line.product_code,
                quantity=line.quantity,
                unit_price=line.unit_price,
                total=line.total,
                vat_rate=line.vat_rate,
                currency=invoice.currency,  # La valuta è a livello di fattura
                product_id=line.product_id,
                product_name=product_name,
                product_internal_code=product_internal_code,
                um=um,
            )
        )

    # Costruisci la risposta
    return InvoiceDetail(
        id=invoice.id,
        supplier=SupplierInfo(
            name=supplier.name,
            vat_number=supplier.vat_number,
            address=supplier.address,
        ),
        invoice_number=invoice.invoice_number,
        invoice_date=invoice.invoice_date.isoformat() if invoice.invoice_date else None,
        currency=invoice.currency,
        total_amount=invoice.total_amount,
        lines=detail_lines,
    )


@router.delete("/invoices/{invoice_id}")
def delete_invoice(invoice_id: int, db: Session = Depends(get_db)):
    """
    Elimina una fattura dal sistema.
    Le righe associate verranno eliminate automaticamente grazie al cascade.
    """
    invoice = db.query(Invoice).filter(Invoice.id == invoice_id).first()

    if not invoice:
        raise HTTPException(status_code=404, detail="Fattura non trovata")

    try:
        db.delete(invoice)
        db.commit()
        return {"success": True}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Errore durante l'eliminazione della fattura: {str(e)}")


@router.post("/products/{source_product_id}/merge", response_model=MergeProductResponse)
def merge_products(
    source_product_id: int,
    request: MergeProductRequest,
    db: Session = Depends(get_db),
):
    """
    Unisce un prodotto sorgente con un prodotto destinazione.
    - Aggiorna tutte le invoice_lines che puntano al prodotto sorgente
    - Sposta lo storico prezzi dal prodotto sorgente a quello destinazione
    - Elimina il prodotto sorgente
    
    L'operazione è atomica: se qualsiasi parte fallisce, tutte le modifiche vengono annullate.
    """
    target_product_id = request.target_product_id

    # Validazione 1: Verifica non auto-merge
    if source_product_id == target_product_id:
        raise HTTPException(
            status_code=409,
            detail="Non è possibile unire un prodotto con se stesso"
        )

    # Validazione 2: Verifica esistenza prodotti
    source_product = db.query(Product).filter(Product.id == source_product_id).first()
    target_product = db.query(Product).filter(Product.id == target_product_id).first()

    if not source_product:
        raise HTTPException(
            status_code=404,
            detail="Prodotto sorgente non trovato"
        )
    
    if not target_product:
        raise HTTPException(
            status_code=404,
            detail="Prodotto destinazione non trovato"
        )

    try:
        # Inizia transazione atomica
        # 1. Aggiorna tutte le invoice_lines che puntano al prodotto sorgente
        updated_lines = (
            db.query(InvoiceLine)
            .filter(InvoiceLine.product_id == source_product_id)
            .update({"product_id": target_product_id}, synchronize_session=False)
        )

        # 2. Aggiorna tutte le voci dello storico prezzi
        updated_history = (
            db.query(ProductPriceHistory)
            .filter(ProductPriceHistory.product_id == source_product_id)
            .update({"product_id": target_product_id}, synchronize_session=False)
        )

        # 3. Elimina il prodotto sorgente
        # Le relazioni con invoice_lines e price_history sono già state aggiornate,
        # quindi possiamo eliminare il prodotto in sicurezza
        db.delete(source_product)

        # Commit della transazione
        db.commit()

        return MergeProductResponse(
            success=True,
            message=f"Prodotto unito con successo. Aggiornate {updated_lines} righe fattura e {updated_history} voci di storico prezzi."
        )

    except Exception as e:
        # Rollback in caso di errore
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Errore durante l'unione dei prodotti: {str(e)}"
        )
