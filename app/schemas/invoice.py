# app/schemas/invoice.py
from typing import List, Optional
from enum import Enum

from pydantic import BaseModel, Field


class InvoiceLineBase(BaseModel):
    raw_description: str = Field(..., description="Descrizione prodotto così come appare in fattura (SENZA il codice articolo)")
    product_code: Optional[str] = Field(None, description="Codice articolo/fornitore se presente nella colonna 'Cod. articolo'")
    quantity: Optional[float] = Field(None, description="Quantità riga")
    unit_price: Optional[float] = Field(None, description="Prezzo unitario")
    total: Optional[float] = Field(None, description="Totale riga")
    vat_rate: Optional[float] = Field(None, description="Aliquota IVA, se riconosciuta")
    unit_measure: Optional[str] = Field(None, description="Unità di misura (es. kg, pz, L)")
    currency: Optional[str] = Field(None, description="Valuta, es. EUR")


class SupplierInfo(BaseModel):
    name: str
    vat_number: Optional[str] = None
    address: Optional[str] = None


class InvoiceExtraction(BaseModel):
    supplier: SupplierInfo
    invoice_number: Optional[str] = None
    invoice_date: Optional[str] = Field(
        None, description="Data fattura in formato ISO (YYYY-MM-DD) se possibile"
    )
    currency: Optional[str] = None
    total_amount: Optional[float] = Field(None, description="Totale documento comprensivo di IVA (campo 'Totale documento' nella fattura)")
    lines: List[InvoiceLineBase]
    raw_text: Optional[str] = Field(
        None,
        description="Testo completo AI (json raw) per debug / rielaborazioni"
    )


# === Modelli per risposta API di import ===

class LineMatchStatus(str, Enum):
    matched = "matched"
    unmatched = "unmatched"


class InvoiceLineWithMatch(InvoiceLineBase):
    deterministic_product_id: Optional[int] = None
    deterministic_product_label: Optional[str] = None
    match_status: LineMatchStatus = LineMatchStatus.unmatched


class InvoiceImportResponse(BaseModel):
    invoice_id: Optional[int] = None  # se in futuro la salvi già
    supplier_id: int  # ID del fornitore creato/trovato nel DB
    supplier: SupplierInfo
    invoice_number: Optional[str]
    invoice_date: Optional[str]
    currency: Optional[str]
    total_amount: Optional[float] = None  # Totale documento comprensivo di IVA
    lines: List[InvoiceLineWithMatch]

class InvoiceListItem(BaseModel):
    id: int
    supplier_name: str
    invoice_number: Optional[str]
    invoice_date: Optional[str]
    currency: Optional[str]
    total_amount: Optional[float]

class DashboardSummary(BaseModel):
    total_invoices: int
    total_amount: float
    total_products: int


# === Modelli per dettaglio fattura ===

class InvoiceLineDetail(BaseModel):
    id: int
    raw_description: str
    product_code: Optional[str] = None
    quantity: Optional[float] = None
    unit_price: Optional[float] = None
    total: Optional[float] = None
    vat_rate: Optional[float] = None
    currency: Optional[str] = None
    product_id: Optional[int] = None
    product_name: Optional[str] = None
    product_internal_code: Optional[str] = None  # Nota: campo non presente nel modello Product attuale
    um: Optional[str] = Field(None, description="Unità di misura (da unit_measure della riga o del prodotto)")

    class Config:
        from_attributes = True


class InvoiceDetail(BaseModel):
    id: int
    supplier: SupplierInfo
    invoice_number: Optional[str] = None
    invoice_date: Optional[str] = None
    currency: Optional[str] = None
    total_amount: Optional[float] = None
    lines: List[InvoiceLineDetail]

    class Config:
        from_attributes = True
