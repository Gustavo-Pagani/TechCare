import geopandas as gpd
import pandas as pd
from pathlib import Path

#=========================
# 1- CAMINHOS
#=========================

pasta = Path("Endereço da pasta onde os arquivos do script 1 foram salvos ")

#arquivo criado pelo script 1
arquivo_entrada = pasta / "setores_campinas_filtrados.gpkg"

#Arquivo que sera criado pelo script 2
arquivo_saida = pasta / "setores_campinas_padronizados.gpkg"

#=========================
# 2- Ler arquivo
#=========================
print("Lendo arquivo filtrado de Campinas...")

#Cria um GeoDataFrame
setores = gpd.read_file(arquivo_entrada)

print("Arquivo carregado e lido com sucesso.")
print("\nColunas encontradas")
#Converta a estrutura de dados em uma lista nativa do python (mais facil de manipular)
print(setores.columns.tolist())

#=========================
# 3- COlunas uteis
#=========================
colunas = [
    "CD_SETOR",
    "SITUACAO",
    "CD_SIT",
    "CD_TIPO",
    "AREA_KM2",
    "CD_MUN",
    "NM_MUN",
    "CD_DIST",
    "NM_DIST",
    "v0001",
    "v0002",
    "v0003",
    "v0004",
    "v0005",
    "v0006",
    "v0007",
    "geometry"
]

# Cria uma nova tabela apenas com as colunas selecionadas
setores = setores[colunas].copy()

print(f"Colunas mantidas: {len(setores.columns)}")

#=========================
# 4- Renomear colunas
#=========================
setores = setores.rename(columns={
    "CD_SETOR": "codigo_setor",
    "SITUACAO": "situacao",
    "CD_SIT": "codigo_situacao",
    "CD_TIPO": "codigo_tipo",
    "AREA_KM2": "area_km2",

    "CD_MUN": "codigo_municipio",
    "NM_MUN": "municipio",

    "CD_DIST": "codigo_distrito",
    "NM_DIST": "distrito",

    "v0001": "populacao_total",
    "v0002": "total_domicilios",
    "v0003": "domicilios_particulares",
    "v0004": "domicilios_coletivos",
    "v0005": "media_moradores",
    "v0006": "percentual_domicilios_imputados",
    "v0007": "domicilios_particulares_ocupados"
})

print("Colunas renomeadas com sucesso.")

#=========================
# 5- PAdronizar os tipos de dados
#=========================

# Codigos ficam como texto porque sao identificadores
colunas_codigo = [
    "codigo_setor",
    "codigo_situacao",
    "codigo_tipo",
    "codigo_municipio",
    "codigo_distrito"
]

for i in colunas_codigo:
    setores[i] = setores[i].astype(str)

# Colunas que precisam ser numericas
colunas_numericas = [
    "area_km2",
    "populacao_total",
    "total_domicilios",
    "domicilios_particulares",
    "domicilios_coletivos",
    "media_moradores",
    "percentual_domicilios_imputados",
    "domicilios_particulares_ocupados"
]

for i in colunas_numericas:
    setores[i] = pd.to_numeric(
        setores[i],
        errors="coerce" #Caso de algum erro escreve o valor como NaN
    )

#=========================
# 6- Padronizar o CRS
#=========================

crs_padrao = "EPSG:31983"

print(f"CRS ATUAL: {setores.crs}")

if setores.crs is None:
    raise ValueError("O arquivo nao possui CRS definido.")

if setores.crs.to_string() != crs_padrao:
    setores = setores.to_crs(crs_padrao)
    print(f"CRS convertido para {crs_padrao}")

else:
    print("CRS ja esta no padrao.")


#=========================
# 7- Salvar Arquivo padronizado
#=========================
setores.to_file(
    arquivo_saida,
    layer="setores_campinas",
    driver="GPKG"
)

print("\nArquivo padronizado criado com sucesso.")

print(f"Arquivo salvo em: {arquivo_saida}")










