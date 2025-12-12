# Troubleshooting - Errori 404 e Problemi di Connessione

## 🔍 Diagnosi Problemi Comuni

### Problema: 404 NOT_FOUND in Produzione

#### 1. Verifica gli Endpoint Disponibili

L'applicazione espone endpoint in due modi:

**Con prefisso `/api`:**
- `GET /api/health` ✅
- `GET /api/invoices` ✅
- `POST /api/invoices/import` ✅
- etc.

**Senza prefisso (per compatibilità):**
- `GET /` ✅
- `GET /health` ✅
- `GET /routes` ✅ (lista tutti i route)
- `GET /docs` ✅ (documentazione Swagger)

#### 2. Test Rapido degli Endpoint

Prova questi endpoint in ordine:

```bash
# 1. Root endpoint
curl https://your-domain.com/

# 2. Health check senza prefisso
curl https://your-domain.com/health

# 3. Health check con prefisso
curl https://your-domain.com/api/health

# 4. Lista route disponibili
curl https://your-domain.com/routes
```

#### 3. Verifica la Configurazione ROOT_PATH

Se l'app è dietro un reverse proxy, controlla il file `.env`:

```env
# Se NON usi reverse proxy, lascia vuoto o rimuovi:
ROOT_PATH=

# Se usi reverse proxy (es: nginx con /api), configura:
ROOT_PATH=/api
```

**⚠️ IMPORTANTE**: Se `ROOT_PATH` è configurato ma non dovrebbe esserlo, rimuovilo o lascialo vuoto!

#### 4. Controlla i Log

Con il logging abilitato, dovresti vedere nei log del server:

```
INFO: GET /health - Headers: {...}
INFO: Response status: 200
```

Se non vedi i log, significa che le richieste non arrivano al server.

### Problema: Frontend non riesce a chiamare il Backend

#### 1. Verifica CORS

Il backend è configurato per accettare richieste da qualsiasi origine (`allow_origins=["*"]`). Se hai ancora problemi:

- Verifica che il frontend stia chiamando l'URL corretto
- Controlla la console del browser per errori CORS specifici
- Verifica che il metodo HTTP sia corretto (GET, POST, etc.)

#### 2. Verifica l'URL Base

Assicurati che il frontend chiami l'URL corretto:

```javascript
// ✅ Corretto
const API_URL = "https://your-backend-domain.com/api";

// ❌ Sbagliato (manca /api)
const API_URL = "https://your-backend-domain.com";
```

#### 3. Test con curl/Postman

Testa prima con curl o Postman per escludere problemi del frontend:

```bash
# Test health check
curl -X GET https://your-backend-domain.com/api/health

# Test con headers CORS
curl -X GET https://your-backend-domain.com/api/health \
  -H "Origin: https://your-frontend-domain.com" \
  -H "Access-Control-Request-Method: GET"
```

### Problema: Endpoint funziona in locale ma non in produzione

#### 1. Verifica le Variabili d'Ambiente

Assicurati che in produzione siano configurate:

```env
DATABASE_URL=sqlite:///./reorder.db
OPENAI_API_KEY=your_actual_key
ROOT_PATH=  # Vuoto se non usi reverse proxy
```

#### 2. Verifica il Processo

Assicurati che il server sia in esecuzione:

```bash
# Verifica se il processo è attivo
ps aux | grep uvicorn

# Verifica le porte
netstat -tulpn | grep 8000
```

#### 3. Verifica i Permessi del Database

Se usi SQLite, assicurati che il file del database abbia i permessi corretti:

```bash
chmod 644 reorder.db
```

## 🛠️ Soluzioni Rapide

### Soluzione 1: Rimuovi ROOT_PATH se non necessario

Nel file `.env` in produzione:

```env
ROOT_PATH=
```

Oppure rimuovi completamente la riga.

### Soluzione 2: Riavvia il Server

Dopo aver modificato le configurazioni:

```bash
# Se usi systemd
sudo systemctl restart reorder-backend

# Se usi PM2
pm2 restart reorder-backend

# Se usi Docker
docker restart reorder-backend
```

### Soluzione 3: Verifica il Reverse Proxy

Se usi nginx o altro reverse proxy, verifica la configurazione:

```nginx
location / {
    proxy_pass http://localhost:8000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

## 📊 Checklist Debug

- [ ] L'endpoint `/` risponde?
- [ ] L'endpoint `/health` risponde?
- [ ] L'endpoint `/api/health` risponde?
- [ ] L'endpoint `/routes` mostra tutti i route?
- [ ] I log mostrano le richieste in arrivo?
- [ ] `ROOT_PATH` è configurato correttamente (o vuoto)?
- [ ] Il server è in esecuzione?
- [ ] Le variabili d'ambiente sono configurate?
- [ ] Il database esiste e ha i permessi corretti?
- [ ] CORS è configurato correttamente?

## 🆘 Se Nulla Funziona

1. **Controlla i log completi del server** - Cerca errori o eccezioni
2. **Testa in locale** - Verifica che funzioni in locale prima
3. **Verifica la configurazione del deployment** - Platform-specific (Vercel, Railway, AWS, etc.)
4. **Controlla il firewall/security groups** - Assicurati che la porta sia aperta
5. **Verifica DNS** - Assicurati che il dominio punti al server corretto

## 📝 Informazioni Utili per il Supporto

Se apri un issue, includi:

- URL completo che stai chiamando
- Metodo HTTP (GET, POST, etc.)
- Headers della richiesta
- Log del server (ultime 50 righe)
- Configurazione `.env` (senza chiavi sensibili)
- Configurazione del reverse proxy (se presente)
- Piattaforma di deployment (Vercel, Railway, AWS, etc.)

