# Esempi API - Modifiche Backend

## 📄 Esempio Response `/api/invoices/import`

### Prima (vecchia versione)
```json
{
  "invoice_id": null,
  "supplier_id": 1,
  "supplier": {
    "name": "DAC SPA",
    "vat_number": "IT03038290171",
    "address": "VIA AVEZZANO..."
  },
  "invoice_number": "Q__/168507",
  "invoice_date": "2025-10-27",
  "currency": "EUR",
  "lines": [
    {
      "raw_description": "0015179.01 - B.A. CAMPANELLO S/V F Tipo dato: PDC Rif. testo: 3145HOTEL OLIMPIA SRL",
      "quantity": 1.9,
      "unit_price": 11.5,
      "total": 21.85,
      "vat_rate": 10.0,
      "unit_measure": "KG",
      "currency": "EUR",
      "deterministic_product_id": null,
      "deterministic_product_label": null,
      "match_status": "unmatched"
    }
  ]
}
```

### Dopo (nuova versione) ⭐
```json
{
  "invoice_id": null,
  "supplier_id": 1,
  "supplier": {
    "name": "DAC SPA",
    "vat_number": "IT03038290171",
    "address": "VIA AVEZZANO..."
  },
  "invoice_number": "Q__/168507",
  "invoice_date": "2025-10-27",
  "currency": "EUR",
  "total_amount": 355.72,  // ⭐ NUOVO: Totale documento comprensivo di IVA
  "lines": [
    {
      "raw_description": "B.A. CAMPANELLO S/V F Tipo dato: PDC Rif. testo: 3145HOTEL OLIMPIA SRL",  // ⚠️ MODIFICATO: senza codice articolo
      "product_code": "0015179.01",  // ⭐ NUOVO: Codice articolo separato
      "quantity": 1.9,
      "unit_price": 11.5,
      "total": 21.85,
      "vat_rate": 10.0,
      "unit_measure": "KG",
      "currency": "EUR",
      "deterministic_product_id": 42,
      "deterministic_product_label": "B.A. CAMPANELLO S/V F",
      "match_status": "matched"  // ✅ Match migliorato grazie a product_code
    },
    {
      "raw_description": "SPALLA SUINO S/O S/C CEE S/V FR Tipo dato: PDC Rif. testo: 3145HOTEL OLIMPIA SRL",
      "product_code": "0015904.01",
      "quantity": 11.8,
      "unit_price": 4.95,
      "total": 58.41,
      "vat_rate": 10.0,
      "unit_measure": "KG",
      "currency": "EUR",
      "deterministic_product_id": null,
      "deterministic_product_label": null,
      "match_status": "unmatched"
    },
    {
      "raw_description": "PAVESINI CLASSICI GR.200 Tipo dato: PDC Rif. testo: 3145HOTEL OLIMPIA SRL",
      "product_code": "0005386.01",
      "quantity": 12.0,
      "unit_price": 2.71,
      "total": 32.52,
      "vat_rate": 10.0,
      "unit_measure": "PZ",
      "currency": "EUR",
      "deterministic_product_id": null,
      "deterministic_product_label": null,
      "match_status": "unmatched"
    }
  ]
}
```

---

## 📄 Esempio Request `/api/invoices/confirm`

### Prima (vecchia versione)
```json
{
  "supplier_id": 1,
  "invoice_number": "Q__/168507",
  "invoice_date": "2025-10-27",
  "currency": "EUR",
  "lines": [
    {
      "raw_description": "0015179.01 - B.A. CAMPANELLO S/V F...",
      "quantity": 1.9,
      "unit_price": 11.5,
      "total": 21.85,
      "vat_rate": 10.0,
      "unit_measure": "KG",
      "product_id": 42,
      "cost_center_id": null
    }
  ],
  "file_path": "/uploads/fattura.pdf"
}
```

### Dopo (nuova versione) ⭐
```json
{
  "supplier_id": 1,
  "invoice_number": "Q__/168507",
  "invoice_date": "2025-10-27",
  "currency": "EUR",
  "lines": [
    {
      "raw_description": "B.A. CAMPANELLO S/V F Tipo dato: PDC Rif. testo: 3145HOTEL OLIMPIA SRL",  // ⚠️ MODIFICATO
      "product_code": "0015179.01",  // ⭐ NUOVO: Includere se disponibile
      "quantity": 1.9,
      "unit_price": 11.5,
      "total": 21.85,
      "vat_rate": 10.0,
      "unit_measure": "KG",
      "product_id": 42,
      "cost_center_id": null
    }
  ],
  "file_path": "/uploads/fattura.pdf"
}
```

---

## 📄 Esempio Response `/api/invoices/{invoice_id}`

### Dopo (nuova versione) ⭐
```json
{
  "id": 1,
  "supplier": {
    "name": "DAC SPA",
    "vat_number": "IT03038290171",
    "address": "VIA AVEZZANO..."
  },
  "invoice_number": "Q__/168507",
  "invoice_date": "2025-10-27",
  "currency": "EUR",
  "total_amount": 355.72,
  "lines": [
    {
      "id": 1,
      "raw_description": "B.A. CAMPANELLO S/V F Tipo dato: PDC Rif. testo: 3145HOTEL OLIMPIA SRL",
      "product_code": "0015179.01",  // ⭐ NUOVO
      "quantity": 1.9,
      "unit_price": 11.5,
      "total": 21.85,
      "vat_rate": 10.0,
      "currency": "EUR",
      "product_id": 42,
      "product_name": "B.A. CAMPANELLO S/V F",
      "product_internal_code": null,
      "um": "KG"
    }
  ]
}
```

---

## 🔍 Casi Edge

### Caso 1: Codice articolo non presente
```json
{
  "raw_description": "PRODOTTO SENZA CODICE ARTICOLO",
  "product_code": null,  // ⚠️ Può essere null
  "quantity": 5.0,
  "unit_price": 10.0,
  "total": 50.0,
  "match_status": "unmatched"
}
```

### Caso 2: Totale documento non estratto
```json
{
  "invoice_number": "FATT-001",
  "total_amount": null,  // ⚠️ Può essere null se non estratto
  "lines": [...]
}
```

**Gestione frontend:**
```typescript
const displayTotal = response.total_amount ?? 
  response.lines.reduce((sum, line) => sum + (line.total || 0), 0);
```

---

## ✅ Validazione Frontend

### TypeScript Types
```typescript
interface InvoiceLineWithMatch {
  raw_description: string;
  product_code?: string | null;  // Opzionale, può essere null
  quantity?: number | null;
  unit_price?: number | null;
  total?: number | null;
  vat_rate?: number | null;
  unit_measure?: string | null;
  currency?: string | null;
  deterministic_product_id?: number | null;
  deterministic_product_label?: string | null;
  match_status: "matched" | "unmatched";
}

interface InvoiceImportResponse {
  invoice_id?: number | null;
  supplier_id: number;
  supplier: SupplierInfo;
  invoice_number?: string | null;
  invoice_date?: string | null;
  currency?: string | null;
  total_amount?: number | null;  // ⭐ NUOVO
  lines: InvoiceLineWithMatch[];
}
```

---

**Nota**: Tutti i nuovi campi sono opzionali per retrocompatibilità. Il frontend deve gestire correttamente i valori `null`/`undefined`.

