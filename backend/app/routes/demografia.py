
from fastapi import APIRouter, HTTPException
from app.database import conectar

roteador = APIRouter(tags=["Demografia"])


# =========================================
# 1. CENSO 2022: FAIXAS ETÁRIAS
# =========================================

@roteador.get("/demografia/faixas-etarias-2022")
def consultar_faixas_etarias_2022():

    with conectar() as conexao:
        with conexao.cursor() as cursor:

            cursor.execute("""
                SELECT
                    COUNT(*) AS setores_total,

                    COUNT(pop_60_mais) AS setores_com_dado,

                    COALESCE(
                        SUM(populacao_total), 0
                    ) AS populacao_total,

                    COALESCE(
                        SUM(populacao_total) FILTER (
                            WHERE pop_60_mais IS NOT NULL
                        ), 0
                    ) AS populacao_coberta,

                    COALESCE(
                        SUM(pop_50_59) FILTER (
                            WHERE pop_60_mais IS NOT NULL
                        ), 0
                    ) AS pop_50_59,

                    COALESCE(
                        SUM(pop_60_69) FILTER (
                            WHERE pop_60_mais IS NOT NULL
                        ), 0
                    ) AS pop_60_69,

                    COALESCE(
                        SUM(pop_70_mais) FILTER (
                            WHERE pop_60_mais IS NOT NULL
                        ), 0
                    ) AS pop_70_mais,

                    COALESCE(
                        SUM(pop_60_mais), 0
                    ) AS pop_60_mais

                FROM dados_setor_2022
            """)

            resultado = cursor.fetchone()

    if resultado is None:
        raise HTTPException(
            status_code=500,
            detail="Não foi possível consultar o Censo 2022."
        )

    (
        setores_total,
        setores_com_dado,
        populacao_total,
        populacao_coberta,
        pop_50_59,
        pop_60_69,
        pop_70_mais,
        pop_60_mais
    ) = map(int, resultado)

    if not populacao_coberta or not pop_60_mais:
        raise HTTPException(
            status_code=500,
            detail="Dados demográficos insuficientes."
        )

    # Confere se as faixas compõem o total 60+
    if pop_60_69 + pop_70_mais != pop_60_mais:
        raise HTTPException(
            status_code=500,
            detail="As faixas etárias não conferem com o total 60+."
        )

    return {
        "dados": {
            "populacao_50_59": pop_50_59,
            "populacao_60_69": pop_60_69,
            "populacao_70_mais": pop_70_mais,
            "populacao_60_mais": pop_60_mais,

            "percentual_60_mais": round(
                100 * pop_60_mais / populacao_coberta, 2
            ),

            "percentual_70_mais_entre_60_mais": round(
                100 * pop_70_mais / pop_60_mais, 2
            ),

            "pessoas_50_59_por_100_60_mais": round(
                100 * pop_50_59 / pop_60_mais, 2
            )
        },

        "cobertura": {
            "setores_total": setores_total,
            "setores_com_dado_60_mais": setores_com_dado,

            "setores_sem_dado_60_mais":
                setores_total - setores_com_dado,

            "populacao_total_setores": populacao_total,

            "populacao_setores_com_dado_60_mais":
                populacao_coberta,

            "populacao_setores_sem_dado_60_mais":
                populacao_total - populacao_coberta,

            "percentual_populacional": round(
                100 * populacao_coberta / populacao_total, 2
            ) if populacao_total else None
        },

        "meta": {
            "municipio": "Campinas",
            "ano": 2022,
            "fonte": "IBGE - Censo Demográfico 2022",
            "natureza": "Dados publicados, com cobertura parcial",
            "observacao": (
                "As faixas foram somadas apenas nos setores "
                "com dado 60+ publicado. Informações "
                "suprimidas não foram consideradas zero."
            )
        }
    }


# =========================================
# 2. SÉRIE ETÁRIA DA FUNDAÇÃO SEADE
# =========================================

@roteador.get("/demografia/serie-etaria-seade")
def consultar_serie_etaria_seade():

    with conectar() as conexao:
        with conexao.cursor() as cursor:

            cursor.execute("""
                SELECT
                    ano,
                    COUNT(*) AS registros,

                    SUM(populacao) AS populacao_total,

                    SUM(populacao) FILTER (
                        WHERE faixa_etaria IN (
                            '60 a 64',
                            '65 a 69',
                            '70 a 74',
                            '75 e +'
                        )
                    ) AS pop_60_mais,

                    SUM(populacao) FILTER (
                        WHERE faixa_etaria = '75 e +'
                    ) AS pop_75_mais

                FROM projecao_populacional

                WHERE cod_ibge = %s

                AND ano IN (2025, 2030, 2040, 2050)

                GROUP BY ano
                ORDER BY ano
            """, ("3509502",))

            resultados = cursor.fetchall()

    anos_esperados = {2025, 2030, 2040, 2050}

    anos_encontrados = {
        int(linha[0]) for linha in resultados
    }

    if anos_encontrados != anos_esperados:
        raise HTTPException(
            status_code=500,
            detail="Série da Seade incompleta."
        )

    dados = []

    for ano, registros, total, pop_60_mais, pop_75_mais in resultados:

        # Cada ano deve ter 16 faixas etárias x 2 sexos
        if (
            int(registros) != 32
            or total is None
            or pop_60_mais is None
            or pop_75_mais is None
            or int(total) <= 0
        ):
            raise HTTPException(
                status_code=500,
                detail=f"Dados incompletos no ano {ano}."
            )

        total = int(total)
        pop_60_mais = int(pop_60_mais)
        pop_75_mais = int(pop_75_mais)

        dados.append({
            "ano": int(ano),

            "populacao_total": total,

            "populacao_0_59":
                total - pop_60_mais,

            "populacao_60_74":
                pop_60_mais - pop_75_mais,

            "populacao_60_mais": pop_60_mais,

            "populacao_75_mais": pop_75_mais,

            "percentual_60_mais": round(
                100 * pop_60_mais / total, 2
            ),

            "percentual_75_mais": round(
                100 * pop_75_mais / total, 2
            )
        })

    return {
        "dados": dados,

        "meta": {
            "municipio": "Campinas",
            "fonte": "Fundação Seade",
            "natureza": "Projeções municipais por idade e sexo",
            "anos": [2025, 2030, 2040, 2050],

            "observacao": (
                "A última faixa etária disponível é 75+. "
                "Não permite identificar separadamente 80+. "
                "Não tratar a série Seade e o Censo 2022 "
                "como uma única série estatística."
            )
        }
    }
