from pathlib import Path
import pandas as pd


# ============================================================
# 1. CAMINHOS
# ============================================================

# Pasta em que este arquivo Python está localizado.
BASE_DIR = Path(__file__).resolve().parent

# Pasta com os arquivos originais.
PASTA_ORIGINAIS = BASE_DIR / "Arquivos Originais"

# Pasta em que os arquivos tratados serão criados.
PASTA_GERADOS = BASE_DIR / "Arquivos Gerados"

# Garante que a pasta exista.
PASTA_GERADOS.mkdir(parents=True, exist_ok=True)


# Arquivos de entrada.
ARQUIVO_DICIONARIO = (
    PASTA_ORIGINAIS / "dic_evolucao_esp_sexoidade.csv"
)

ARQUIVO_CRESCIMENTO = (
    PASTA_ORIGINAIS / "evolucao_esp_crescimento_2000_50.csv"
)

ARQUIVO_SEXO_IDADE = (
    PASTA_ORIGINAIS / "evolucao_esp_sexoidade_2000_50.csv"
)


# Arquivos de saída.
SAIDA_CRESCIMENTO = (
    PASTA_GERADOS / "seade_campinas_crescimento.csv"
)

SAIDA_SEXO_IDADE = (
    PASTA_GERADOS / "seade_campinas_sexo_idade.csv"
)

SAIDA_PROJECOES = (
    PASTA_GERADOS / "seade_projecoes_campinas.csv"
)


# ============================================================
# 2. CONFIGURAÇÕES DO TECHCARE
# ============================================================

# Código IBGE de Campinas.
CODIGO_CAMPINAS = "3509502"

# Anos do SEADE que serão usados como cenários futuros.
# 2022 não está disponível nesta fonte.
ANOS_PROJECAO = [2020, 2030, 2040, 2050]

# Faixas que compõem população com 60 anos ou mais.
FAIXAS_60_MAIS = [
    "60 a 64",
    "65 a 69",
    "70 a 74",
    "75 e +",
]


# ============================================================
# 3. FUNÇÕES AUXILIARES
# ============================================================

def texto_inteiro(valor):
    """
    Converte números no formato brasileiro usado no arquivo.

    Exemplo:
        "1.223.394" -> 1223394
    """
    if pd.isna(valor):
        return pd.NA

    texto = str(valor).strip()
    texto = texto.replace(".", "")

    return int(texto)


def texto_decimal(valor):
    """
    Converte decimal com vírgula para float.]
    """
    if pd.isna(valor):
        return pd.NA

    texto = str(valor).strip()
    texto = texto.replace(".", "")
    texto = texto.replace(",", ".")

    return float(texto)


# ============================================================
# 4. LER OS ARQUIVOS ORIGINAIS
# ============================================================

print("Lendo os arquivos originais do SEADE...")

dicionario = pd.read_csv(
    ARQUIVO_DICIONARIO,
    sep=";",
    encoding="cp1252",
    dtype=str,
)

crescimento = pd.read_csv(
    ARQUIVO_CRESCIMENTO,
    sep=";",
    encoding="cp1252",
    dtype=str,
)

sexo_idade = pd.read_csv(
    ARQUIVO_SEXO_IDADE,
    sep=";",
    encoding="cp1252",
    dtype=str,
)


# ============================================================
# 5. CONFERIR A ESTRUTURA DOS ARQUIVOS
# ============================================================

# O dicionário serve para documentar a origem das variáveis.
variaveis_dicionario = set(
    dicionario["variavel"].astype(str).str.strip()
)

variaveis_esperadas = {
    "ano",
    "cod_ibge",
    "sexo",
    "idade",
    "populacao",
}

faltantes_dicionario = (
    variaveis_esperadas - variaveis_dicionario
)

if faltantes_dicionario:
    raise ValueError(
        "O dicionário do SEADE não possui todas as variáveis "
        f"esperadas: {sorted(faltantes_dicionario)}"
    )


colunas_sexo_idade = {
    "cod_ibge",
    "ano",
    "sexo",
    "faixa_etaria",
    "populacao",
}

faltantes_sexo_idade = (
    colunas_sexo_idade - set(sexo_idade.columns)
)

if faltantes_sexo_idade:
    raise ValueError(
        "Colunas ausentes no arquivo sexo/idade: "
        f"{sorted(faltantes_sexo_idade)}"
    )

# ============================================================
# 6. FILTRAR CAMPINAS
# ============================================================

print("Filtrando Campinas...")

crescimento_campinas = crescimento[
    crescimento["cod_ibge"].astype(str).str.strip()
    == CODIGO_CAMPINAS
].copy()

sexo_idade_campinas = sexo_idade[
    sexo_idade["cod_ibge"].astype(str).str.strip()
    == CODIGO_CAMPINAS
].copy()


if len(crescimento_campinas) != 1:
    raise ValueError(
        "Esperava exatamente 1 linha de Campinas "
        "no arquivo de crescimento."
    )



# ============================================================
# 7. PADRONIZAR SEXO / IDADE
# ============================================================

print("Padronizando sexo, idade e população...")

# Remove espaços extras.
sexo_idade_campinas["sexo"] = (
    sexo_idade_campinas["sexo"]
    .astype(str)
    .str.strip()
)

sexo_idade_campinas["faixa_etaria"] = (
    sexo_idade_campinas["faixa_etaria"]
    .astype(str)
    .str.strip()
)

# Ano vira inteiro.
sexo_idade_campinas["ano"] = pd.to_numeric(
    sexo_idade_campinas["ano"],
    errors="raise",
).astype(int)

# População deixa de ser texto com ponto de milhar.
sexo_idade_campinas["populacao"] = (
    sexo_idade_campinas["populacao"]
    .apply(texto_inteiro)
    .astype("Int64")
)

