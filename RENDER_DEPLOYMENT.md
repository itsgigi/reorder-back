# 🚀 Deployment su Render - Guida Completa

Render è **molto più semplice** di Vercel per FastAPI perché:
- ✅ Supporto nativo per FastAPI (niente Mangum o adattatori)
- ✅ Nessun problema con handler o runtime
- ✅ Supporto SQLite (se vuoi)
- ✅ PostgreSQL incluso gratuitamente
- ✅ Setup in 5 minuti

## 📋 Passi per il Deploy

### STEP 1: Crea Account su Render

1. Vai su **[render.com](https://render.com)**
2. Clicca **"Get Started for Free"**
3. Registrati con GitHub (più facile)

### STEP 2: Crea un Nuovo Web Service

1. Nel dashboard Render, clicca **"New +"**
2. Seleziona **"Web Service"**
3. Connetti il tuo repository GitHub
4. Seleziona il repository `reorder-backend`

### STEP 3: Configura il Service

Compila i campi:

- **Name**: `reorder-backend` (o qualsiasi nome)
- **Region**: scegli la più vicina (es: `Frankfurt`)
- **Branch**: `main` (o il tuo branch principale)
- **Root Directory**: lascia vuoto (o `.` se necessario)
- **Runtime**: `Python 3`
- **Build Command**: 
  ```bash
  pip install -r requirements.txt
  ```
- **Start Command**: 
  ```bash
  uvicorn app.main:app --host 0.0.0.0 --port $PORT
  ```

### STEP 4: Aggiungi PostgreSQL Database (Opzionale ma Consigliato)

1. Nel dashboard Render, clicca **"New +"**
2. Seleziona **"PostgreSQL"**
3. Compila:
   - **Name**: `reorder-db` (o qualsiasi nome)
   - **Database**: `reorder` (o qualsiasi nome)
   - **User**: lascia default
   - **Region**: stessa del web service
   - **Plan**: **Free** (per iniziare)
4. Clicca **"Create Database"**
5. Attendi 2-3 minuti per la creazione

### STEP 5: Configura Environment Variables

1. Vai al tuo **Web Service** su Render
2. Clicca su **"Environment"** nel menu laterale
3. Aggiungi queste variabili:

#### Se usi PostgreSQL (Consigliato):
```
DATABASE_URL=<Internal Database URL>
```
**Nota**: Render fornisce automaticamente `DATABASE_URL` se colleghi il database al service. Vai su **"Environment"** → **"Link Database"** e seleziona il database che hai creato.

#### Se usi SQLite (solo per test):
```
DATABASE_URL=sqlite:///./reorder.db
```

#### OpenAI API Key:
```
OPENAI_API_KEY=your_openai_api_key_here
```

#### Root Path (opzionale):
```
ROOT_PATH=
```

### STEP 6: Collega il Database al Service

1. Nel tuo **Web Service**, vai su **"Environment"**
2. Scorri fino a **"Add Environment Variable"**
3. Clicca su **"Link Database"**
4. Seleziona il database PostgreSQL che hai creato
5. Render aggiungerà automaticamente `DATABASE_URL`

### STEP 7: Deploy

1. Render inizierà automaticamente il deploy
2. Attendi 3-5 minuti
3. Vedi i log in tempo reale cliccando su **"Logs"**

### STEP 8: Verifica

Dopo il deploy, Render ti darà un URL tipo:
```
https://reorder-backend.onrender.com
```

Testa:
```bash
curl https://reorder-backend.onrender.com/api/health
```

Dovresti vedere: `{"status":"ok"}`

## ✅ Vantaggi di Render vs Vercel

| Feature | Render | Vercel |
|---------|--------|--------|
| FastAPI nativo | ✅ Sì | ❌ Serve Mangum |
| Problemi handler | ✅ Nessuno | ❌ TypeError frequenti |
| SQLite support | ✅ Sì | ❌ Read-only filesystem |
| PostgreSQL gratuito | ✅ Sì (90 giorni) | ❌ No |
| Setup | ✅ 5 minuti | ❌ Complesso |
| Logs | ✅ Facili | ✅ Facili |
| Costo | ✅ Free tier | ✅ Free tier |

## 🔧 Configurazione Avanzata

### Auto-Deploy

Render fa auto-deploy automaticamente quando pushi su GitHub. Puoi disabilitarlo in **Settings → Auto-Deploy**.

### Custom Domain

1. Vai su **Settings → Custom Domains**
2. Aggiungi il tuo dominio
3. Segui le istruzioni per configurare DNS

### Health Checks

Render fa automaticamente health checks. Puoi configurarli in **Settings → Health Check Path**:
```
/api/health
```

## 🐛 Troubleshooting

### Problema: Build fallisce

**Soluzione**:
- Verifica che `requirements.txt` sia corretto
- Controlla i log di build per errori specifici
- Assicurati che Python 3.9+ sia selezionato

### Problema: App non si avvia

**Soluzione**:
- Verifica il **Start Command**: deve essere `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- Controlla i log per errori di import
- Verifica che tutte le variabili d'ambiente siano configurate

### Problema: Database non connesso

**Soluzione**:
- Verifica che il database sia **collegato** al service
- Controlla che `DATABASE_URL` sia presente nelle variabili d'ambiente
- Verifica i log per errori di connessione

## 💰 Costi

### Free Tier Render:
- ✅ Web Service: Gratuito (si spegne dopo 15 minuti di inattività)
- ✅ PostgreSQL: Gratuito per 90 giorni, poi $7/mese
- ✅ 750 ore/mese di compute time

### Per Produzione:
- Web Service: $7/mese (sempre attivo)
- PostgreSQL: $7/mese
- **Totale: ~$14/mese**

## 📝 File Necessari

Render funziona con la struttura attuale del progetto. Non serve:
- ❌ `api/index.py` (non serve su Render)
- ❌ `vercel.json` (non serve su Render)
- ❌ Mangum (non serve su Render)

Serve solo:
- ✅ `requirements.txt` (già presente)
- ✅ `app/main.py` (già presente)
- ✅ Tutto il resto del progetto (già presente)

## 🎯 Prossimi Passi

1. Crea account Render
2. Crea Web Service
3. Collega repository GitHub
4. Configura variabili d'ambiente
5. Deploy automatico!

**Tempo totale: ~10 minuti** vs ore di troubleshooting su Vercel! 🚀

## 🔗 Link Utili

- [Render Docs](https://render.com/docs)
- [Render Python Guide](https://render.com/docs/deploy-fastapi)
- [Render PostgreSQL](https://render.com/docs/databases)

---

**Render è molto più semplice per FastAPI. Provalo!** 🎉

