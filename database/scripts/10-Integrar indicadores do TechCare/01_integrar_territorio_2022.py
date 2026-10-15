from pathlib import Path
import pandas as pd
import geopandas as gpd

# =========================================================
# ETAPA 10 - SCRIPT 1
# INTEGRAR TERRITÓRIO, DEMOGRAFIA E RENDA
# =========================================================

BASE = Path(__file__).resolve().parent
ENTRADA = BASE / "Arquivos Originais"
SAIDA = BASE / "Arquivos Gerados"
SAIDA.mkdir(parents=True, exist_ok=True)

print("Lendo APGs e setores com APG...")
apgs = gpd.read_file(ENTRADA / "apg_campinas_tratada.gpkg")
setores = gpd.read_file(ENTRADA / "setores_campinas_com_apg.gpkg")

print("Lendo demografia e renda...")
demografia = pd.read_csv(
    ENTRADA / "demografia_campinas_tratada.csv",
    sep=";",
    encoding="utf-8-sig",
    dtype={
        "codigo_setor": "string",
        "codigo_municipio": "string",
        "codigo_distrito": "string",
    },
)

renda = pd.read_csv(
    ENTRADA / "renda_setores_campinas.csv",
    encoding="utf-8-sig",
    dtype={"codigo_setor": "string"},
)

# ---------------------------------------------------------
# 1. Padronizar chaves
# ---------------------------------------------------------
setores["codigo_setor"] = setores["codigo_setor"].astype("string")
setores["codigo_municipio"] = setores["codigo_municipio"].astype("string")
setores["codigo_distrito"] = setores["codigo_distrito"].astype("string")

# ---------------------------------------------------------
# 2. Validar chaves antes do JOIN
# ---------------------------------------------------------
if len(apgs) != 17 or apgs["id_apg"].nunique() != 17:
    raise ValueError("A base de APGs deve conter exatamente 17 APGs únicas.")

if len(setores) != 2592 or setores["codigo_setor"].nunique() != 2592:
    raise ValueError("A base territorial deve conter exatamente 2.592 setores únicos.")

if len(demografia) != 2592 or demografia["codigo_setor"].nunique() != 2592:
    raise ValueError("A demografia deve conter exatamente 2.592 setores únicos.")

if renda["codigo_setor"].duplicated().any():
    raise ValueError("Há códigos de setor duplicados na base de renda.")

if set(setores["codigo_setor"]) != set(demografia["codigo_setor"]):
    raise ValueError("As chaves de setor da base territorial e da demografia não coincidem.")

if not set(renda["codigo_setor"]).issubset(set(setores["codigo_setor"])):
    raise ValueError("A renda possui setor que não existe na base territorial de Campinas.")

# ---------------------------------------------------------
# 3. APG integrada
# Mantém atributos oficiais da APG e sua geometria.
# ---------------------------------------------------------
apg_integrada = apgs.copy()

# ---------------------------------------------------------
# 4. Setor censitário integrado
# Mantém somente identificação/território + geometria.
# Dados estatísticos ficam em dados_setor_2022.
# ---------------------------------------------------------
colunas_setor = [
    "codigo_setor",
    "id_apg",
    "situacao",
    "codigo_situacao",
    "codigo_tipo",
    "area_km2",
    "codigo_municipio",
    "municipio",
    "codigo_distrito",
    "distrito",
    "percentual_area_na_apg",
    "geometry",
]
setor_integrado = setores[colunas_setor].copy()

# ---------------------------------------------------------
# 5. Dados básicos do setor vindos da Etapa 4
# ---------------------------------------------------------
colunas_dados_basicos = [
    "codigo_setor",
    "populacao_total",
    "total_domicilios",
    "domicilios_particulares",
    "domicilios_coletivos",
    "media_moradores",
    "percentual_domicilios_imputados",
    "domicilios_particulares_ocupados",
]
dados_basicos = setores[colunas_dados_basicos].copy()

# ---------------------------------------------------------
# 6. Demografia
# Remove somente campos territoriais repetidos.
# Mantém flags de inibição e ausência exatamente como vieram.
# ---------------------------------------------------------
colunas_repetidas_demografia = [
    "codigo_municipio",
    "nome_municipio",
    "codigo_distrito",
    "nome_distrito",
    "populacao_total",
]

demografia_para_join = demografia.drop(
    columns=[c for c in colunas_repetidas_demografia if c in demografia.columns]
).copy()

# ---------------------------------------------------------
# 7. Integrar dados básicos + demografia
# ---------------------------------------------------------
dados_setor = dados_basicos.merge(
    demografia_para_join,
    on="codigo_setor",
    how="left",
    validate="one_to_one",
)

# ---------------------------------------------------------
# 8. Integrar renda
# A flag técnica distingue:
# - setor sem registro publicado de renda;
# - registro publicado, mas valor de renda nulo.
# ---------------------------------------------------------
renda = renda.copy()
renda["registro_renda_publicado"] = True

dados_setor = dados_setor.merge(
    renda,
    on="codigo_setor",
    how="left",
    validate="one_to_one",
)

dados_setor["registro_renda_publicado"] = dados_setor["registro_renda_publicado"].notna()

# ---------------------------------------------------------
# 9. Conferências pós-integração
# ---------------------------------------------------------
if len(dados_setor) != 2592:
    raise ValueError("A integração alterou a quantidade de setores.")

if dados_setor["codigo_setor"].duplicated().any():
    raise ValueError("A integração gerou setor duplicado.")

if set(dados_setor["codigo_setor"]) != set(setor_integrado["codigo_setor"]):
    raise ValueError("setor_censitario e dados_setor_2022 ficaram com chaves diferentes.")

# ---------------------------------------------------------
# 10. Salvar saídas intermediárias da Etapa 10
# ---------------------------------------------------------
apg_integrada.to_file(
    SAIDA / "apg_integrada.gpkg",
    layer="apg_integrada",
    driver="GPKG",
    index=False,
)
apg_integrada.drop(columns="geometry").to_csv(
    SAIDA / "apg_integrada_atributos.csv",
    index=False,
    encoding="utf-8-sig",
)

setor_integrado.to_file(
    SAIDA / "setor_censitario_integrado.gpkg",
    layer="setor_censitario_integrado",
    driver="GPKG",
    index=False,
)
setor_integrado.drop(columns="geometry").to_csv(
    SAIDA / "setor_censitario_integrado_atributos.csv",
    index=False,
    encoding="utf-8-sig",
)

dados_setor.to_csv(
    SAIDA / "dados_setor_2022_integrados.csv",
    index=False,
    encoding="utf-8-sig",
)

print("\nScript 1 concluído com sucesso.")
print(f"APGs: {len(apg_integrada)}")
print(f"Setores: {len(setor_integrado)}")
print(f"Linhas dados_setor_2022: {len(dados_setor)}")
print(f"Registros de renda publicados: {int(dados_setor['registro_renda_publicado'].sum())}")
print(f"Sem registro publicado de renda: {int((~dados_setor['registro_renda_publicado']).sum())}")
