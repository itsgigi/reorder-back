"""
Vercel Serverless Function Handler per FastAPI
Questo file adatta l'app FastAPI per funzionare su Vercel come serverless function.
"""
# Importa l'app
from app.main import app

# Usa Mangum per adattare FastAPI a Vercel serverless
# Mangum converte l'app ASGI (FastAPI) in un handler compatibile con AWS Lambda/Vercel
from mangum import Mangum

# Crea l'handler
# lifespan="off" disabilita gli eventi di startup/shutdown che non funzionano su serverless
handler = Mangum(app, lifespan="off")

