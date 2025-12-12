"""
Vercel Serverless Function Handler per FastAPI
Questo file adatta l'app FastAPI per funzionare su Vercel come serverless function.
"""
import os
from mangum import Mangum
from app.main import app

# Mangum adatta l'app ASGI (FastAPI) per AWS Lambda/Vercel
# lifespan="off" disabilita gli eventi di startup/shutdown che non funzionano su serverless
handler = Mangum(app, lifespan="off")

# Vercel si aspetta una variabile chiamata 'handler' o 'app' a livello di modulo
# Non usare __all__ per evitare problemi con il runtime Vercel

