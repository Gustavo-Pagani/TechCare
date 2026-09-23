import geopandas as gpd
from pathlib import Path
from shapely import make_valid

#=========================
# 1-Caminhos
#=========================
pasta = Path("Endereço da pasta onde os arquivos do script 1 e 2 foram salvos")

arquivo_entrada = pasta / "setores_campinas_padronizados.gpkg"

arquivo_saida_gpkg = pasta / "setores_campinas.gpkg"

arquivo_saida_csv = pasta / "setores_campinas_atributos.csv"

#=========================
# 2-Ler Arquivo
#=========================
print("Lendo arquivo filtrado de Campinas...")

#Cria um GeoDataFrame
setores = gpd.read_file(arquivo_entrada)

print("Arquivo carregado e lido com sucesso.")
print(f"Quantidade de setores: {len(setores)}")
print(f"CRS atual: {setores.crs}")

#=========================
# 3-Verificar geometrias
#=========================
invalidas = ~setores.geometry.is_valid # ~ inverte o resultado (pegando as invalidas)

vazias = setores.geometry.is_empty

nulas = setores.geometry.isna()

print(f"Geometrias invalidas: {invalidas.sum()}")

print(f"Geometrias vazias: {vazias.sum()}")

print(f"Geometrias nulas: {nulas.sum()}")

#=========================
# 4-Validar Resultado
#=========================

# se encontrar algum problema, interrompe o script
if invalidas.sum() > 0 or vazias.sum() > 0 or nulas.sum() > 0:

    raise ValueError(
        "Foram encontrados problemas nas geometrias."
    )

print("\nTodas as geometrias estao validas.")

#=========================
# 5-Conferencias final
#=========================
print(f"Quantidade final de setores: {len(setores)}")

print(f"CRS final: {setores.crs}")

print(f"Quantidade de colunas: {len(setores.columns)}")

#=========================
# 6-Salvar arquivo grafico final (GPKG)
#=========================

setores.to_file(
    arquivo_saida_gpkg,
    layer="setores_campinas",
    driver="GPKG"
)

print("\nArquivo GPKG final criado com sucesso.")

print(f"Arquivo salvo em: {arquivo_saida_gpkg}")

#=========================
# 7-Salvar csv final
#=========================

# remove geometry somente da copia que sera salva como CSV

setores.drop(columns="geometry").to_csv(
    arquivo_saida_csv,
    index=False,
    encoding="utf-8-sig"
)

print("\nArquivo CSV final criado com sucesso.")

print(f"Arquivo salvo em: {arquivo_saida_csv}")

print("\nETAPA 3 CONCLUIDA.")







