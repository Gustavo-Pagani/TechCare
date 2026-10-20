
"""APIs de perfis de cuidado do TechCare.

As estimativas foram calculadas e validadas na Etapa 11 e
armazenadas em indicador_territorial na Etapa 13.
"""
from fastapi import APIRouter, HTTPException
from app.database import conectar

roteador = APIRouter(tags=["Cuidados"])


# Nomes dos indicadores que já existem no PostgreSQL.
INDICADORES = (
    "populacao_60_mais",
    "autonomos",
    "apoio_leve",
    "dependencia_parcial",
    "dependencia_elevada",
    "dificuldade_ou_dependencia",
    "necessidade_ajuda_declarada",
)

PERFIS = (
    ("autonomo", "autonomos", "Autônomo e independente"),
    ("apoio_leve", "apoio_leve", "Apoio leve"),
    ("dependencia_parcial", "dependencia_parcial", "Dependência parcial"),
    ("dependencia_elevada", "dependencia_elevada", "Dependência elevada"),
)


# =========================================
# 1. ORGANIZAÇÃO E VALIDAÇÃO DOS INDICADORES
# =========================================

def organizar_indicadores(linhas):

    valores = {}

    for nome, valor in linhas:

        if (
            nome in valores
            or valor is None
            or valor < 0
            or valor != int(valor)
        ):
            raise HTTPException(
                500,
                "Indicadores de cuidado inválidos ou duplicados."
            )

        valores[nome] = int(valor)

    if set(valores) != set(INDICADORES):
        raise HTTPException(
            500,
            "Indicadores de cuidado incompletos."
        )

    base = valores["populacao_60_mais"]

    if base <= 0:
        raise HTTPException(
            500,
            "População de referência inválida."
        )

    total_perfis = sum(
        valores[coluna]
        for _, coluna, _ in PERFIS
    )

    if total_perfis != base:
        raise HTTPException(
            500,
            "A soma dos quatro perfis não confere."
        )

    # Confere os indicadores complementares
    if (
        valores["dependencia_parcial"]
        + valores["dependencia_elevada"]
        != valores["necessidade_ajuda_declarada"]
        or
        base - valores["autonomos"]
        != valores["dificuldade_ou_dependencia"]
    ):
        raise HTTPException(
            500,
            "Os indicadores complementares não conferem."
        )

    perfis = []

    for codigo, coluna, nome in PERFIS:

        quantidade = valores[coluna]

        perfis.append({
            "codigo": codigo,
            "nome": nome,
            "quantidade_estimada": quantidade,
            "percentual": round(
                100 * quantidade / base, 2
            ),
        })

    return {
        "populacao_60_mais_base": base,
        "perfis": perfis,
        "indicadores_complementares": {
            "dificuldade_ou_dependencia":
                valores["dificuldade_ou_dependencia"],

            "necessidade_ajuda_declarada":
                valores["necessidade_ajuda_declarada"],
        },
    }


# =========================================
# 2. INFORMAÇÕES METODOLÓGICAS
# =========================================

def metodologia(ano, territorial=False):

    observacao = (
        "Em 2022, a base 60+ é parcial e a composição "
        "por idade e sexo da Seade 2020 é usada como "
        "aproximação. Os perfis não são diagnósticos "
        "individuais nem vagas SAD/ILPI. "
    )

    if territorial:
        observacao += (
            "Por APG, os pesos de idade e sexo são "
            "municipais. Os cenários futuros são "
            "distribuições estimadas pelo TechCare, "
            "não projeções oficiais da Seade por APG."
        )

    return {
        "fonte_parametros": "PNS 2019 - IBGE",
        "fonte_composicao": "Fundação Seade",

        "ano_composicao_seade":
            2020 if ano == 2022 else ano,

        "fonte_populacao": (
            "IBGE - Censo 2022, setores com dado 60+ publicado"
            if ano == 2022
            else "Fundação Seade, projeção municipal"
        ),

        "natureza": "Estimativa de perfis de cuidado do TechCare",
        "observacao": observacao,
    }


