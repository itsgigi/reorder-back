# Setup Database PostgreSQL

Questa guida spiega come configurare un database PostgreSQL per il Reorder Backend.

## 🚀 Opzioni Gratuite per PostgreSQL

### 1. Supabase (Consigliato) ⭐

**Vantaggi**: Gratuito, facile da usare, dashboard completa

1. Vai su [supabase.com](https://supabase.com)
2. Crea un account gratuito
3. Clicca "New Project"
4. Compila:
   - **Name**: reorder-backend (o qualsiasi nome)
   - **Database Password**: scegli una password forte (salvala!)
   - **Region**: scegli la più vicina
5. Attendi 2-3 minuti per la creazione
6. Vai su **Settings → Database**
7. Per **Vercel/Serverless**: Usa il **Connection Pooler** (porta 6543)
   - Vai su **Settings → Database → Connection Pooling**
   - Copia la **Connection String** dal pooler
   - Formato: `postgresql://postgres:[PASSWORD]@db.xxx.supabase.co:6543/postgres`
   - ⚠️ **IMPORTANTE**: Usa la porta **6543** (pooler) non 5432 per serverless!
   - ⚠️ **NOTA**: Non includere parametri `pgbouncer` nella connection string (psycopg2 non li supporta)
8. Per sviluppo locale: Puoi usare la porta 5432 normale

**Nota**: Il codice converte automaticamente la porta 5432 in 6543 per Supabase, ma è meglio usare direttamente il pooler.

**Limiti gratuiti**: 500MB storage, 2GB bandwidth/mese

### 2. Neon

**Vantaggi**: Serverless PostgreSQL, molto veloce

1. Vai su [neon.tech](https://neon.tech)
2. Crea un account gratuito
3. Clicca "Create Project"
4. Compila i dati del progetto
5. Copia la **Connection String** dalla dashboard

**Limiti gratuiti**: 3GB storage, 1 compute hour/giorno

### 3. Railway

**Vantaggi**: Facile, buona integrazione

1. Vai su [railway.app](https://railway.app)
2. Crea un account
3. Clicca "New Project" → "Add PostgreSQL"
4. Copia la **Connection String** dalla dashboard

**Limiti gratuiti**: $5 crediti/mese

## 🔧 Configurazione

### Opzione 1: Variabile d'Ambiente (Vercel)

Nel dashboard Vercel:
1. Vai su **Settings → Environment Variables**
2. Aggiungi:
   ```
   DATABASE_URL=postgresql://user:password@host:port/dbname
   ```
3. Clicca "Save"
4. Riavvia il deployment

### Opzione 2: File .env (Locale)

Crea un file `.env` nella root del progetto:

```env
DATABASE_URL=postgresql://user:password@host:port/dbname
OPENAI_API_KEY=your_key_here
```

**⚠️ IMPORTANTE**: Non committare il file `.env` (è già nel `.gitignore`)

## 📋 Inizializzazione Database

### Metodo 1: Automatico (All'avvio)

L'app crea automaticamente le tabelle al primo avvio se il database è vuoto.

### Metodo 2: Script Manuale

Esegui lo script di inizializzazione:

```bash
python init_db.py
```

Oppure con DATABASE_URL specificato:

```bash
DATABASE_URL=postgresql://user:pass@host:port/dbname python init_db.py
```

## ✅ Verifica

Dopo la configurazione, verifica che funzioni:

1. **Health Check**:
   ```bash
   curl https://your-app.vercel.app/api/health
   ```

2. **Test Database** (se hai accesso):
   ```bash
   # Connettiti al database
   psql "postgresql://user:pass@host:port/dbname"
   
   # Lista tabelle
   \dt
   
   # Dovresti vedere:
   # - suppliers
   # - products
   # - invoices
   # - invoice_lines
   # - product_price_history
   ```

## 🐛 Troubleshooting

### Errore: "could not connect to server" o "Cannot assign requested address"

**Causa**: 
- Per Supabase su Vercel: stai usando la porta 5432 invece del pooler (6543)
- Connection string sbagliata o database non raggiungibile
- Problemi IPv6 vs IPv4

**Soluzione**:
- **Per Supabase su Vercel**: Usa il **Connection Pooler** (porta 6543)
  - Vai su Supabase → Settings → Database → Connection Pooling
  - Copia la connection string dal pooler
  - Formato: `postgresql://...@db.xxx.supabase.co:6543/...?pgbouncer=true`
- Verifica la connection string
- Assicurati che il database sia attivo
- Il codice converte automaticamente 5432→6543 per Supabase, ma è meglio usare direttamente il pooler

### Errore: "password authentication failed"

**Causa**: Password errata nella connection string

**Soluzione**:
- Verifica la password nel DATABASE_URL
- Assicurati di aver sostituito `[PASSWORD]` con la password reale

### Errore: "database does not exist"

**Causa**: Il database specificato non esiste

**Soluzione**:
- Crea il database manualmente
- Oppure usa il database di default (`postgres`)

### Tabelle non create

**Causa**: Errore durante la creazione

**Soluzione**:
- Esegui manualmente: `python init_db.py`
- Controlla i log per errori specifici
- Verifica i permessi del database user

## 📝 Formato Connection String

```
postgresql://[user]:[password]@[host]:[port]/[database]
```

Esempio:
```
postgresql://postgres:mypassword123@db.abcdefgh.supabase.co:5432/postgres
```

## 🔒 Sicurezza

1. **Non committare** la connection string nel codice
2. Usa **variabili d'ambiente** sempre
3. **Ruota le password** periodicamente
4. Usa **connection pooling** in produzione (già configurato con SQLAlchemy)

## 📚 Risorse

- [Supabase Docs](https://supabase.com/docs)
- [Neon Docs](https://neon.tech/docs)
- [PostgreSQL Connection Strings](https://www.postgresql.org/docs/current/libpq-connect.html#LIBPQ-CONNSTRING)

