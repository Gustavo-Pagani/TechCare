
"""Consulta aos cadastros e indicadores documentais de serviços do TechCare."""

from collections import Counter

from fastapi import APIRouter, HTTPException
from psycopg.rows import dict_row

from app.database import conectar

roteador = APIRouter(tags=["Serviços"])


# =========================================
# 1. INFORMAÇÕES E CUIDADOS METODOLÓGICOS
# =========================================

def informacoes_cadastro():
    return {
        "fontes": [
            "Entidades Registradas CMI 28.11.2025",
            "PMAS Campinas 2026-2029",
        ],
        "observacao": (
            "São registros documentais de entidades e serviços. "
            "O cadastro não comprova natureza pública, vagas "
            "disponíveis ou capacidade instalada. "
            "Os serviços não foram distribuídos por APG."
        ),
    }


def precisa_revisao(valor):
    return valor is True or str(valor).strip().lower() == "true"


# =========================================
# 2. RESUMO DOS SERVIÇOS CADASTRADOS
# =========================================

@roteador.get("/servicos/resumo")
def consultar_resumo_servicos():
    with conectar() as conexao:
        with conexao.cursor(row_factory=dict_row) as cursor:
            cursor.execute("""
                SELECT tipo_servico, nivel_registro,
                       id_apg, review_required
                FROM servico_publico
            """)
            servicos = cursor.fetchall()

            cursor.execute("""
                SELECT COUNT(*) AS total
                FROM indicador_publico
            """)
            total_indicadores = cursor.fetchone()["total"]

    por_tipo = Counter(
        servico["tipo_servico"] for servico in servicos
    )
    por_nivel = Counter(
        servico["nivel_registro"] for servico in servicos
    )

    return {
        "dados": {
            "total_registros": len(servicos),
            "registros_por_tipo": dict(sorted(por_tipo.items())),
            "registros_por_nivel": dict(sorted(por_nivel.items())),
            "registros_para_revisao": sum(
                precisa_revisao(s["review_required"])
                for s in servicos
            ),
            "registros_com_apg": sum(
                s["id_apg"] not in (None, "")
                for s in servicos
            ),
            "total_indicadores_documentais": int(total_indicadores),
        },
        "meta": informacoes_cadastro(),
    }


# =========================================
# 3. CATÁLOGO DE ENTIDADES E SERVIÇOS
# =========================================

@roteador.get("/servicos/catalogo")
def consultar_catalogo_servicos(
    tipo_servico: str | None = None,
    busca: str | None = None,
):
    sql = """
        SELECT chave_servico, nome_servico, tipo_servico,
               nivel_registro, publico_alvo, cnpj,
               endereco, bairro, telefone, id_apg,
               fonte, pagina_fonte, review_required
        FROM servico_publico
        WHERE 1 = 1
    """
    parametros = []

    if tipo_servico and tipo_servico.strip():
        sql += " AND LOWER(tipo_servico) = LOWER(%s)"
        parametros.append(tipo_servico.strip())

    if busca and busca.strip():
        sql += """
            AND (
                nome_servico ILIKE %s
                OR bairro ILIKE %s
            )
        """
        termo = f"%{busca.strip()}%"
        parametros.extend([termo, termo])

    sql += " ORDER BY tipo_servico, nome_servico, chave_servico"

    with conectar() as conexao:
        with conexao.cursor(row_factory=dict_row) as cursor:
            cursor.execute(sql, parametros)
            servicos = cursor.fetchall()

    return {
        "quantidade": len(servicos),
        "servicos": servicos,
        "meta": informacoes_cadastro(),
    }


# =========================================
# 4. INDICADORES DOCUMENTAIS
# =========================================

@roteador.get("/servicos/indicadores")
def consultar_indicadores_servicos(
    origem: str | None = None,
    chave_servico: str | None = None,
):
    if origem and origem.upper() not in ("PMAS", "PMS"):
        raise HTTPException(
            status_code=422,
            detail="Origem inválida. Utilize PMAS ou PMS."
        )

    sql = """
        SELECT chave_indicador, chave_servico, id_apg,
               origem, numero_meta, nome_indicador,
               descricao, valor, unidade, ano_referencia,
               periodo_referencia, fonte, pagina_fonte,
               observacao, review_required
        FROM indicador_publico
        WHERE 1 = 1
    """
    parametros = []

    if origem:
        sql += " AND origem = %s"
        parametros.append(origem.upper())

    if chave_servico and chave_servico.strip():
        sql += " AND chave_servico = %s"
        parametros.append(chave_servico.strip())

    sql += " ORDER BY origem, chave_indicador"

    with conectar() as conexao:
        with conexao.cursor(row_factory=dict_row) as cursor:
            cursor.execute(sql, parametros)
            indicadores = cursor.fetchall()

    for indicador in indicadores:
        if indicador["valor"] is not None:
            indicador["valor"] = float(indicador["valor"])

    return {
        "quantidade": len(indicadores),
        "indicadores": indicadores,
        "meta": {
            "fontes": ["PMAS Campinas 2026-2029", "PMS Campinas"],
            "observacao": (
                "Indicadores documentais com unidades e períodos "
                "distintos. Metas, atendimentos e quantidades "
                "não representam automaticamente vagas disponíveis. "
                "Alguns indicadores do PMS não são exclusivos "
                "da população idosa. Não somar valores "
                "de indicadores diferentes."
            ),
        },
    }
