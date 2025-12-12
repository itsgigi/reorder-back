# app/db/models.py
from sqlalchemy import Column, Integer, String, Date, Float, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.db.session import Base


class Supplier(Base):
    __tablename__ = "suppliers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, index=True, nullable=False)
    vat_number = Column(String(50), nullable=True)
    address = Column(Text, nullable=True)

    invoices = relationship("Invoice", back_populates="supplier")


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    product_code = Column(String(100), nullable=True, index=True)  # Codice articolo/fornitore per matching deterministico
    name = Column(String(255), nullable=False)
    unit_price = Column(Float, nullable=True)
    unit_measure = Column(String(50), nullable=True)  # Mantenuto per retrocompatibilità ma non più esposto nell'API

    invoice_lines = relationship("InvoiceLine", back_populates="product")
    price_history = relationship("ProductPriceHistory", back_populates="product", cascade="all, delete-orphan")


class Invoice(Base):
    __tablename__ = "invoices"

    id = Column(Integer, primary_key=True, index=True)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=False)
    invoice_number = Column(String(100), index=True, nullable=True)
    invoice_date = Column(Date, nullable=True)
    currency = Column(String(10), nullable=True)
    total_amount = Column(Float, nullable=True)
    file_path = Column(String(500), nullable=True)  # dove salvi pdf/immagine

    supplier = relationship("Supplier", back_populates="invoices")
    lines = relationship("InvoiceLine", back_populates="invoice", cascade="all, delete-orphan")


class InvoiceLine(Base):
    __tablename__ = "invoice_lines"

    id = Column(Integer, primary_key=True, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=False)
    raw_description = Column(Text, nullable=False)
    product_code = Column(String(100), nullable=True, index=True)  # Codice articolo/fornitore per matching deterministico
    quantity = Column(Float, nullable=True)
    unit_price = Column(Float, nullable=True)
    total = Column(Float, nullable=True)
    vat_rate = Column(Float, nullable=True)
    unit_measure = Column(String(50), nullable=True)

    product_id = Column(Integer, ForeignKey("products.id"), nullable=True)
    cost_center_id = Column(Integer, nullable=True)  # per ora solo int, in futuro tabella cost_centers

    invoice = relationship("Invoice", back_populates="lines")
    product = relationship("Product", back_populates="invoice_lines")


class ProductPriceHistory(Base):
    __tablename__ = "product_price_history"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    invoice_id = Column(Integer, ForeignKey("invoices.id"), nullable=False, index=True)
    price_date = Column(Date, nullable=False, index=True)
    unit_price = Column(Float, nullable=False)
    quantity = Column(Float, nullable=True)
    unit_measure = Column(String(50), nullable=True)
    total = Column(Float, nullable=True)
    currency = Column(String(10), nullable=True)

    product = relationship("Product", back_populates="price_history")
    invoice = relationship("Invoice")
