import geopandas as gpd
import pandas as pd
from pathlib import Path
from shapely.geometry import MultiPolygon


# 1 - CAMINHOS
# Estes caminhos funcionam na estrutura do pacote descompactado.
# Se as pastas estiverem em outro lugar, altere somente estas duas linhas.
pasta_entrada = Path(__file__).resolve().parents[3] / "APG_Campinas_Originais"
pasta_saida = Path(__file__).resolve().parents[3] / "arquivos_gerados"

arquivo_entrada = pasta_entrada / "5298d4b2-fc97-84c8-73f0-000028777e69.shp"
arquivo_saida_gpkg = pasta_saida / "apg_campinas_tratada.gpkg"
arquivo_saida_csv = pasta_saida / "apg_campinas_atributos.csv"

if not pasta_saida.is_dir():
    raise ValueError("Crie a pasta de saída antes de executar o script.")


# 2 - LER O SHAPEFILE
print("Lendo Shapefile original das APGs...")
apgs = gpd.read_file(arquivo_entrada)
print(f"Arquivo carregado. Quantidade de APGs: {len(apgs)}")


# 3 - SELECIONAR COLUNAS
colunas = [
    "ID", "APG", "NOME_COMPL",
    "POP_1970", "POP_1980", "POP_1991", "POP_1996",
    "POP_2000", "POP_2010", "POP_2022", "geometry"
]
apgs = apgs[colunas].copy()


# 4 - RENOMEAR COLUNAS
apgs = apgs.rename(columns={
    "ID": "id_apg",
    "APG": "codigo_apg",
    "NOME_COMPL": "nome_apg",
    "POP_1970": "pop_1970",
    "POP_1980": "pop_1980",
    "POP_1991": "pop_1991",
    "POP_1996": "pop_1996",
    "POP_2000": "pop_2000",
    "POP_2010": "pop_2010",
    "POP_2022": "pop_2022"
})


# 5 - PADRONIZAR TIPOS DOS DADOS
colunas_texto = ["codigo_apg", "nome_apg"]
for coluna in colunas_texto:
    # O tipo string mantém valores ausentes identificáveis na conferência.
    apgs[coluna] = apgs[coluna].astype("string").str.strip()

colunas_inteiras = [
    "id_apg", "pop_1970", "pop_1980", "pop_1991",
    "pop_1996", "pop_2000", "pop_2010", "pop_2022"
]
for coluna in colunas_inteiras:
    numeros = pd.to_numeric(apgs[coluna], errors="raise")
    # Interrompe em vez de arredondar ou descartar casas decimais.
    if numeros.isna().any() or (numeros % 1 != 0).any():
        raise ValueError(f"A coluna {coluna} contém valores ausentes ou não inteiros.")
    apgs[coluna] = numeros.astype("int64")


# 6 - PADRONIZAR O CRS
crs_padrao = "EPSG:31983"
print(f"CRS atual: {apgs.crs}")
if apgs.crs is None:
    raise ValueError("O arquivo não possui CRS definido.")
if apgs.crs.to_epsg() != 31983:
    apgs = apgs.to_crs(crs_padrao)
    print(f"CRS convertido para {crs_padrao}.")
else:
    print("CRS já está no padrão.")


# 7 - PADRONIZAR GEOMETRIA (SEM CORREÇÃO AUTOMÁTICA)
def transformar_multipolygon(geometria):
    if geometria is None or geometria.is_empty:
        return geometria  # A conferência final vai detectar o problema.
    if geometria.geom_type == "Polygon":
        return MultiPolygon([geometria])
    if geometria.geom_type == "MultiPolygon":
        return geometria
    raise ValueError(f"Tipo de geometria inesperado: {geometria.geom_type}")


apgs["geometry"] = apgs.geometry.apply(transformar_multipolygon)


# 8 - CONFERÊNCIA FINAL, ANTES DE SALVAR
invalidas = (~apgs.geometry.is_valid).sum()
vazias = apgs.geometry.is_empty.sum()
nulas = apgs.geometry.isna().sum()
print(f"Geometrias inválidas: {invalidas}")
print(f"Geometrias vazias: {vazias}")
print(f"Geometrias nulas: {nulas}")

if invalidas > 0 or vazias > 0 or nulas > 0:
    raise ValueError("Problema nas geometrias. Confira a base antes de continuar.")
if len(apgs) != 17:
    raise ValueError(f"Quantidade de APGs diferente de 17: {len(apgs)}")
for coluna in colunas_texto:
    if apgs[coluna].isna().any() or apgs[coluna].eq("").any():
        raise ValueError(f"A coluna {coluna} contém valores vazios.")
if apgs["codigo_apg"].nunique() != 17:
    raise ValueError("Existem APGs duplicadas.")
if apgs["pop_2022"].sum() != 1139047:
    raise ValueError("A soma de pop_2022 é diferente de 1.139.047.")
if apgs.crs.to_epsg() != 31983 or not apgs.geom_type.eq("MultiPolygon").all():
    raise ValueError("CRS ou tipo geométrico fora do padrão.")
print("Conferência final concluída com sucesso.")


# 9 - SALVAR SOMENTE OS DOIS ARQUIVOS FINAIS
apgs.to_file(
    arquivo_saida_gpkg,
    layer="apg_campinas",
    driver="GPKG",
    index=False
)
atributos = apgs.drop(columns="geometry").copy()
atributos.to_csv(arquivo_saida_csv, index=False, encoding="utf-8-sig")

print("\nEtapa 2 concluída com sucesso.")
print(f"GPKG criado: {arquivo_saida_gpkg}")
print(f"CSV criado: {arquivo_saida_csv}")