# Mantém apenas as colunas necessárias.
sexo_idade_campinas = sexo_idade_campinas[
    [
        "cod_ibge",
        "ano",
        "sexo",
        "faixa_etaria",
        "populacao",
    ]
].copy()

# Organiza o resultado.
sexo_idade_campinas = sexo_idade_campinas.sort_values(
    ["ano", "sexo", "faixa_etaria"]
).reset_index(drop=True)


# ============================================================
# 8. PADRONIZAR CRESCIMENTO
# ============================================================

print("Padronizando crescimento populacional...")

# Colunas de população.
colunas_populacao = [
    coluna
    for coluna in crescimento_campinas.columns
    if coluna.startswith("populacao_")
]

for coluna in colunas_populacao:
    crescimento_campinas[coluna] = (
        crescimento_campinas[coluna]
        .apply(texto_inteiro)
        .astype("Int64")
    )

# Colunas de taxa de crescimento.
colunas_taxa = [
    coluna
    for coluna in crescimento_campinas.columns
    if coluna.startswith("tx_crescimentopop_")
]

for coluna in colunas_taxa:
    crescimento_campinas[coluna] = (
        crescimento_campinas[coluna]
        .apply(texto_decimal)
        .astype(float)
    )

crescimento_campinas = (
    crescimento_campinas.reset_index(drop=True)
)


# ============================================================
# 9. GERAR A TABELA DE PROJEÇÕES DO TECHCARE
# ============================================================

print("Gerando os cenários principais do TechCare...")

# Ligação entre cada ano e a taxa do período imediatamente anterior.
COLUNA_TAXA_POR_ANO = {
    2020: "tx_crescimentopop_2010/2020",
    2030: "tx_crescimentopop_2020/2030",
    2040: "tx_crescimentopop_2030/2040",
    2050: "tx_crescimentopop_2040/2050",
}

linha_crescimento = crescimento_campinas.iloc[0]

projecoes = []

for ano in ANOS_PROJECAO:

    dados_ano = sexo_idade_campinas[
        sexo_idade_campinas["ano"] == ano
    ].copy()

    if dados_ano.empty:
        raise ValueError(
            f"Não existem registros de Campinas para o ano {ano}."
        )

    # População total oficial do arquivo de crescimento.
    populacao_total = int(
        linha_crescimento[f"populacao_{ano}"]
    )

    # População 60+.
    filtro_60 = dados_ano[
        "faixa_etaria"
    ].isin(FAIXAS_60_MAIS)

    populacao_60_mais = int(
        dados_ano.loc[
            filtro_60,
            "populacao",
        ].sum()
    )

    populacao_75_mais = int(
        dados_ano.loc[
            dados_ano["faixa_etaria"] == "75 e +",
            "populacao",
        ].sum()
    )

    homens_60_mais = int(
        dados_ano.loc[
            filtro_60
            & (dados_ano["sexo"] == "Homens"),
            "populacao",
        ].sum()
    )

    mulheres_60_mais = int(
        dados_ano.loc[
            filtro_60
            & (dados_ano["sexo"] == "Mulheres"),
            "populacao",
        ].sum()
    )

    percentual_60_mais = round(
        populacao_60_mais
        / populacao_total
        * 100,
        2,
    )

    percentual_75_mais = round(
        populacao_75_mais
        / populacao_total
        * 100,
        2,
    )

    coluna_taxa = COLUNA_TAXA_POR_ANO[ano]

    taxa_crescimento = float(
        linha_crescimento[coluna_taxa]
    )

    projecoes.append(
        {
            "ano": ano,
            "populacao_total": populacao_total,
            "populacao_60_mais": populacao_60_mais,
            "percentual_60_mais": percentual_60_mais,
            "populacao_75_mais": populacao_75_mais,
            "percentual_75_mais": percentual_75_mais,
            "homens_60_mais": homens_60_mais,
            "mulheres_60_mais": mulheres_60_mais,
            "taxa_crescimento_periodo": taxa_crescimento,
            "fonte": "Fundacao Seade",
        }
    )


projecoes_campinas = pd.DataFrame(projecoes)


# ============================================================
# 10. SALVAR OS ARQUIVOS GERADOS
# ============================================================

print("Salvando arquivos tratados...")

crescimento_campinas.to_csv(
    SAIDA_CRESCIMENTO,
    index=False,
    encoding="utf-8-sig",
)

sexo_idade_campinas.to_csv(
    SAIDA_SEXO_IDADE,
    index=False,
    encoding="utf-8-sig",
)

projecoes_campinas.to_csv(
    SAIDA_PROJECOES,
    index=False,
    encoding="utf-8-sig",
)


# ============================================================
# 11. RESUMO
# ============================================================

print()
print("=" * 60)
print("ETAPA 6 - TRATAMENTO SEADE CONCLUÍDO")
print("=" * 60)
print(
    f"Registros sexo/idade de Campinas: "
    f"{len(sexo_idade_campinas)}"
)
print(
    f"Anos disponíveis: "
    f"{sorted(sexo_idade_campinas['ano'].unique())}"
)
print(
    f"Linhas da tabela de cenários: "
    f"{len(projecoes_campinas)}"
)
print()
print("Arquivos gerados:")
print(f"- {SAIDA_CRESCIMENTO.name}")
print(f"- {SAIDA_SEXO_IDADE.name}")
print(f"- {SAIDA_PROJECOES.name}")
print()
print(
    "Observação: 2022 deve vir do Censo 2022. "
    "O SEADE não possui 2022 nesta base."
)
print(
    "Observação: a maior faixa do SEADE é 75 e +. "
    "Não foi criada população 80+."
)
