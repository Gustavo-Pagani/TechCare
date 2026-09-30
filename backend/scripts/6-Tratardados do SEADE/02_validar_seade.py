
from pathlib import Path
import pandas as pd


# ============================================================
# 1. CAMINHOS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

PASTA_GERADOS = BASE_DIR / "Arquivos Gerados"

ARQUIVO_CRESCIMENTO = (
    PASTA_GERADOS / "seade_campinas_crescimento.csv"
)

ARQUIVO_SEXO_IDADE = (
    PASTA_GERADOS / "seade_campinas_sexo_idade.csv"
)

ARQUIVO_PROJECOES = (
    PASTA_GERADOS / "seade_projecoes_campinas.csv"
)

ARQUIVO_RELATORIO = (
    PASTA_GERADOS / "VALIDACAO_ETAPA6.txt"
)


CODIGO_CAMPINAS = "3509502"

ANOS_ESPERADOS = [
    2000,
    2005,
    2010,
    2015,
    2020,
    2025,
    2030,
    2035,
    2040,
    2045,
    2050,
]

ANOS_PROJECAO = [
    2020,
    2030,
    2040,
    2050,
]

SEXOS_ESPERADOS = {
    "Homens",
    "Mulheres",
}

FAIXAS_ESPERADAS = {
    "00 a 04",
    "05 a 09",
    "10 a 14",
    "15 a 19",
    "20 a 24",
    "25 a 29",
    "30 a 34",
    "35 a 39",
    "40 a 44",
    "45 a 49",
    "50 a 54",
    "55 a 59",
    "60 a 64",
    "65 a 69",
    "70 a 74",
    "75 e +",
}

FAIXAS_60_MAIS = {
    "60 a 64",
    "65 a 69",
    "70 a 74",
    "75 e +",
}


# ============================================================
# 2. VERIFICAR SE OS ARQUIVOS EXISTEM
# ============================================================

arquivos = [
    ARQUIVO_CRESCIMENTO,
    ARQUIVO_SEXO_IDADE,
    ARQUIVO_PROJECOES,
]

faltantes = [
    arquivo.name
    for arquivo in arquivos
    if not arquivo.exists()
]

if faltantes:
    raise FileNotFoundError(
        "Execute primeiro o script 01_tratar_seade.py. "
        "Arquivos ausentes: "
        + ", ".join(faltantes)
    )


# ============================================================
# 3. LER OS ARQUIVOS GERADOS
# ============================================================

crescimento = pd.read_csv(
    ARQUIVO_CRESCIMENTO,
    dtype={"cod_ibge": str},
)

sexo_idade = pd.read_csv(
    ARQUIVO_SEXO_IDADE,
    dtype={"cod_ibge": str},
)

projecoes = pd.read_csv(
    ARQUIVO_PROJECOES,
)


# ============================================================
# 4. LISTA DE PROBLEMAS
# ============================================================

problemas = []


# ============================================================
# 5. VALIDAR CRESCIMENTO
# ============================================================

if len(crescimento) != 1:
    problemas.append(
        "A tabela de crescimento deveria possuir "
        "exatamente 1 linha para Campinas."
    )

if set(crescimento["cod_ibge"].astype(str)) != {
    CODIGO_CAMPINAS
}:
    problemas.append(
        "A tabela de crescimento possui código IBGE "
        "diferente de Campinas."
    )

if crescimento.isna().any().any():
    problemas.append(
        "Existem valores nulos na tabela de crescimento."
    )


# ============================================================
# 6. VALIDAR SEXO / IDADE
# ============================================================

# 11 anos x 2 sexos x 16 faixas = 352 registros.
REGISTROS_ESPERADOS = (
    len(ANOS_ESPERADOS)
    * len(SEXOS_ESPERADOS)
    * len(FAIXAS_ESPERADAS)
)

if len(sexo_idade) != REGISTROS_ESPERADOS:
    problemas.append(
        "Quantidade inesperada de registros em sexo/idade: "
        f"{len(sexo_idade)}. Esperado: {REGISTROS_ESPERADOS}."
    )

if set(sexo_idade["ano"].unique()) != set(ANOS_ESPERADOS):
    problemas.append(
        "Os anos da tabela sexo/idade não correspondem "
        "aos anos esperados."
    )

if set(sexo_idade["sexo"].unique()) != SEXOS_ESPERADOS:
    problemas.append(
        "Os valores da coluna sexo não correspondem "
        "a Homens e Mulheres."
    )

if set(sexo_idade["faixa_etaria"].unique()) != FAIXAS_ESPERADAS:
    problemas.append(
        "As faixas etárias não correspondem às "
        "16 faixas esperadas."
    )

if sexo_idade.isna().any().any():
    problemas.append(
        "Existem valores nulos na tabela sexo/idade."
    )

if (sexo_idade["populacao"] < 0).any():
    problemas.append(
        "Existem valores negativos de população."
    )

duplicados = sexo_idade.duplicated(
    subset=[
        "cod_ibge",
        "ano",
        "sexo",
        "faixa_etaria",
    ]
).sum()

if duplicados > 0:
    problemas.append(
        f"Foram encontrados {duplicados} registros duplicados "
        "em sexo/idade."
    )


# ============================================================
# 7. VALIDAR PROJEÇÕES
# ============================================================

