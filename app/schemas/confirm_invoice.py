# app/schemas/confirm_invoice.py
from typing import List, Optional
from pydantic import BaseModel


class ConfirmInvoiceLine(BaseModel):
    raw_description: str
    product_code: Optional[str] = None
    quantity: float
    unit_price: float
    total: float
    vat_rate: Optional[float] = None
    unit_measure: Optional[str] = None
    product_id: Optional[int] = None
    cost_center_id: Optional[int] = None


class ConfirmInvoiceRequest(BaseModel):
    supplier_id: int
    invoice_number: str
    invoice_date: str  # YYYY-MM-DD
    currency: str = "EUR"
    lines: List[ConfirmInvoiceLine]
    file_path: Optional[str] = None  # se salvi il pdf da qualche parte


class ConfirmInvoiceResponse(BaseModel):
    invoice_id: int
