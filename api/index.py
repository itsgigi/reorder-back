"""
Vercel Serverless Function Handler per FastAPI
Questo file adatta l'app FastAPI per funzionare su Vercel come serverless function.
"""
import sys
import os

# Importa l'app FastAPI
from app.main import app

# Prova a usare Mangum, ma gestisci errori di compatibilità con Vercel runtime
try:
    from mangum import Mangum
    
    # Mangum converte l'app ASGI (FastAPI) in un handler compatibile con AWS Lambda/Vercel
    # lifespan="off" disabilita gli eventi di startup/shutdown che non funzionano su serverless
    handler = Mangum(app, lifespan="off")
    
except (TypeError, AttributeError, ImportError) as e:
    # Se Mangum fallisce a causa di problemi di compatibilità con Vercel runtime
    # Usa un wrapper ASGI semplice
    import logging
    logger = logging.getLogger(__name__)
    logger.warning(f"Mangum initialization failed: {e}, using ASGI wrapper")
    
    async def asgi_wrapper(scope, receive, send):
        """ASGI wrapper per Vercel quando Mangum non funziona"""
        await app(scope, receive, send)
    
    handler = asgi_wrapper
except Exception as e:
    # Ultimo fallback: esporta direttamente l'app
    # Vercel potrebbe gestirlo direttamente in alcune configurazioni
    import logging
    logger = logging.getLogger(__name__)
    logger.error(f"Unexpected error with Mangum: {e}, using app directly")
    handler = app

