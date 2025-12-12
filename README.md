# Reorder Backend

Backend API per la gestione automatizzata di fatture e prodotti, con estrazione intelligente tramite AI e matching automatico.

## 🚀 Caratteristiche

- **Estrazione automatica fatture**: Estrazione dati strutturati da fatture PDF/immagini tramite Datapizza AI
- **Matching intelligente**: Matching automatico dei prodotti con il database esistente usando codici prodotto e descrizioni
- **Gestione prodotti**: Catalogo prodotti con storico prezzi e analisi variazioni
- **Gestione fornitori**: Anagrafica fornitori con fatture associate
- **Dashboard**: Statistiche e riepiloghi per monitoraggio
- **Merge prodotti**: Funzionalità per unire prodotti duplicati

## 📋 Requisiti

- Python 3.8+
- SQLite (o altro database supportato da SQLAlchemy)
- API Key OpenAI (per Datapizza AI)

## 🛠️ Installazione

1. **Clona il repository**
```bash
git clone https://github.com/itsgigi/reorder-back.git
cd reorder-back
```

2. **Crea un ambiente virtuale**
```bash
python -m venv venv
source venv/bin/activate  # Su Windows: venv\Scripts\activate
```

3. **Installa le dipendenze**
```bash
pip install -r requirements.txt
```

4. **Configura le variabili d'ambiente**

Crea un file `.env` nella root del progetto:
```env
OPENAI_API_KEY=your_openai_api_key_here
DATABASE_URL=sqlite:///./reorder.db
```

5. **Inizializza il database**

Il database viene creato automaticamente al primo avvio dell'applicazione.

## 🏃 Avvio

```bash
uvicorn app.main:app --reload
```

L'API sarà disponibile su `http://localhost:8000`

Documentazione interattiva (Swagger UI): `http://localhost:8000/docs`

## 📚 API Endpoints

### Health Check
- `GET /api/health` - Verifica stato del servizio

### Fatture
- `POST /api/invoices/import` - Importa e estrae dati da una fattura (PDF/immagine)
- `POST /api/invoices/confirm` - Conferma e salva una fattura dopo il refinement
- `GET /api/invoices` - Lista tutte le fatture
- `GET /api/invoices/{invoice_id}` - Dettagli di una fattura specifica
- `DELETE /api/invoices/{invoice_id}` - Elimina una fattura

### Prodotti
- `GET /api/products` - Lista tutti i prodotti con variazioni di prezzo
- `GET /api/products/{product_id}` - Dettagli completi di un prodotto con storico prezzi
- `POST /api/products/{source_product_id}/merge` - Unisce due prodotti

### Dashboard
- `GET /api/dashboard/summary` - Statistiche riassuntive (totale fatture, importo, prodotti)

## 🔧 Architettura

```
app/
├── main.py              # Applicazione FastAPI principale
├── config.py            # Configurazione e settings
├── deps.py              # Dipendenze (DB session, ecc.)
├── api/
│   └── routes.py        # Endpoints API
├── db/
│   ├── models.py        # Modelli SQLAlchemy
│   └── session.py       # Configurazione database
├── schemas/
│   ├── invoice.py       # Schemi Pydantic per fatture
│   ├── product.py       # Schemi Pydantic per prodotti
│   └── confirm_invoice.py
└── services/
    ├── invoice_extractor.py  # Estrazione AI con Datapizza
    └── matching.py           # Logica di matching prodotti
```

## 🗄️ Database

Il sistema utilizza SQLAlchemy ORM con i seguenti modelli principali:

- **Supplier**: Fornitori
- **Product**: Prodotti con codici e prezzi
- **Invoice**: Fatture
- **InvoiceLine**: Righe di fattura
- **ProductPriceHistory**: Storico prezzi prodotti

## 🔍 Matching dei Prodotti

Il sistema implementa un matching intelligente a due livelli:

1. **Matching deterministico**: Basato su `product_code` quando disponibile
2. **Matching fuzzy**: Basato su similarità delle descrizioni quando il codice non è disponibile

Durante l'importazione di una fattura, ogni riga viene automaticamente matchata con i prodotti esistenti nel database.

## 📝 Note

- Il database SQLite (`reorder.db`) viene creato automaticamente al primo avvio
- Le fatture importate vengono prima estratte e mostrate all'utente per conferma prima del salvataggio definitivo
- Lo storico dei prezzi viene automaticamente aggiornato ad ogni nuova fattura confermata

## 📄 Documentazione

Per esempi dettagliati delle API, consulta:
- `API_EXAMPLES.md` - Esempi di request/response
- `FRONTEND_INTEGRATION.md` - Guida integrazione frontend
- `FRONTEND_MATCHING_UPDATE.md` - Aggiornamenti sistema matching

## 🧪 Sviluppo

Per contribuire al progetto:

1. Crea un branch per la tua feature
2. Implementa le modifiche
3. Testa le API
4. Crea una Pull Request

## 📄 Licenza

Questo progetto è privato.

## 👤 Autore

itsgigi

---

Per supporto o domande, apri una issue su GitHub.

