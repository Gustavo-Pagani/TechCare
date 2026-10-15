

from pathlib import Path
import pandas as pd


# ============================================================
# 1. CAMINHOS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
PASTA_GERADOS = BASE_DIR / "Arquivos Gerados"

ENTRADA = PASTA_GERADOS / "pns_idosos_funcionalidade.csv"
SAIDA = PASTA_GERADOS / "pns_parametros_perfil_cuidado.csv"


# ============================================================
# 2. CONFIGURAÇÕES
# ============================================================

PERFIS = [
    "autonomo",
    "apoio_leve",
    "dependencia_parcial",
    "dependencia_elevada",
]

CRITERIOS = {
    "autonomo": (
        "Sem necessidade de ajuda em ABVD/AIVD e sem dificuldade "
        "nas atividades consideradas"
    ),
    "apoio_leve": (
        "Alguma dificuldade em ABVD/AIVD, mas sem necessidade "
        "de ajuda declarada"
    ),
    "dependencia_parcial": (
        "Necessidade de ajuda em AIVD, sem necessidade de ajuda em ABVD"
    ),
    "dependencia_elevada": (
        "Necessidade de ajuda em uma ou mais ABVD"
    ),
}


# ============================================================
# 3. FUNÇÃO PARA CALCULAR UM GRUPO
# ============================================================

def calcular_grupo(dados, faixa, sexo):
    """
    Calcula os quatro perfis dentro de um subconjunto da PNS.

    proporcao = soma dos pesos do perfil / soma dos pesos do grupo
    """

    resultado = []
    peso_total = dados["peso_amostral"].sum()
    n_total = len(dados)

    if n_total == 0 or peso_total <= 0:
        raise ValueError(
            f"Grupo sem observações válidas: faixa={faixa}, sexo={sexo}"
        )

    for perfil in PERFIS:
        parte = dados[dados["perfil_cuidado"] == perfil]

        n_perfil = len(parte)
        peso_perfil = parte["peso_amostral"].sum()
        proporcao = peso_perfil / peso_total

        resultado.append(
            {
                "faixa_etaria": faixa,
                "sexo": sexo,
                "perfil_cuidado": perfil,
                "n_amostra_grupo": n_total,
                "n_amostra_perfil": n_perfil,
                "peso_expandido_grupo": round(peso_total, 2),
                "peso_expandido_perfil": round(peso_perfil, 2),
                "proporcao": round(proporcao, 6),
                "percentual": round(proporcao * 100, 2),
                "criterio_perfil": CRITERIOS[perfil],
                "fonte": "PNS 2019 - IBGE",
            }
        )

    return resultado


# ============================================================
# 4. LER A BASE FILTRADA
# ============================================================

if not ENTRADA.exists():
    raise FileNotFoundError(
        "Execute primeiro o script 01_ler_filtrar_pns.py."
    )

print("Lendo os idosos filtrados da PNS 2019...")
pns = pd.read_csv(ENTRADA)

colunas_obrigatorias = {
    "faixa_etaria",
    "sexo",
    "peso_amostral",
    "perfil_cuidado",
}

faltantes = colunas_obrigatorias - set(pns.columns)
if faltantes:
    raise ValueError(
        "Colunas ausentes no arquivo filtrado: "
        + ", ".join(sorted(faltantes))
    )

pns["peso_amostral"] = pd.to_numeric(
    pns["peso_amostral"],
    errors="raise",
)


# ============================================================
# 5. CALCULAR OS PARÂMETROS
# ============================================================

print("Calculando parâmetros ponderados de cuidado...")
linhas = []

# A) Faixa etária + sexo.
for faixa in ["60-64", "65-69", "70-74", "75+"]:
    for sexo in ["Homem", "Mulher"]:
        grupo = pns[
            (pns["faixa_etaria"] == faixa)
            & (pns["sexo"] == sexo)
        ]
        linhas.extend(calcular_grupo(grupo, faixa, sexo))

# B) Faixa etária, ambos os sexos.
for faixa in ["60-64", "65-69", "70-74", "75+"]:
    grupo = pns[pns["faixa_etaria"] == faixa]
    linhas.extend(calcular_grupo(grupo, faixa, "Todos"))

# C) Total 60+ por sexo.
for sexo in ["Homem", "Mulher"]:
    grupo = pns[pns["sexo"] == sexo]
    linhas.extend(calcular_grupo(grupo, "60+", sexo))

# D) Total geral 60+.
linhas.extend(calcular_grupo(pns, "60+", "Todos"))

parametros = pd.DataFrame(linhas)


# ============================================================
# 6. SALVAR
# ============================================================

parametros.to_csv(
    SAIDA,
    index=False,
    encoding="utf-8-sig",
)


# ============================================================
# 7. MOSTRAR UM RESUMO
# ============================================================

print()
print("=" * 64)
print("ETAPA 7 - PARÂMETROS DE CUIDADO GERADOS")
print("=" * 64)
print(f"Linhas geradas: {len(parametros)}")
print()
print("Perfil geral da população 60+ (ponderado):")

resumo = parametros[
    (parametros["faixa_etaria"] == "60+")
    & (parametros["sexo"] == "Todos")
]

for _, linha in resumo.iterrows():
    print(
        f"- {linha['perfil_cuidado']}: "
        f"{linha['percentual']:.2f}%"
    )

print()
print(f"Arquivo gerado: {SAIDA.name}")
