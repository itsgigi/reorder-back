# Prompt per Team Frontend

## 🚀 Modifiche API - Aggiornamento Richiesto

Il backend è stato aggiornato per migliorare l'estrazione dati dalle fatture. **Aggiorna il frontend** per supportare i nuovi campi.

---

## ⚡ Modifiche Rapide

### 1. Nuovi Campi nelle Response API

**Endpoint `/api/invoices/import`:**
```typescript
// AGGIUNGI a InvoiceImportResponse
total_amount?: number;  // Totale documento comprensivo di IVA

// MODIFICA InvoiceLineWithMatch
interface InvoiceLineWithMatch {
  raw_description: string;      // ⚠️ Ora contiene SOLO descrizione (senza codice)
  product_code?: string;         // ⭐ NUOVO: Codice articolo separato
  // ... altri campi invariati
}
```

**Endpoint `/api/invoices/{invoice_id}`:**
```typescript
// AGGIUNGI a InvoiceLineDetail
product_code?: string;  // Codice articolo
```

### 2. Modifiche Request API

**Endpoint `/api/invoices/confirm`:**
```typescript
// AGGIUNGI a ConfirmInvoiceLine
product_code?: string;  // Includere quando invii la conferma
```

---

## 🎨 Modifiche UI Minime

### Visualizzazione Righe Fattura

**Prima:** Mostravi `raw_description` completo (es. "2PAN161 – (Custom) Camillo MINI BUNS...")

**Ora:** 
- Mostra `product_code` separato (se presente) → badge/stile distintivo
- Mostra `raw_description` → solo descrizione prodotto

**Esempio:**
```tsx
{line.product_code && <Badge>{line.product_code}</Badge>}
<span>{line.raw_description}</span>
```

### Totale Documento

Mostra `total_amount` dalla response invece di calcolarlo:
```tsx
{extraction.total_amount && (
  <div>Totale: {extraction.total_amount} {extraction.currency}</div>
)}
```

---

## ✅ Checklist

- [ ] Aggiorna TypeScript types/interfaces
- [ ] Modifica visualizzazione righe: mostra `product_code` separato
- [ ] Includi `product_code` nel payload di conferma fattura
- [ ] Mostra `total_amount` se disponibile
- [ ] Testa flusso completo

---

## 📋 Dettagli Completi

Vedi `FRONTEND_INTEGRATION.md` per documentazione completa con esempi di codice.

---

**Priorità**: Media  
**Tempo stimato**: 1-2 ore  
**Breaking changes**: No (campi opzionali, retrocompatibile)

