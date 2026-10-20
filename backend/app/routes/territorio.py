
"""APIs territoriais do TechCare: indicadores das 17 APGs e mapa GeoJSON.

Dados de 2022: IBGE/Censo (cobertura etária parcial).
Dados de 2030/2040/2050: estimativas territoriais do TechCare,
NÃO projeções oficiais da Seade por APG.
"""

import json

from fastapi import APIRouter, HTTPException
from psycopg.rows import dict_row

from app.database import conectar

roteador = APIRouter(tags=["Território"])
ANOS = (2022, 2030, 2040, 2050)
TOTAL_APGS = 17


# =========================================================
# 1. FUNÇÕES COMPARTILHADAS
# =========================================================

def validar_ano(ano):
    if ano not in ANOS:
        raise HTTPException(
            status_code=422,
            detail="Ano inválido. Utilize 2022, 2030, 2040 ou 2050."
        )


def metadados(ano):
    if ano == 2022:
        return {
            "fonte": "IBGE - Censo Demográfico 2022",
            "natureza": "Dados censitários publicados; cobertura etária parcial",
            "observacao": (
                "A população 60+ soma apenas setores com dado divulgado. "
                "O percentual 60+ usa como denominador somente a "
                "população dos setores com divulgação etária. "
                "A população total inclui todos os setores. "
                "Dados ausentes não são considerados zero."
            ),
        }

    return {
        "fonte": "Fundação Seade e cálculos territoriais do TechCare",
        "natureza": "Estimativa territorial do TechCare",
        "observacao": (
            "A Fundação Seade fornece projeções municipais. "
            "A distribuição por APG foi estimada pelo TechCare; "
            "não é uma projeção oficial da Seade por APG."
        ),
    }


# =========================================================
# 2. LISTA DAS 17 APGs E INDICADORES RESUMIDOS
# =========================================================

SQL_RESUMO = """
    SELECT
        a.id_apg,
        a.codigo_apg,
        a.nome_apg,

        MAX(CASE WHEN i.nome_indicador = 'populacao_total'
            THEN i.valor END) AS populacao_total,

        MAX(CASE WHEN i.nome_indicador = 'populacao_60_mais'
            THEN i.valor END) AS populacao_60_mais,

        MAX(CASE WHEN i.nome_indicador = 'percentual_60_mais_setores_com_dado'
            THEN i.valor END) AS percentual_censitario,

        MAX(CASE WHEN i.nome_indicador = 'percentual_60_mais'
            THEN i.valor END) AS percentual_estimado,

        MAX(CASE WHEN i.nome_indicador = 'cobertura_populacional_dado_60_mais'
            THEN i.valor END) AS cobertura_2022

    FROM apg AS a

    LEFT JOIN indicador_territorial AS i
        ON i.id_apg = a.id_apg
       AND i.nivel_territorial = 'APG'
       AND i.ano = %s
       AND i.nome_indicador IN (
           'populacao_total',
           'populacao_60_mais',
           'percentual_60_mais_setores_com_dado',
           'percentual_60_mais',
           'cobertura_populacional_dado_60_mais'
       )

    GROUP BY a.id_apg, a.codigo_apg, a.nome_apg
    ORDER BY a.nome_apg
"""


def obter_resumos(ano):

    with conectar() as conexao:
        with conexao.cursor(row_factory=dict_row) as cursor:
            cursor.execute(SQL_RESUMO, (ano,))
            linhas = cursor.fetchall()

    if len(linhas) != TOTAL_APGS:
        raise HTTPException(
            500,
            "O banco não retornou as 17 APGs."
        )

    apgs = []

    for linha in linhas:

        percentual = (
            linha["percentual_censitario"]
            if ano == 2022
            else linha["percentual_estimado"]
        )

        if (
            linha["populacao_total"] is None
            or linha["populacao_60_mais"] is None
            or percentual is None
            or (
                ano == 2022
                and linha["cobertura_2022"] is None
            )
        ):
            raise HTTPException(
                500,
                f"Indicadores incompletos para a APG {linha['id_apg']}."
            )

        apgs.append({
            "id_apg": int(linha["id_apg"]),
            "codigo_apg": linha["codigo_apg"],
            "nome_apg": linha["nome_apg"],
            "ano": ano,

            "populacao_total":
                int(linha["populacao_total"]),

            "populacao_60_mais":
                int(linha["populacao_60_mais"]),

            "percentual_60_mais":
                round(float(percentual), 2),

            "cobertura_populacional_2022": (
                round(float(linha["cobertura_2022"]), 2)
                if ano == 2022
                else None
            ),
        })

    return apgs


