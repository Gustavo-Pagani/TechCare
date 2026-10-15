#python -m uvicorn app.main:app --reload
# hhtp /docs (ver endpoints)
from fastapi import FastAPI
from app.routes import indicadores
from fastapi.middleware.cors import CORSMiddleware


# Inicializa o FastAPI
app = FastAPI(
    title="TechCare API",
    version="1.0.0"
)

# Permite que o frontend local consulte a API
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500"
    ],
    allow_methods=["GET"],
    allow_headers=["*"]
)

# Registra o módulo de indicadores
app.include_router(
    indicadores.roteador,
    prefix="/api/v1"
)

# Verifica se o servidor está funcionando
@app.get("/api/v1/status")
def verificar_status():
    return {
        "status": "online",
        "projeto": "TechCare"
    }