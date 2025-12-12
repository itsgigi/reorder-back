# Integrazione Frontend - Modifiche API

## 📋 Riepilogo Modifiche

Il backend è stato ottimizzato per migliorare l'estrazione dei dati dalle fatture. Le principali modifiche riguardano:

1. **Separazione codice articolo dalla descrizione prodotto**
2. **Estrazione del totale documento comprensivo di IVA**
3. **Matching deterministico migliorato basato sul codice articolo**

---

## 🔄 Modifiche agli Schemi API

### 1. Endpoint `/api/invoices/import` - Response

La risposta `InvoiceImportResponse` ora include:

```typescript
interface InvoiceImportResponse {
  invoice_id?: number;
  supplier_id: number;
  supplier: SupplierInfo;
  invoice_number?: string;
  invoice_date?: string;
  currency?: string;
  total_amount?: number;  // ⭐ NUOVO: Totale documento comprensivo di IVA
  lines: InvoiceLineWithMatch[];
}
```

### 2. Schema `InvoiceLineWithMatch` - Modifiche

Ogni riga fattura ora include il campo `product_code`:

```typescript
interface InvoiceLineWithMatch {
  raw_description: string;      // ⚠️ MODIFICATO: Ora contiene SOLO la descrizione (senza codice articolo)
  product_code?: string;        // ⭐ NUOVO: Codice articolo/fornitore separato
  quantity?: number;
  unit_price?: number;
  total?: number;
  vat_rate?: number;
  unit_measure?: string;
  currency?: string;
  deterministic_product_id?: number;
  deterministic_product_label?: string;
  match_status: "matched" | "unmatched";
}
```

**IMPORTANTE**: 
- `raw_description` ora contiene **SOLO** la descrizione prodotto (es. "B.A. CAMPANELLO S/V F")
- `product_code` contiene il codice articolo separato (es. "0015179.01", "2PAN161")
- Se il codice articolo non è presente, `product_code` sarà `null` o `undefined`

### 3. Endpoint `/api/invoices/confirm` - Request

La richiesta `ConfirmInvoiceRequest` ora include:

```typescript
interface ConfirmInvoiceLine {
  raw_description: string;
  product_code?: string;        // ⭐ NUOVO: Includere se disponibile
  quantity: number;
  unit_price: number;
  total: number;
  vat_rate?: number;
  unit_measure?: string;
  product_id?: number;
  cost_center_id?: number;
}
```

### 4. Endpoint `/api/invoices/{invoice_id}` - Response

La risposta `InvoiceDetail` include `product_code` nelle righe:

```typescript
interface InvoiceLineDetail {
  id: number;
  raw_description: string;
  product_code?: string;        // ⭐ NUOVO
  quantity?: number;
  unit_price?: number;
  total?: number;
  vat_rate?: number;
  currency?: string;
  product_id?: number;
  product_name?: string;
  product_internal_code?: string;
  um?: string;
}
```

---

## 🎨 Modifiche UI Consigliate

### 1. Visualizzazione Righe Fattura

**Prima:**
```
2PAN161 – (Custom) Camillo MINI BUNS PANINI AL LATTE 32GR 60PZ...
```

**Dopo:**
```
[0015179.01] B.A. CAMPANELLO S/V F
```

**Suggerimento UI:**
- Mostrare il codice articolo in un badge/stile distintivo se presente
- Se `product_code` è presente, mostrarlo prima della descrizione
- Usare uno stile visivamente separato (es. badge grigio, monospace font)

**Esempio React/TypeScript:**
```tsx
{line.product_code && (
  <span className="product-code-badge">{line.product_code}</span>
)}
<span className="product-description">{line.raw_description}</span>
```

### 2. Visualizzazione Totale Documento

Ora puoi mostrare il totale documento estratto direttamente dalla fattura:

```tsx
{extraction.total_amount && (
  <div className="invoice-total">
    <label>Totale Documento:</label>
    <span>{formatCurrency(extraction.total_amount, extraction.currency)}</span>
  </div>
)}
```

**Nota**: Il backend ora fornisce `total_amount` nell'estrazione. Puoi confrontarlo con la somma delle righe per validazione.

### 3. Form di Conferma Fattura

Assicurati di includere `product_code` quando invii la conferma:

```typescript
const confirmInvoice = async (data: InvoiceData) => {
  const payload: ConfirmInvoiceRequest = {
    supplier_id: data.supplier_id,
    invoice_number: data.invoice_number,
    invoice_date: data.invoice_date,
    currency: data.currency,
    lines: data.lines.map(line => ({
      raw_description: line.raw_description,
      product_code: line.product_code,  // ⭐ Includere
      quantity: line.quantity,
      unit_price: line.unit_price,
      total: line.total,
      vat_rate: line.vat_rate,
      unit_measure: line.unit_measure,
      product_id: line.product_id,
      cost_center_id: line.cost_center_id,
    })),
    file_path: data.file_path,
  };
  
  await api.post('/api/invoices/confirm', payload);
};
```

---

## 🔍 Matching Deterministico Migliorato

Il backend ora usa il `product_code` per un matching più preciso:

1. **Priorità 1**: Match su `product_code` (se presente) - più affidabile
2. **Priorità 2**: Match su descrizione esatta
3. **Priorità 3**: Match su codice estratto dalla descrizione
4. **Priorità 4**: Match fuzzy su descrizione normalizzata

**Implicazioni per il frontend:**
- Se una riga ha `product_code` e `match_status: "matched"`, il match è molto affidabile
- Puoi mostrare un indicatore visivo diverso per match basati su codice articolo
- Il `deterministic_product_label` mostra il nome del prodotto matchato

---

## 📝 Checklist Integrazione

- [ ] Aggiornare TypeScript interfaces/types per includere `product_code` e `total_amount`
- [ ] Modificare la visualizzazione delle righe per mostrare codice articolo separato
- [ ] Aggiornare il form di conferma per includere `product_code`
- [ ] Mostrare il totale documento estratto (`total_amount`) se disponibile
- [ ] Testare il flusso completo: import → visualizzazione → conferma
- [ ] Verificare che il matching deterministico funzioni correttamente con i nuovi campi

---

## 🐛 Gestione Compatibilità

Se il backend non restituisce `product_code` o `total_amount` (per fatture vecchie o errori di estrazione):

- `product_code` sarà `null`/`undefined` → mostrare solo la descrizione
- `total_amount` sarà `null`/`undefined` → calcolare dalla somma delle righe come fallback

**Esempio:**
```typescript
const displayTotal = extraction.total_amount ?? 
  extraction.lines.reduce((sum, line) => sum + (line.total || 0), 0);
```

---

## 📞 Note Tecniche

- Il campo `product_code` è opzionale (`Optional<string>`)
- Il campo `total_amount` è opzionale (`Optional<number>`)
- Entrambi i campi possono essere `null` se non estratti correttamente dalla fattura
- Il matching deterministico funziona anche senza `product_code`, ma è meno preciso

---

## 🧪 Test Consigliati

1. **Test con fattura tipo**: Verificare che codice articolo e descrizione siano separati correttamente
2. **Test matching**: Verificare che prodotti con stesso codice articolo vengano matchati correttamente
3. **Test totale documento**: Verificare che `total_amount` corrisponda al totale nella fattura
4. **Test retrocompatibilità**: Verificare che fatture senza `product_code` funzionino ancora

---

**Data aggiornamento**: 2025-01-XX
**Versione API**: Compatibile con backend aggiornato

