# Deployment su Vercel

Questa guida spiega come deployare il Reorder Backend su Vercel come serverless function.

## 🚀 Configurazione Vercel

### File Necessari

Il progetto è già configurato con:

1. **`api/index.py`** - Handler serverless che adatta FastAPI per Vercel usando Mangum
2. **`vercel.json`** - Configurazione Vercel per routing e build
3. **`requirements.txt`** - Include `mangum` per l'adattatore serverless

### Struttura

```
.
├── api/
│   ├── __init__.py
│   └── index.py          # Handler Vercel serverless
├── app/                  # La tua app FastAPI
│   ├── main.py
│   └── ...
├── vercel.json           # Configurazione Vercel
└── requirements.txt
```

## 📋 Passi per il Deploy

### 1. Installa Vercel CLI (opzionale)

```bash
npm i -g vercel
```

### 2. Deploy

**Opzione A: Via Dashboard Vercel**
1. Vai su [vercel.com](https://vercel.com)
2. Importa il repository GitHub
3. Vercel rileverà automaticamente la configurazione Python

**Opzione B: Via CLI**
```bash
vercel
```

### 3. Configura Variabili d'Ambiente

Nel dashboard Vercel, vai su **Settings → Environment Variables** e aggiungi:

```env
OPENAI_API_KEY=your_openai_api_key_here
DATABASE_URL=sqlite:///./reorder.db
ROOT_PATH=
```

⚠️ **IMPORTANTE**: Vercel ha un filesystem read-only per le serverless functions. SQLite potrebbe non funzionare correttamente in produzione su Vercel.

### 4. Database su Vercel

**Problema**: SQLite non funziona bene su Vercel serverless perché:
- Il filesystem è read-only
- Le funzioni sono stateless
- Il database verrebbe perso ad ogni deploy

**Soluzioni**:

#### Opzione 1: Database esterno (Consigliato)
Usa un database esterno come:
- **PostgreSQL**: Supabase, Neon, Railway, Render
- **MySQL**: PlanetScale, Railway
- **MongoDB**: MongoDB Atlas

Aggiorna `DATABASE_URL` in Vercel:
```env
DATABASE_URL=postgresql://user:password@host:port/dbname
```

#### Opzione 2: Vercel KV / Upstash (per dati semplici)
Per dati leggeri, considera Vercel KV o Upstash Redis.

#### Opzione 3: Migra a Render/Railway/Fly.io
Per un deployment più tradizionale con SQLite supportato.

## 🔧 Come Funziona

### Mangum Adapter

`api/index.py` usa **Mangum** per adattare FastAPI (ASGI) a AWS Lambda/Vercel:

```python
from mangum import Mangum
from app.main import app

handler = Mangum(app, lifespan="off")
```

### Routing Vercel

`vercel.json` configura:
- **Build**: Usa `@vercel/python` per buildare `api/index.py`
- **Routes**: Tutte le richieste (`/*`) vanno a `api/index.py`
- **PYTHONPATH**: Impostato a `.` per importare `app.*`

## ✅ Verifica Deployment

Dopo il deploy, testa:

```bash
# Health check
curl https://your-project.vercel.app/health

# API health
curl https://your-project.vercel.app/api/health

# Root
curl https://your-project.vercel.app/
```

## 🐛 Troubleshooting

### Problema: 404 su tutti gli endpoint

**Causa**: Vercel non trova `api/index.py` o la configurazione è sbagliata.

**Soluzione**:
1. Verifica che `api/index.py` esista
2. Verifica che `vercel.json` sia nella root
3. Controlla i build logs su Vercel

### Problema: Import errors

**Causa**: PYTHONPATH non configurato correttamente.

**Soluzione**: 
- Verifica che `vercel.json` abbia `"PYTHONPATH": "."`
- Assicurati che tutti i moduli siano importabili dalla root

### Problema: Database non funziona

**Causa**: SQLite su filesystem read-only di Vercel.

**Soluzione**: 
- Migra a database esterno (PostgreSQL, etc.)
- Oppure usa un hosting diverso (Render, Railway) per il backend

### Problema: Cold start lento

**Causa**: Le serverless functions hanno cold start.

**Soluzione**:
- Considera Vercel Pro per funzioni più veloci
- Oppure usa hosting tradizionale (Render, Railway) per performance migliori

## 📝 Note Importanti

1. **Cold Start**: La prima richiesta dopo inattività può essere lenta (1-3 secondi)
2. **Timeout**: Funzioni Vercel hanno timeout (10s Hobby, 60s Pro)
3. **File Upload**: Per file grandi, considera Vercel Blob Storage
4. **Database**: SQLite non è adatto per produzione su Vercel serverless

## 🔄 Alternative a Vercel per FastAPI

Se hai bisogno di:
- **SQLite support**: Render, Railway, Fly.io
- **Performance costanti**: Render, Railway, Fly.io
- **WebSocket**: Render, Railway, Fly.io
- **Long-running tasks**: Render, Railway, Fly.io

Vercel è ottimo per:
- **Serverless**: Pay-per-use, scaling automatico
- **Edge functions**: Bassa latenza globale
- **Frontend + Backend**: Deploy tutto insieme

## 📚 Risorse

- [Vercel Python Documentation](https://vercel.com/docs/concepts/functions/serverless-functions/runtimes/python)
- [Mangum Documentation](https://mangum.io/)
- [FastAPI on Vercel Guide](https://vercel.com/guides/deploying-fastapi-with-vercel)

