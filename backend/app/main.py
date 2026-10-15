from fastapi import FastAPI

# Cria a aplicação
app = FastAPI(
    title="TechCare API",
    version="1.0.0"
)

# Cria uma rota para verificar o servidor
@app.get("/api/v1/status")
def verificar_status():
    return {
        "status": "online",
        "projeto": "TechCare"
    }

#Teste:
#python -m uvicorn app.main:app --reload