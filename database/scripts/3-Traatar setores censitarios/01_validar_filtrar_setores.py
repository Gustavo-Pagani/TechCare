import geopandas as gpd
from pathlib import Path

#================
# 1-CAMINHOS
#=================
pasta_entrada = Path(r"Caminho para pasta onde os arquivos estão salvos.")
pasta_saida = Path(r"Caminho para pasta que o arquivo sera criado")

#arquivo principal do Shapefile
arquivo_entrada = pasta_entrada / "SP_setores_CD2022.shp"

#arquivo que sera criado
arquivo_saida = pasta_saida / "setores_campinas_filtrados.gpkg"

#===========
# 2-LER ARQUIVO
# ===========


setores = gpd.read_file(arquivo_entrada)

print("Arquivo carregado com sucesso.\n")
print(f"Quantidade total de setores encontrados: {len(setores)} ")

#==========
# 3-Filtrar somente campinas
#===========


#Codigo OFICIAL do municipio de campinas
Codigo_campinas = "3509502"

# Garantir que cd_mun seja texto (já qu ele é um codigo identificador)
setores["CD_MUN"] = setores["CD_MUN"].astype(str)

# o .copy cria uma nova tabela independente com os setores filtrados.
setores_campinas = setores[setores["CD_MUN"] == Codigo_campinas].copy()

print(f"\n Setores de Campinas encontrados: {len(setores_campinas)}")


#=============================================
# 4- Quantidade de setores
#=============================================

quantidade_esperada = 2592
quantidade_encontrada = len(setores_campinas)

if quantidade_encontrada != quantidade_esperada:
    print(f"\nAtenção: esperamos {quantidade_esperada} \n mas encontramos: {quantidade_encontrada}")
else:
    print(f"Quantidade conferida: {quantidade_encontrada} setores.")

#=============================================
# 5- Verificando duplicados e vazios
#=============================================

# Conta setores sem código
setores_vazios = setores_campinas["CD_SETOR"].isna().sum()

# Conta códigos de setor repetidos
setores_duplicados = setores_campinas["CD_SETOR"].duplicated().sum()

print(f"Códigos de setor vazios: {setores_vazios}")
print(f"Códigos de setor duplicados: {setores_duplicados}")

#=============================================
# 6- Vendo se todos sao campinas
#=============================================

municipios_encontrados = setores_campinas["NM_MUN"].unique()

print(f"Municípios encontrados após o filtro: {municipios_encontrados}")

#=============================================
# 7- Salvando resultado
#=============================================
setores_campinas.to_file(
    arquivo_saida,
    layer="setores_campinas",
    driver="GPKG"
)

print("\nScript 1 concluído.")
print(f"Arquivo criado: {arquivo_saida}")