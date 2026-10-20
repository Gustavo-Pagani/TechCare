from fastapi import APIRouter, HTTPException
from app.database import conectar

roteador = APIRouter()


# =========================================
# PROJEÇÕES POPULACIONAIS DE CAMPINAS
# Fonte: Fundação Seade
# =========================================

@roteador.get("/projecoes/municipio")
def consultar_projecoes():

    # Consulta os dados no PostgreSQL
    with conectar() as conexao:

        with conexao.cursor() as cursor:

            cursor.execute("""
                SELECT
                    ano,
                    SUM(populacao) AS populacao_60_mais

                FROM projecao_populacional

                WHERE cod_ibge = '3509502'

                AND ano IN (2025, 2030, 2040, 2050)

                AND faixa_etaria IN (
                    '60 a 64',
                    '65 a 69',
                    '70 a 74',
                    '75 e +'
                )

                GROUP BY ano
                ORDER BY ano
            """)

            resultados = cursor.fetchall()


    # Organiza os resultados
    dados = []

    for ano, populacao in resultados:

        dados.append({
            "ano": ano,
            "populacao_60_mais": int(populacao)
        })


    # Organiza os valores para calcular o crescimento
    valores = {
        item["ano"]: item["populacao_60_mais"]
        for item in dados
    }

    anos_esperados = {2025, 2030, 2040, 2050}

    # Verifica se todos os anos foram encontrados
    if set(valores) != anos_esperados or valores[2025] == 0:

        raise HTTPException(
            status_code=500,
            detail="Dados de projeção incompletos."
        )


    # Calcula o crescimento de 2025 até 2050
    crescimento = (
        (valores[2050] - valores[2025])
        / valores[2025]
    ) * 100


    # Devolve os dados para o frontend
    return {
        "dados": dados,

        "crescimento_2025_2050_percentual": round(
            crescimento, 1
        ),

        "meta": {
            "municipio": "Campinas",
            "ano_inicial": 2025,
            "ano_final": 2050,
            "fonte": "Fundação Seade",
            "natureza": "Projeção populacional municipal oficial",
            "faixa_etaria": "60 anos ou mais"
        }
    }
