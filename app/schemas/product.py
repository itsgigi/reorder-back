from typing import Optional, List
from pydantic import BaseModel


class PriceVariation(BaseModel):
    """Informazioni sulla variazione di prezzo più recente"""
    previous_price: float
    current_price: float
    absolute_change: float  # differenza assoluta (current - previous)
    percentage_change: float  # variazione percentuale
    variation_date: str  # data della variazione (formato ISO YYYY-MM-DD)

    class Config:
        from_attributes = True


class Product(BaseModel):
    id: int
    product_code: Optional[str] = None  # Codice articolo/fornitore
    name: str
    unit_price: Optional[float] = None
    variazione: Optional[PriceVariation] = None  # ultima variazione di prezzo se presente

    class Config:
        from_attributes = True


class PriceHistoryEntry(BaseModel):
    """Singola voce dello storico prezzi di un prodotto"""
    id: int
    invoice_id: int
    price_date: str  # formato ISO (YYYY-MM-DD)
    unit_price: float
    quantity: Optional[float] = None
    unit_measure: Optional[str] = None
    total: Optional[float] = None
    currency: Optional[str] = None

    class Config:
        from_attributes = True


class ProductDetail(BaseModel):
    """Dettaglio completo di un prodotto con storico prezzi"""
    id: int
    name: str
    unit_price: Optional[float] = None
    unit_measure: Optional[str] = None
    price_history: List[PriceHistoryEntry] = []

    class Config:
        from_attributes = True


class MergeProductRequest(BaseModel):
    """Richiesta per unire un prodotto sorgente con uno destinazione"""
    target_product_id: int


class MergeProductResponse(BaseModel):
    """Risposta per l'unione di prodotti"""
    success: bool
    message: str

