"""
Vercel Serverless Function Handler per FastAPI
Questo file adatta l'app FastAPI per funzionare su Vercel come serverless function.
"""
from mangum import Mangum
from app.main import app

# Mangum adatta l'app ASGI (FastAPI) per AWS Lambda/Vercel
handler = Mangum(app, lifespan="off")

# Vercel si aspetta una funzione chiamata 'handler' o 'app'
# Esportiamo 'handler' che è compatibile con Vercel Python runtime
__all__ = ["handler"]