if list(projecoes["ano"]) != ANOS_PROJECAO:
    problemas.append(
        "Os anos da tabela de projeções não correspondem "
        "a 2020, 2030, 2040 e 2050."
    )

if projecoes.isna().any().any():
    problemas.append(
        "Existem valores nulos na tabela de projeções."
    )

if (projecoes["populacao_total"] <= 0).any():
    problemas.append(
        "Existe população total inválida na tabela de projeções."
    )

if (
    projecoes["populacao_60_mais"]
    > projecoes["populacao_total"]
).any():
    problemas.append(
        "Existe população 60+ maior que a população total."
    )

if (
    projecoes["populacao_75_mais"]
    > projecoes["populacao_60_mais"]
).any():
    problemas.append(
        "Existe população 75+ maior que a população 60+."
    )


# ============================================================
# 8. CONFERIR TOTAIS E CÁLCULOS
# ============================================================

linha_crescimento = crescimento.iloc[0]

for ano in ANOS_PROJECAO:

    detalhe = sexo_idade[
        sexo_idade["ano"] == ano
    ]

    projecao = projecoes[
        projecoes["ano"] == ano
    ].iloc[0]

    # ----------------------------------------
    # População total
    # ----------------------------------------

    total_detalhado = int(
        detalhe["populacao"].sum()
    )

    total_crescimento = int(
        linha_crescimento[f"populacao_{ano}"]
    )

    total_projecao = int(
        projecao["populacao_total"]
    )

    if not (
        total_detalhado
        == total_crescimento
        == total_projecao
    ):
        problemas.append(
            f"Inconsistência na população total de {ano}."
        )

    # ----------------------------------------
    # População 60+
    # ----------------------------------------

    populacao_60 = int(
        detalhe.loc[
            detalhe["faixa_etaria"].isin(FAIXAS_60_MAIS),
            "populacao",
        ].sum()
    )

    if populacao_60 != int(
        projecao["populacao_60_mais"]
    ):
        problemas.append(
            f"Inconsistência na população 60+ de {ano}."
        )

    # ----------------------------------------
    # População 75+
    # ----------------------------------------

    populacao_75 = int(
        detalhe.loc[
            detalhe["faixa_etaria"] == "75 e +",
            "populacao",
        ].sum()
    )

    if populacao_75 != int(
        projecao["populacao_75_mais"]
    ):
        problemas.append(
            f"Inconsistência na população 75+ de {ano}."
        )

    # ----------------------------------------
    # Homens e mulheres 60+
    # ----------------------------------------

    homens_60 = int(
        detalhe.loc[
            detalhe["faixa_etaria"].isin(FAIXAS_60_MAIS)
            & (detalhe["sexo"] == "Homens"),
            "populacao",
        ].sum()
    )

    mulheres_60 = int(
        detalhe.loc[
            detalhe["faixa_etaria"].isin(FAIXAS_60_MAIS)
            & (detalhe["sexo"] == "Mulheres"),
            "populacao",
        ].sum()
    )

    if homens_60 != int(
        projecao["homens_60_mais"]
    ):
        problemas.append(
            f"Inconsistência nos homens 60+ de {ano}."
        )

    if mulheres_60 != int(
        projecao["mulheres_60_mais"]
    ):
        problemas.append(
            f"Inconsistência nas mulheres 60+ de {ano}."
        )


# ============================================================
# 9. CRIAR RELATÓRIO
# ============================================================

linhas = []

linhas.append(
    "VALIDAÇÃO - TECHCARE - ETAPA 6 - SEADE"
)
linhas.append("=" * 55)
linhas.append("")
linhas.append(
    f"Município: Campinas ({CODIGO_CAMPINAS})"
)
linhas.append(
    f"Registros sexo/idade: {len(sexo_idade)}"
)
linhas.append(
    "Anos disponíveis: "
    + ", ".join(
        str(ano)
        for ano in sorted(
            sexo_idade["ano"].unique()
        )
    )
)
linhas.append(
    "Cenários gerados: "
    + ", ".join(
        str(ano)
        for ano in ANOS_PROJECAO
    )
)
linhas.append(
    f"Sexos: {', '.join(sorted(SEXOS_ESPERADOS))}"
)
linhas.append(
    f"Quantidade de faixas etárias: "
    f"{len(FAIXAS_ESPERADAS)}"
)
linhas.append("")
linhas.append("LIMITAÇÕES DA FONTE")
linhas.append("-" * 55)
linhas.append(
    "- O arquivo SEADE não possui o ano de 2022."
)
linhas.append(
    "- O cenário 2022 do TechCare deve usar o Censo 2022."
)
linhas.append(
    "- A maior faixa etária disponível é 75 e +."
)
linhas.append(
    "- Esta etapa não cria nem estima população 80+."
)
linhas.append("")
linhas.append("RESULTADO")
linhas.append("-" * 55)

if problemas:
    linhas.append("VALIDAÇÃO COM PENDÊNCIAS")
    for problema in problemas:
        linhas.append(f"- {problema}")
else:
    linhas.append("VALIDAÇÃO OK")
    linhas.append(
        "Nenhuma inconsistência foi encontrada."
    )

texto_relatorio = "\n".join(linhas)

print(texto_relatorio)
print()
