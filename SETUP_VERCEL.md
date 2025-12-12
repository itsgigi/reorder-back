# 🚀 Guida Completa: Setup Vercel + Database

Questa è la guida **passo-passo** per deployare il backend su Vercel con database PostgreSQL.

## ⚠️ Problema Attuale

Stai ricevendo errori:
- `Cannot assign requested address` → Problema IPv6 (Vercel non supporta IPv6)
- `TypeError: issubclass() arg 1 must be a class` → Problema Mangum

## ✅ Soluzione: Usa Neon invece di Supabase

**Perché Neon?**
- ✅ Supporto nativo per serverless/Vercel
- ✅ Nessun problema IPv6
- ✅ Più veloce per serverless
- ✅ Gratuito (3GB storage)

## 📋 Passi da Seguire

### STEP 1: Crea Database su Neon

1. Vai su **[neon.tech](https://neon.tech)**
2. Clicca **"Sign Up"** (puoi usare GitHub)
3. Clicca **"Create Project"**
4. Compila:
   - **Name**: `reorder-backend` (o qualsiasi nome)
   - **Region**: scegli la più vicina (es: `Europe (Frankfurt)`)
   - **PostgreSQL version**: lascia default (15)
5. Clicca **"Create Project"**
6. Attendi 30 secondi per la creazione

### STEP 2: Copia la Connection String

1. Nella dashboard Neon, vedrai la **Connection String**
2. Clicca sul pulsante **"Copy"** accanto alla connection string
3. Formato: `postgresql://user:password@ep-xxx-xxx.region.aws.neon.tech/dbname?sslmode=require`
4. **SALVA questa stringa** - ti servirà dopo!

### STEP 3: Configura Vercel

1. Vai su **[vercel.com](https://vercel.com)**
2. Vai al tuo progetto
3. Clicca su **"Settings"** (in alto)
4. Clicca su **"Environment Variables"** (menu laterale)
5. Clicca **"Add New"**
6. Compila:
   - **Key**: `DATABASE_URL`
   - **Value**: incolla la connection string di Neon che hai copiato
   - **Environment**: seleziona tutte (Production, Preview, Development)
7. Clicca **"Save"**

### STEP 4: Aggiungi OPENAI_API_KEY (se non l'hai già fatto)

1. Sempre in **Environment Variables**
2. Clicca **"Add New"**
3. Compila:
   - **Key**: `OPENAI_API_KEY`
   - **Value**: la tua chiave OpenAI
   - **Environment**: tutte
4. Clicca **"Save"**

### STEP 5: Riavvia il Deployment

1. Vai su **"Deployments"** (menu laterale)
2. Trova l'ultimo deployment
3. Clicca sui **3 puntini** (⋮) → **"Redeploy"**
4. Oppure fai un nuovo commit/push per triggerare un nuovo deploy

### STEP 6: Verifica che Funzioni

1. Attendi che il deploy finisca (2-3 minuti)
2. Vai su **"Logs"** per vedere se ci sono errori
3. Testa l'endpoint:
   ```bash
   curl https://your-project.vercel.app/api/health
   ```
4. Dovresti vedere: `{"status":"ok"}`

## 🎯 Risultato Atteso

Dopo questi passi:
- ✅ Nessun errore IPv6
- ✅ Database connesso correttamente
- ✅ Tabelle create automaticamente
- ✅ API funzionante

## 🔄 Se Preferisci Continuare con Supabase

Se vuoi continuare con Supabase, devi:

1. **Usa il Connection Pooler** (porta 6543)
2. **Risolvi il problema IPv6**:
   - Vai su Supabase Dashboard
   - Settings → Database → Connection Pooling
   - Usa la connection string del pooler
   - **IMPORTANTE**: Il codice ora risolve automaticamente a IPv4, ma Neon è più affidabile

## ❓ Domande Frequenti

### Perché Neon invece di Supabase?

- Neon è progettato per serverless
- Nessun problema IPv6
- Più semplice da configurare
- Performance migliori su Vercel

### Posso usare Supabase?

Sì, ma devi usare il Connection Pooler (porta 6543) e il codice ora risolve automaticamente a IPv4. Neon è comunque più semplice.

### Quanto costa Neon?

**Gratuito** fino a:
- 3GB storage
- 1 compute hour/giorno
- Più che sufficiente per iniziare!

### Come verifico che il database funzioni?

Dopo il deploy, controlla i log di Vercel. Dovresti vedere:
```
✅ PostgreSQL database tables created/verified successfully
```

## 🆘 Se Qualcosa Non Funziona

1. **Controlla i Log di Vercel**:
   - Vai su Deployments → clicca sul deployment → Logs
   - Cerca errori in rosso

2. **Verifica le Environment Variables**:
   - Settings → Environment Variables
   - Assicurati che `DATABASE_URL` sia presente
   - Verifica che la connection string sia corretta

3. **Testa la Connection String**:
   ```bash
   # Prova a connetterti (se hai psql installato)
   psql "postgresql://user:pass@host:port/dbname"
   ```

4. **Rifai il Deploy**:
   - A volte serve un nuovo deploy dopo aver aggiunto variabili d'ambiente

## 📝 Checklist Finale

- [ ] Database Neon creato
- [ ] Connection string copiata
- [ ] `DATABASE_URL` aggiunta in Vercel
- [ ] `OPENAI_API_KEY` aggiunta in Vercel (se necessario)
- [ ] Deployment riavviato
- [ ] Health check funziona (`/api/health`)
- [ ] Nessun errore nei log

---

**Hai bisogno di aiuto?** Controlla i log di Vercel e verifica che tutte le variabili d'ambiente siano configurate correttamente!

