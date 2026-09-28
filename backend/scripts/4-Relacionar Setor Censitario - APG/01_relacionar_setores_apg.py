from pathlib import Path
import geopandas as gpd
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[1]

PASTA_ENTRADA = BASE_DIR / "01_entrada"
PASTA_SAIDA = BASE_DIR / "03_resultados"

ARQUIVO_SETORES = PASTA_ENTRADA / "setores_campinas.gpkg"
ARQUIVO_APGS = PASTA_ENTRADA / "apg_campinas_tratada.gpkg"

SAIDA_GPKG = PASTA_SAIDA / "setores_campinas_com_apg.gpkg"
SAIDA_CSV = PASTA_SAIDA / "setores_campinas_com_apg_atributos.csv"
SAIDA_RELACAO = PASTA_SAIDA / "relacao_setor_apg.csv"

PASTA_SAIDA.mkdir(parents=True, exist_ok=True)

print("Lendo os arquivos...")
setores = gpd.read_file(ARQUIVO_SETORES)
apgs = gpd.read_file(ARQUIVO_APGS)

if setores.crs is None:
    raise ValueError("O arquivo de setores não possui CRS definido.")

if apgs.crs is None:
    raise ValueError("O arquivo de APGs não possui CRS definido.")

if setores.crs != apgs.crs:
    print(f"CRS diferentes. Convertendo APGs de {apgs.crs} para {setores.crs}...")
    apgs = apgs.to_crs(setores.crs)

colunas_setores = ["codigo_setor", "geometry"]
colunas_apgs = ["id_apg", "codigo_apg", "nome_apg", "geometry"]

for coluna in colunas_setores:
    if coluna not in setores.columns:
        raise ValueError(f"Coluna ausente nos setores: {coluna}")

for coluna in colunas_apgs:
    if coluna not in apgs.columns:
        raise ValueError(f"Coluna ausente nas APGs: {coluna}")

setores_aux = setores[["codigo_setor", "geometry"]].reset_index(drop=True)
setores_aux = setores_aux.reset_index(names="setor_idx")

apgs_aux = apgs[["id_apg", "codigo_apg", "nome_apg", "geometry"]].reset_index(drop=True)
apgs_aux = apgs_aux.reset_index(names="apg_idx")

print("Buscando interseções entre setores e APGs...")

candidatos = gpd.sjoin(
    setores_aux,
    apgs_aux,
    how="left",
    predicate="intersects"
).reset_index(drop=True)

if candidatos["id_apg"].isna().any():
    quantidade = candidatos["id_apg"].isna().sum()
    raise ValueError(f"Foram encontrados {quantidade} setores sem interseção com nenhuma APG.")

print("Calculando áreas de interseção...")

areas_intersecao = []

for _, linha in candidatos.iterrows():
    indice_setor = int(linha["setor_idx"])
    indice_apg = int(linha["apg_idx"])

    geometria_setor = setores.geometry.iloc[indice_setor]
    geometria_apg = apgs.geometry.iloc[indice_apg]

    area = geometria_setor.intersection(geometria_apg).area
    areas_intersecao.append(area)

candidatos["area_intersecao_m2"] = areas_intersecao

indices_maior_area = (
    candidatos
    .groupby("setor_idx")["area_intersecao_m2"]
    .idxmax()
)

melhor_relacao = candidatos.loc[indices_maior_area].copy()

areas_setores = setores.geometry.area.reset_index(drop=True)

melhor_relacao["area_setor_m2"] = (
    melhor_relacao["setor_idx"]
    .map(areas_setores.to_dict())
)

melhor_relacao["percentual_area_na_apg"] = (
    melhor_relacao["area_intersecao_m2"]
    / melhor_relacao["area_setor_m2"]
    * 100
)

colunas_relacao = [
    "setor_idx",
    "id_apg",
    "codigo_apg",
    "nome_apg",
    "percentual_area_na_apg"
]

resultado = setores.reset_index(drop=True).reset_index(names="setor_idx")

resultado = resultado.merge(
    melhor_relacao[colunas_relacao],
    on="setor_idx",
    how="left"
)

resultado = resultado.drop(columns=["setor_idx"])
resultado["percentual_area_na_apg"] = resultado["percentual_area_na_apg"].round(6)

print("Salvando resultados...")

resultado.to_file(SAIDA_GPKG, driver="GPKG")

resultado.drop(columns="geometry").to_csv(
    SAIDA_CSV,
    index=False,
    encoding="utf-8-sig"
)

resultado[
    [
        "codigo_setor",
        "id_apg",
        "codigo_apg",
        "nome_apg",
        "percentual_area_na_apg"
    ]
].to_csv(
    SAIDA_RELACAO,
    index=False,
    encoding="utf-8-sig"
)

print()
print("ETAPA 4 CONCLUÍDA")
print(f"Setores relacionados: {len(resultado)}")
print(f"APGs encontradas: {resultado['nome_apg'].nunique()}")
print(f"Arquivo geográfico: {SAIDA_GPKG.name}")
print(f"Arquivo de atributos: {SAIDA_CSV.name}")
print(f"Relação setor -> APG: {SAIDA_RELACAO.name}")
