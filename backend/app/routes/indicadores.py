from fastapi import APIRouter, HTTPException
from app.database import conectar

roteador = APIRouter()


# =========================================
# INDICADORES MUNICIPAIS - CENSO 2022
# =========================================

@roteador.get("/indicadores/resumo-municipal")
def resumo_municipal():

    with conectar() as conexao:
        with conexao.cursor() as cursor:

            # População dos setores com dados publicados
            cursor.execute("""
                SELECT
                    SUM(populacao_total),
                    SUM(pop_60_mais),
                    SUM(pop_70_mais),
                    SUM(pop_50_59)
                FROM dados_setor_2022
                WHERE pop_60_mais IS NOT NULL
                  AND pop_70_mais IS NOT NULL
                  AND pop_50_59 IS NOT NULL
            """)

            populacao, idosos, idosos_70, pessoas_50_59 = cursor.fetchone()

            # População total, incluindo setores sem dados etários
            cursor.execute("""
                SELECT SUM(populacao_total)
                FROM dados_setor_2022
            """)

            populacao_municipio = cursor.fetchone()[0]

            # Renda média ponderada pelo número de responsáveis
            cursor.execute("""
                SELECT
                    SUM(
                        renda_media_responsavel *
                        responsaveis_domicilios_ocupados
                    )
                    /
                    NULLIF(
                        SUM(responsaveis_domicilios_ocupados),
                        0
                    )
                FROM dados_setor_2022
                WHERE renda_media_responsavel IS NOT NULL
                  AND responsaveis_domicilios_ocupados > 0
            """)

            renda_media = cursor.fetchone()[0]

    # Verifica se há dados suficientes para calcular
    if (
        not populacao
        or not idosos
        or not populacao_municipio
        or renda_media is None
    ):
        raise HTTPException(
            status_code=500,
            detail="Dados insuficientes para calcular os indicadores."
        )

    # Calcula os quatro indicadores
    percentual_idosos = idosos / populacao * 100

    percentual_70 = idosos_70 / idosos * 100

    geracao_chegando = pessoas_50_59 / idosos * 100

    cobertura = populacao / populacao_municipio * 100

    # Devolve os resultados em JSON
    return {
        "dados": {
            "percentual_60_mais": round(percentual_idosos, 1),
            "percentual_70_entre_idosos": round(percentual_70, 1),
            "geracao_chegando": round(geracao_chegando),
            "renda_media_responsavel": round(float(renda_media), 2)
        },
        "meta": {
            "ano": 2022,
            "cobertura_etaria_percentual": round(cobertura, 1),
            "fonte": "IBGE - Censo Demografico 2022",
            "observacao": (
                "Indicadores etarios usam os mesmos setores "
                "com dados publicados. A renda e ponderada "
                "pelo numero de responsaveis."
            )
        }
    }