# =========================================
# 3. PERFIS DE CUIDADO DO MUNICÍPIO
# =========================================

@roteador.get("/cuidados/perfis-municipio")
def consultar_perfis_municipio(
    ano: int = 2022
):

    if ano not in (2022, 2030, 2040, 2050):
        raise HTTPException(
            status_code=422,
            detail="Ano inválido. Utilize 2022, 2030, 2040 ou 2050."
        )
    with conectar() as conexao:

        with conexao.cursor() as cursor:

            cursor.execute("""
                SELECT
                    nome_indicador,
                    valor

                FROM indicador_territorial

                WHERE nivel_territorial = 'MUNICIPIO'

                AND id_apg IS NULL

                AND ano = %s

                AND nome_indicador IN (
                    'populacao_60_mais',
                    'autonomos',
                    'apoio_leve',
                    'dependencia_parcial',
                    'dependencia_elevada',
                    'dificuldade_ou_dependencia',
                    'necessidade_ajuda_declarada'
                )
            """, (ano,))

            linhas = cursor.fetchall()

    if not linhas:
        raise HTTPException(
            404,
            "Não foram encontrados perfis para esse ano."
        )

    return {
        "municipio": "Campinas",
        "ano": ano,
        **organizar_indicadores(linhas),
        "meta": metodologia(ano),
    }


# =========================================
# 4. PERFIS DE CUIDADO DAS APGs
# =========================================

@roteador.get("/cuidados/perfis-apg")
def consultar_perfis_apg(
    ano: int = 2022,
    id_apg: int | None = None
):

    if ano not in (2022, 2030, 2040, 2050):
        raise HTTPException(
            status_code=422,
            detail="Ano inválido. Utilize 2022, 2030, 2040 ou 2050."
        )
    
    with conectar() as conexao:

        with conexao.cursor() as cursor:

            cursor.execute("""
                SELECT
                    i.id_apg,
                    a.nome_apg,
                    i.nome_indicador,
                    i.valor

                FROM indicador_territorial AS i

                JOIN apg AS a
                    ON a.id_apg = i.id_apg

                WHERE i.nivel_territorial = 'APG'

                AND i.ano = %s

                AND (
                    %s::integer IS NULL
                    OR i.id_apg = %s::integer
                )

                AND i.nome_indicador IN (
                    'populacao_60_mais',
                    'autonomos',
                    'apoio_leve',
                    'dependencia_parcial',
                    'dependencia_elevada',
                    'dificuldade_ou_dependencia',
                    'necessidade_ajuda_declarada'
                )

                ORDER BY
                    a.nome_apg,
                    i.nome_indicador
            """, (ano, id_apg, id_apg))

            linhas = cursor.fetchall()

    if not linhas:
        raise HTTPException(
            404,
            "Nenhuma APG encontrada para os filtros informados."
        )

    # Agrupa os indicadores por APG
    grupos = {}

    for codigo, nome, indicador, valor in linhas:

        codigo = int(codigo)

        if codigo not in grupos:
            grupos[codigo] = {
                "id_apg": codigo,
                "nome_apg": nome,
                "linhas": [],
            }

        grupos[codigo]["linhas"].append(
            (indicador, valor)
        )

    if id_apg is None and len(grupos) != 17:
        raise HTTPException(
            500,
            "A consulta não retornou as 17 APGs."
        )

    # Monta a resposta de cada APG
    apgs = []

    for grupo in grupos.values():

        apgs.append({
            "id_apg": grupo["id_apg"],
            "nome_apg": grupo["nome_apg"],

            **organizar_indicadores(
                grupo["linhas"]
            ),
        })

    return {
        "ano": ano,
        "quantidade_apgs": len(apgs),
        "apgs": apgs,
        "meta": metodologia(
            ano,
            territorial=True
        ),
    }
