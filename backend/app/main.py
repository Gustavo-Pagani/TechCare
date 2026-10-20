#python -m uvicorn app.main:app --reload
# hhtp /docs (ver endpoints)
from fastapi import FastAPI
from app.routes import indicadores, projecoes, demografia, cuidados, servicos, territorio
from fastapi.middleware.cors import CORSMiddleware


# Inicializa o FastAPI
app = FastAPI(
    title="TechCare API",
    version="1.0.0"
)

# =========================================
# COMUNICAÇÃO COM O FRONTEND
# =========================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500"
    ],
    allow_methods=["GET"],
    allow_headers=["*"]
)

# =========================================
# MÓDULOS DA API
# =========================================

app.include_router(
    indicadores.roteador,
    prefix="/api/v1"
)

app.include_router(
    projecoes.roteador,
    prefix="/api/v1"
)

# API de demografia
app.include_router(
    demografia.roteador,
    prefix="/api/v1"
)

# API de perfis de cuidado
app.include_router(
    cuidados.roteador,
    prefix="/api/v1"
)

app.include_router(
    servicos.roteador,
    prefix="/api/v1"
)

# API territorial das APGs
app.include_router(
    territorio.roteador,
    prefix="/api/v1"
)
# =========================================
# STATUS DO SERVIDOR
# =========================================

@app.get("/api/v1/status")
def verificar_status():

    return {
        "status": "online",
        "projeto": "TechCare"
    }