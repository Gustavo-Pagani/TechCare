"""Prepara APGs, setores censitarios e dados demograficos/renda.

Nao define chaves SQL nem cria tabelas. Preserva os identificadores existentes.
"""
from pathlib import Path
import geopandas as gpd
import pandas as pd

PASTA = Path(__file__).resolve().parent
ORIGINAIS = PASTA / "Arquivos Originais"
GERADOS = PASTA / "Arquivos Gerados"
GERADOS.mkdir(exist_ok=True)


def salvar_geografia(nome_entrada, nome_saida):
    dados = gpd.read_file(ORIGINAIS / nome_entrada)

    # Os mapas integrados do projeto estao no sistema de coordenadas 31983.
    if dados.crs is None or dados.crs.to_epsg() != 31983:
        raise ValueError(f"CRS diferente de EPSG:31983 em {nome_entrada}")

    # WKT e texto com o contorno geografico: na Etapa 13, o PostGIS
    # transformara esse texto em geometria novamente.
    dados["geometry_wkt"] = dados.geometry.to_wkt(rounding_precision=-1)
    dados = pd.DataFrame(dados.drop(columns="geometry"))
    dados.to_csv(GERADOS / nome_saida, index=False, encoding="utf-8")
    print(f"{nome_saida}: {len(dados)} linhas")


salvar_geografia("apg_integrada.gpkg", "apg.csv")
salvar_geografia("setor_censitario_integrado.gpkg", "setor_censitario.csv")

# Le os dados como texto para nao perder os codigos do IBGE.
dados = pd.read_csv(
    ORIGINAIS / "dados_setor_2022_integrados.csv", dtype=str
)

# Colunas de contagem devem ser inteiros ou ficar vazias quando o dado
# nao foi publicado. Exemplo: 104.0 passa para 104; vazio continua vazio.
colunas_inteiras = [
    "populacao_total", "total_domicilios", "domicilios_particulares",
    "domicilios_coletivos", "domicilios_particulares_ocupados",
    "moradores_demografia", "homens_total", "mulheres_total",
    "responsaveis_domicilios_ocupados", "moradores_domicilios_ocupados",
    "pop_60_mais", "homens_60_mais", "mulheres_60_mais",
]
colunas_inteiras += [
    coluna for coluna in dados.columns
    if coluna.startswith(("pop_", "homens_", "mulheres_"))
]

for coluna in set(colunas_inteiras):
    if coluna in dados.columns:
        dados[coluna] = pd.to_numeric(dados[coluna], errors="raise").astype("Int64")

# Verdadeiro/falso em um unico formato facil de importar futuramente.
for coluna in [
    "sem_linha_demografica", "sem_demografia_pop_zero",
    "revisar_sem_demografia", "possui_valor_inibido",
    "registro_renda_publicado",
]:
    if coluna in dados.columns:
        dados[coluna] = dados[coluna].str.lower()

# IMPORTANTE: os setores sem populacao 60+ publicada permanecem vazios.
# Nao estimamos nem substituimos por zero.
dados.to_csv(
    GERADOS / "dados_setor_2022.csv", index=False, encoding="utf-8"
)
print(f"dados_setor_2022.csv: {len(dados)} linhas")
