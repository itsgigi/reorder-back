"""
Vercel Serverless Function Handler per FastAPI
Questo file adatta l'app FastAPI per funzionare su Vercel come serverless function.
"""
try:
    from mangum import Mangum
    from app.main import app
    
    # Mangum adatta l'app ASGI (FastAPI) per AWS Lambda/Vercel
    # lifespan="off" disabilita gli eventi di startup/shutdown che non funzionano su serverless
    handler = Mangum(app, lifespan="off")
except Exception as e:
    # Fallback se Mangum ha problemi
    import sys
    import traceback
    print(f"Error initializing Mangum: {e}", file=sys.stderr)
    traceback.print_exc(file=sys.stderr)
    # Esporta direttamente l'app come fallback
    from app.main import app
    handler = app

