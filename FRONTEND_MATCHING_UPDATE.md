# Aggiornamento Frontend - Matching Migliorato

## 📋 Riepilogo Modifiche

Il backend è stato aggiornato per migliorare il matching deterministico dei prodotti durante il caricamento delle fatture. **Nessuna modifica richiesta al frontend**, ma è utile sapere come funziona.

---

## 🎯 Come Funziona il Matching

### Priorità del Matching

Quando viene caricata una fattura, il sistema cerca di matchare ogni riga con un prodotto esistente seguendo questa priorità:

1. **Match su `product_code`** (se presente nella riga fattura) - **PRIORITARIO**
   - Cerca prima sul campo `product_code` del prodotto nel database
   - Se non trova, cerca prodotti con il codice nel nome (retrocompatibilità)
   
2. **Match sul nome** (se `product_code` non è presente o non trova match)
   - Match esatto case-insensitive
   
3. **Match fuzzy** (ultima risorsa)
   - Match su parte iniziale normalizzata della descrizione

### Esempio

**Riga fattura:**
```json
{
  "product_code": "0015179.01",
  "raw_description": "B.A. CAMPANELLO S/V F",
  ...
}
```

**Il sistema:**
1. Cerca un prodotto con `product_code = "0015179.01"` ✅ **Match deterministico**
2. Se non trova, cerca prodotti con nome che inizia con "0015179.01"
3. Se non trova, cerca prodotti con nome "B.A. CAMPANELLO S/V F"
4. Se non trova, cerca match fuzzy sulla descrizione

---

## ✅ Cosa Viene Salvato Automaticamente

### Durante il Caricamento Fattura

Quando viene caricata una fattura:
- Se una riga ha `product_code` e viene matchata con un prodotto esistente **senza** `product_code`, il codice viene **automaticamente salvato** sul prodotto
- Se una riga ha `product_code` e non viene matchata, viene creato un nuovo prodotto con il `product_code` salvato

**Nessuna azione richiesta dal frontend** - tutto avviene automaticamente nel backend.

---

## 📊 Modifiche API (Già Documentate)

### Lista Prodotti - Campo `product_code`

La lista prodotti (`/api/products`) ora include `product_code` invece di `unit_measure`:

**Prima:**
```json
{
  "id": 1,
  "name": "B.A. CAMPANELLO S/V F",
  "unit_price": 11.5,
  "unit_measure": "KG"  // ❌ Rimosso
}
```

**Dopo:**
```json
{
  "id": 1,
  "product_code": "0015179.01",  // ✅ Aggiunto dopo id
  "name": "B.A. CAMPANELLO S/V F",
  "unit_price": 11.5
}
```

---

## 🎨 Suggerimenti UI (Opzionali)

### Indicatore di Match Deterministico

Puoi mostrare un indicatore visivo quando un prodotto è stato matchato tramite `product_code` (più affidabile):

```tsx
{line.match_status === "matched" && line.product_code && (
  <Badge variant="success" title="Match deterministico su codice articolo">
    ✓ Match Codice
  </Badge>
)}
```

### Visualizzazione Codice Prodotto

Nella lista prodotti, puoi mostrare il `product_code` se presente:

```tsx
{product.product_code && (
  <span className="product-code">{product.product_code}</span>
)}
```

---

## 🔍 Debug e Verifica

### Verificare il Matching

Dopo il caricamento di una fattura, controlla la response `/api/invoices/import`:

```json
{
  "lines": [
    {
      "product_code": "0015179.01",
      "raw_description": "B.A. CAMPANELLO S/V F",
      "match_status": "matched",  // ✅ Match trovato
      "deterministic_product_id": 42,
      "deterministic_product_label": "B.A. CAMPANELLO S/V F"
    }
  ]
}
```

### Verificare che il Codice sia Salvato

Dopo aver confermato una fattura, verifica che il prodotto abbia il `product_code`:

```bash
GET /api/products/{product_id}
```

Response dovrebbe includere:
```json
{
  "id": 42,
  "product_code": "0015179.01",  // ✅ Salvato automaticamente
  "name": "B.A. CAMPANELLO S/V F",
  ...
}
```

---

## 📝 Note Tecniche

- Il matching su `product_code` è **case-sensitive** (esatto)
- Il matching sul nome è **case-insensitive**
- Se una riga non ha `product_code`, il sistema usa il matching sul nome
- Il `product_code` viene salvato automaticamente quando viene creato o matchato un prodotto
- Non è necessario inviare `product_code` nella conferma fattura se già presente nella response di import

---

## ✅ Checklist Frontend (Opzionale)

- [ ] Aggiornare visualizzazione lista prodotti per mostrare `product_code` se presente
- [ ] Mostrare indicatore visivo per match deterministico (opzionale)
- [ ] Verificare che il flusso di caricamento fattura funzioni correttamente
- [ ] Testare con fatture che hanno `product_code` e senza

---

**Data aggiornamento**: 2025-01-XX  
**Priorità**: Informazionale (nessuna modifica richiesta)  
**Breaking changes**: No

