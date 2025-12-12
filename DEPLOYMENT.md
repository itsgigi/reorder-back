# Guida al Deployment

Questa guida spiega come deployare il Reorder Backend in produzione.

## 🚀 Opzioni di Deployment

### 1. Uvicorn Standalone

Per un deployment semplice con uvicorn:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### 2. Uvicorn con Workers (Produzione)

Per migliori performance in produzione:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 3. Con Gunicorn + Uvicorn Workers

Per un deployment più robusto:

```bash
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

**Nota**: Aggiungi `gunicorn` a `requirements.txt` se usi questa opzione.

### 4. Docker

Crea un `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 🔧 Configurazione per Reverse Proxy

Se deployi l'applicazione dietro un reverse proxy (nginx, Cloudflare, AWS ALB, ecc.), potrebbe essere necessario configurare il `root_path`.

### Esempio con Nginx

```nginx
location /api {
    proxy_pass http://localhost:8000;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

In questo caso, imposta la variabile d'ambiente:

```env
ROOT_PATH=/api
```

### Esempio con Cloudflare/AWS

Se l'app è servita su un path specifico, configura:

```env
ROOT_PATH=/v1
```

## 🌐 Variabili d'Ambiente

Assicurati di configurare queste variabili in produzione:

```env
# Database
DATABASE_URL=sqlite:///./reorder.db
# Oppure per PostgreSQL:
# DATABASE_URL=postgresql://user:password@localhost/reorder

# OpenAI API Key
OPENAI_API_KEY=your_production_api_key

# Root path (solo se necessario)
ROOT_PATH=
```

## ✅ Verifica Deployment

Dopo il deployment, verifica che funzioni:

1. **Endpoint root**: `GET /` - Dovrebbe restituire informazioni sull'API
2. **Health check**: `GET /api/health` - Dovrebbe restituire `{"status": "ok"}`
3. **Documentazione**: `GET /docs` - Dovrebbe mostrare la documentazione Swagger

## 🐛 Troubleshooting 404

Se ricevi errori 404 in produzione:

1. **Verifica il path**: Assicurati di chiamare gli endpoint con il prefisso `/api` (es: `/api/health`)
2. **Controlla il root_path**: Se l'app è dietro un reverse proxy, configura `ROOT_PATH` correttamente
3. **Verifica i log**: Controlla i log del server per vedere se le richieste arrivano
4. **Testa localmente**: Verifica che l'app funzioni in locale con `uvicorn app.main:app --reload`

## 📝 Note

- Il database SQLite viene creato automaticamente al primo avvio
- Per produzione, considera l'uso di PostgreSQL invece di SQLite
- Assicurati di avere backup del database
- Configura HTTPS in produzione (tramite reverse proxy o certificati SSL)