@roteador.get("/territorio/apgs")
def consultar_apgs(ano: int = 2022):

    validar_ano(ano)
    apgs = obter_resumos(ano)

    return {
        "ano": ano,
        "quantidade_apgs": len(apgs),
        "apgs": apgs,
        "meta": metadados(ano),
    }


# =========================================================
# 3. INDICADORES DETALHADOS DE UMA APG
# =========================================================

@roteador.get("/territorio/apg/{id_apg}")
def consultar_apg(
    id_apg: int,
    ano: int = 2022
):

    validar_ano(ano)

    with conectar() as conexao:

        with conexao.cursor(row_factory=dict_row) as cursor:

            cursor.execute("""
                SELECT id_apg, codigo_apg, nome_apg

                FROM apg

                WHERE id_apg = %s
            """, (id_apg,))

            apg = cursor.fetchone()

            if apg is None:
                raise HTTPException(
                    404,
                    "APG não encontrada."
                )

            cursor.execute("""
                SELECT
                    ano,
                    nome_indicador,
                    valor,
                    unidade,
                    fonte_base,
                    natureza_valor,
                    metodologia

                FROM indicador_territorial

                WHERE nivel_territorial = 'APG'

                AND id_apg = %s

                AND ano IN (2022, 2030, 2040, 2050)

                ORDER BY ano, nome_indicador
            """, (id_apg,))

            linhas = cursor.fetchall()

    # Organiza todos os indicadores por ano
    por_ano = {
        ano_item: {}
        for ano_item in ANOS
    }

    for linha in linhas:

        ano_item = int(linha["ano"])
        nome = linha["nome_indicador"]

        if nome in por_ano[ano_item]:
            raise HTTPException(
                500,
                "Indicadores territoriais duplicados."
            )

        por_ano[ano_item][nome] = {
            "valor": float(linha["valor"]),
            "unidade": linha["unidade"],
            "fonte_base": linha["fonte_base"],
            "natureza_valor": linha["natureza_valor"],
            "metodologia": linha["metodologia"],
        }

    # Cria a série para os gráficos da APG
    serie = []

    for ano_item in ANOS:

        indicadores = por_ano[ano_item]

        nome_percentual = (
            "percentual_60_mais_setores_com_dado"
            if ano_item == 2022
            else "percentual_60_mais"
        )

        obrigatorios = (
            "populacao_total",
            "populacao_60_mais",
            nome_percentual
        )

        if any(
            nome not in indicadores
            for nome in obrigatorios
        ):
            raise HTTPException(
                500,
                f"Indicadores incompletos em {ano_item}."
            )

        serie.append({
            "ano": ano_item,

            "populacao_total": int(
                indicadores["populacao_total"]["valor"]
            ),

            "populacao_60_mais": int(
                indicadores["populacao_60_mais"]["valor"]
            ),

            "percentual_60_mais": round(
                indicadores[nome_percentual]["valor"],
                2
            ),
        })

    return {
        "id_apg": int(apg["id_apg"]),
        "codigo_apg": apg["codigo_apg"],
        "nome_apg": apg["nome_apg"],
        "ano_selecionado": ano,

        "indicadores": por_ano[ano],

        "serie_populacional": serie,

        "meta": metadados(ano),
    }


# =========================================================
# 4. GEOMETRIAS GEOJSON PARA O MAPA LEAFLET
# =========================================================

@roteador.get("/territorio/geojson")
def consultar_geojson(ano: int = 2022):

    validar_ano(ano)

    # Busca os indicadores das APGs
    resumos = obter_resumos(ano)

    por_id = {
        apg["id_apg"]: apg
        for apg in resumos
    }

    # Busca as geometrias no PostGIS
    with conectar() as conexao:

        with conexao.cursor(row_factory=dict_row) as cursor:

            cursor.execute("""
                SELECT
                    id_apg,

                    ST_AsGeoJSON(
                        ST_Transform(geometria, 4326)
                    ) AS geometria_geojson

                FROM apg

                ORDER BY id_apg
            """)

            geometrias = cursor.fetchall()

    if len(geometrias) != TOTAL_APGS:
        raise HTTPException(
            500,
            "Geometrias das APGs incompletas."
        )

    features = []

    for linha in geometrias:

        id_apg = int(linha["id_apg"])
        geometria = linha["geometria_geojson"]

        if geometria is None or id_apg not in por_id:
            raise HTTPException(
                500,
                f"Geometria ausente para a APG {id_apg}."
            )

        features.append({
            "type": "Feature",
            "id": id_apg,

            "properties": por_id[id_apg],

            "geometry": json.loads(geometria),
        })

    return {
        "type": "FeatureCollection",
        "features": features,
        "meta": metadados(ano),
    }
