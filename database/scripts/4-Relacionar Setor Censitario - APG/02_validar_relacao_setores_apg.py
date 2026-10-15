from pathlib import Path
import geopandas as gpd
import pandas as pd

BASE_DIR = Path(__file__).resolve().parents[1]

PASTA_SAIDA = BASE_DIR / "03_resultados"

ARQUIVO_RESULTADO = PASTA_SAIDA / "setores_campinas_com_apg.gpkg"
ARQUIVO_RELACAO = PASTA_SAIDA / "relacao_setor_apg.csv"
ARQUIVO_RELATORIO = PASTA_SAIDA / "VALIDACAO_ETAPA4.txt"

print("Lendo resultado da Etapa 4...")

setores = gpd.read_file(ARQUIVO_RESULTADO)
relacao = pd.read_csv(
    ARQUIVO_RELACAO,
    dtype={"codigo_setor": str},
    encoding="utf-8-sig"
)

problemas = []

if len(setores) != 2592:
    problemas.append(f"Quantidade de setores diferente do esperado: {len(setores)}")

duplicados = setores["codigo_setor"].duplicated().sum()

if duplicados > 0:
    problemas.append(f"Foram encontrados {duplicados} códigos de setor duplicados.")

sem_apg = setores[
    ["id_apg", "codigo_apg", "nome_apg"]
].isna().any(axis=1).sum()

if sem_apg > 0:
    problemas.append(f"Foram encontrados {sem_apg} setores sem APG.")

quantidade_apgs = setores["nome_apg"].nunique()

if quantidade_apgs != 17:
    problemas.append(f"Quantidade de APGs diferente do esperado: {quantidade_apgs}")

geometrias_nulas = setores.geometry.isna().sum()
geometrias_vazias = setores.geometry.is_empty.sum()
geometrias_invalidas = (~setores.geometry.is_valid).sum()

if geometrias_nulas > 0:
    problemas.append(f"Foram encontradas {geometrias_nulas} geometrias nulas.")

if geometrias_vazias > 0:
    problemas.append(f"Foram encontradas {geometrias_vazias} geometrias vazias.")

if geometrias_invalidas > 0:
    problemas.append(f"Foram encontradas {geometrias_invalidas} geometrias inválidas.")

percentual_minimo = setores["percentual_area_na_apg"].min()

if percentual_minimo < 50:
    problemas.append("Existe setor cuja APG escolhida cobre menos de 50% da área.")

contagem_apg = (
    setores
    .groupby(["id_apg", "codigo_apg", "nome_apg"])
    .size()
    .reset_index(name="quantidade_setores")
    .sort_values("nome_apg")
)

linhas = []

linhas.append("VALIDAÇÃO - ETAPA 4 - SETOR CENSITÁRIO -> APG")
linhas.append("=" * 55)
linhas.append("")
linhas.append(f"Total de setores: {len(setores)}")
linhas.append(f"Códigos de setor únicos: {setores['codigo_setor'].nunique()}")
linhas.append(f"Setores sem APG: {sem_apg}")
linhas.append(f"APGs encontradas: {quantidade_apgs}")
linhas.append(f"CRS: {setores.crs}")
linhas.append(f"Geometrias nulas: {geometrias_nulas}")
linhas.append(f"Geometrias vazias: {geometrias_vazias}")
linhas.append(f"Geometrias inválidas: {geometrias_invalidas}")
linhas.append(f"Menor percentual de área na APG escolhida: {percentual_minimo:.2f}%")
linhas.append("")
linhas.append("REGRA DE ASSOCIAÇÃO")
linhas.append("-" * 55)
linhas.append("Cada setor foi associado à APG com a maior área de interseção.")
linhas.append("")
linhas.append("SETORES POR APG")
linhas.append("-" * 55)

for _, linha in contagem_apg.iterrows():
    linhas.append(f"{linha['nome_apg']}: {linha['quantidade_setores']} setores")

linhas.append("")
linhas.append("RESULTADO FINAL")
linhas.append("-" * 55)

if problemas:
    linhas.append("VALIDAÇÃO COM PENDÊNCIAS")
    linhas.extend(f"- {problema}" for problema in problemas)
else:
    linhas.append("VALIDAÇÃO OK")
    linhas.append("Nenhuma inconsistência foi encontrada.")

ARQUIVO_RELATORIO.write_text("\n".join(linhas), encoding="utf-8")

print("\n".join(linhas))
