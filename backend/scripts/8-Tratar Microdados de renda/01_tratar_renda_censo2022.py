
from pathlib import Path
import csv
import zipfile
import pandas as pd


# ============================================================
# 1. CAMINHOS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

PASTA_ORIGINAIS = BASE_DIR / "Arquivos Originais"
PASTA_GERADOS = BASE_DIR / "Arquivos Gerados"

PASTA_GERADOS.mkdir(parents=True, exist_ok=True)

ARQUIVO_CSV = (
    PASTA_ORIGINAIS
    / "Agregados_por_setores_renda_responsavel_BR.csv"
)

ARQUIVO_ZIP = (
    PASTA_ORIGINAIS
    / "Agregados_por_setores_renda_responsavel_BR_20260508_csv.zip"
)

SAIDA = (
    PASTA_GERADOS
    / "renda_setores_campinas.csv"
)


# ============================================================
# 2. CONFIGURAÇÃO
# ============================================================

CODIGO_MUNICIPIO_CAMPINAS = "3509502"

COLUNAS_IBGE = [
    "CD_SETOR",
    "V06001",
    "V06002",
    "V06003",
    "V06004",
    "V06005",
]

RENOMEAR = {
    "CD_SETOR": "codigo_setor",
    "V06001": "responsaveis_domicilios_ocupados",
    "V06002": "moradores_domicilios_ocupados",
    "V06003": "variancia_moradores",
    "V06004": "renda_media_responsavel",
    "V06005": "variancia_renda_responsavel",
}


# ============================================================
# 3. DESCOBRIR CODIFICAÇÃO E SEPARADOR
# ============================================================

def descobrir_formato(caminho):
    """
    O IBGE costuma usar CSV com ';' e números com vírgula decimal.
    Mesmo assim, o script detecta o separador para nao dar sorte pro azar
    """

    codificacoes = [
        "utf-8-sig",
        "latin1",
        "cp1252",
    ]

    for encoding in codificacoes:
        try:
            with open(
                caminho,
                "r",
                encoding=encoding,
                newline="",
            ) as arquivo:
                primeira_linha = arquivo.readline()

            separadores = [";", ",", "\t", "|"]

            melhor = max(
                separadores,
                key=lambda sep: primeira_linha.count(sep),
            )

            if primeira_linha.count(melhor) >= 1:
                return encoding, melhor

        except UnicodeDecodeError:
            continue

    raise RuntimeError(
        "Não consegui identificar a codificação/separador "
        "do CSV oficial."
    )


# ============================================================
# 4. CONVERTER NÚMEROS DO IBGE
# ============================================================

def converter_numero(valor):
    """
    Converte textos numéricos do CSV para número.

    Símbolos que representam ausência de valor permanecem como NA.
    """

    if pd.isna(valor):
        return pd.NA

    texto = str(valor).strip().replace('"', "")

    if texto in {
        "",
        ".",
        "-",
        "X",
        "x",
        "...",
        "NA",
        "N/A",
    }:
        return pd.NA

    # Formato brasileiro:
    # 1.234,56 -> 1234.56
    if "," in texto:
        texto = texto.replace(".", "")
        texto = texto.replace(",", ".")

    try:
        return float(texto)
    except ValueError:
        return pd.NA


# ============================================================
# 5. LEITURA DO ARQUIVO
# ============================================================

encoding, separador = descobrir_formato(ARQUIVO_CSV)

print("Lendo a base oficial de renda do IBGE...")
print(f"Codificação detectada: {encoding}")
print(f"Separador detectado: {repr(separador)}")

cabecalho = pd.read_csv(
    ARQUIVO_CSV,
    sep=separador,
    encoding=encoding,
    nrows=0,
)

# Padroniza nomes, pois alguns arquivos podem variar em maiúsculas.
mapa_colunas = {
    str(coluna).strip().upper(): coluna
    for coluna in cabecalho.columns
}

faltantes = [
    coluna
    for coluna in COLUNAS_IBGE
    if coluna not in mapa_colunas
]

if faltantes:
    raise ValueError(
        "A estrutura do arquivo oficial mudou.\n"
        "Colunas esperadas não encontradas: "
        + ", ".join(faltantes)
    )

usecols_reais = [
    mapa_colunas[coluna]
    for coluna in COLUNAS_IBGE
]

dados = pd.read_csv(
    ARQUIVO_CSV,
    sep=separador,
    encoding=encoding,
    dtype=str,
    usecols=usecols_reais,
)

# Renomeia para o padrão esperado antes de continuar.
dados = dados.rename(
    columns={
        mapa_colunas[chave]: chave
        for chave in COLUNAS_IBGE
    }
)


# ============================================================
# 7. FILTRAR CAMPINAS
# ============================================================

print("Filtrando os setores censitários de Campinas...")

dados["CD_SETOR"] = (
    dados["CD_SETOR"]
    .astype(str)
    .str.replace(".0", "", regex=False)
    .str.strip()
)

campinas = dados[
    dados["CD_SETOR"].str.startswith(
        CODIGO_MUNICIPIO_CAMPINAS,
        na=False,
    )
].copy()

if campinas.empty:
    raise ValueError(
        "Nenhum setor de Campinas foi encontrado. "
        "Verifique se o arquivo baixado é o arquivo correto do IBGE."
    )


# ============================================================
# 8. PADRONIZAR VARIÁVEIS
# ============================================================

print("Padronizando as variáveis de renda...")

for coluna in [
    "V06001",
    "V06002",
    "V06003",
    "V06004",
    "V06005",
]:
    campinas[coluna] = campinas[coluna].apply(
        converter_numero
    )

# As duas primeiras são contagens.
for coluna in ["V06001", "V06002"]:
    campinas[coluna] = (
        pd.to_numeric(
            campinas[coluna],
            errors="coerce",
        )
        .round()
        .astype("Int64")
    )

# As demais permanecem numéricas com casas decimais.
for coluna in [
    "V06003",
    "V06004",
    "V06005",
]:
    campinas[coluna] = pd.to_numeric(
        campinas[coluna],
        errors="coerce",
    )


# ============================================================
# 9. RENOMEAR PARA NOMES CLAROS
# ============================================================

campinas = campinas.rename(
    columns=RENOMEAR
)

campinas = campinas[
    [
        "codigo_setor",
        "responsaveis_domicilios_ocupados",
        "moradores_domicilios_ocupados",
        "variancia_moradores",
        "renda_media_responsavel",
        "variancia_renda_responsavel",
    ]
].copy()

campinas = (
    campinas
    .sort_values("codigo_setor")
    .reset_index(drop=True)
)


# ============================================================
# 10. SALVAR
# ============================================================

campinas.to_csv(
    SAIDA,
    index=False,
    encoding="utf-8-sig",
)


# ============================================================
# 11. RESUMO
# ============================================================

print()
print("=" * 60)
print("ETAPA 8 - TRATAMENTO DE RENDA CONCLUÍDO")
print("=" * 60)
print(
    f"Setores de Campinas com registro publicado: "
    f"{len(campinas)}"
)
print()
print("Arquivo gerado:")
print(f"- {SAIDA.name}")
print()
print(
    "Importante: a renda é do responsável pelo domicílio, "
    "não renda individual dos idosos."
)
print(
    "A relação setor -> APG será feita posteriormente "
    "na etapa de integração."
)
print()

