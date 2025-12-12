"""
Vercel Serverless Function Handler per FastAPI
Questo file è usato SOLO per deployment su Vercel.
Per Render, Railway, Fly.io, etc. questo file NON è necessario.
"""
# Importa l'app FastAPI
from app.main import app

# Vercel Python runtime si aspetta una variabile 'handler'
# Esportiamo direttamente l'app FastAPI come handler ASGI
handler = app
