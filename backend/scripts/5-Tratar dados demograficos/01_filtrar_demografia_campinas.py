import pandas as pd
from pathlib import Path


# 1 - CAMINHOS: altere pasta_brutos se os arquivos estiverem em outro local.
pasta_brutos = Path(r"C:\Users\User\AppData\Local\Temp")
pasta_saida = Path(__file__).resolve().parents[3] / "02_Arquivos_Gerados"
arquivo_basico = pasta_brutos / "Agregados_por_setores_basico_BR.csv"
arquivo_demografia = pasta_brutos / "Agregados_por_setores_demografia_BR.csv"
arquivo_saida = pasta_saida / "demografia_campinas_filtrada.csv"

if not pasta_saida.is_dir():
    raise ValueError("Crie a pasta 02_Arquivos_Gerados antes de executar.")


# 2 - LEITURA: códigos ficam como texto, sem perder dígitos.
# usecols evita carregar campos do Básico que não serão usados.
colunas_basico = ["CD_SETOR", "CD_MUN", "NM_MUN", "CD_DIST", "NM_DIST", "v0001"]
basico = pd.read_csv(
    arquivo_basico, sep=";", encoding="latin-1",
    dtype="string", usecols=colunas_basico, keep_default_na=False
)
demografia = pd.read_csv(
    arquivo_demografia, sep=";", encoding="utf-8-sig",
    dtype="string", keep_default_na=False
)
print(f"Básico nacional: {len(basico)} linhas")
print(f"Demografia nacional: {len(demografia)} linhas")
print("Colunas do Básico:", list(basico.columns))
print("Colunas da Demografia:", list(demografia.columns))
if "CD_setor" not in demografia.columns:
    raise ValueError("A chave CD_setor está ausente na Demografia.")


# 3 - FILTRAR CAMPINAS E CONFERIR A BASE DO MUNICÍPIO.
basico["CD_MUN"] = basico["CD_MUN"].str.strip()
campinas = basico.loc[basico["CD_MUN"].eq("3509502")].copy()
campinas["CD_SETOR"] = campinas["CD_SETOR"].str.strip()
populacao = pd.to_numeric(campinas["v0001"], errors="raise")
print(f"Setores de Campinas: {len(campinas)}")
print(f"Setores com população zero: {populacao.eq(0).sum()}")
print(f"População total do Básico: {populacao.sum()}")
if len(campinas) != 2592:
    raise ValueError("Esperados 2.592 setores de Campinas. Confira a base.")
if campinas["CD_SETOR"].eq("").any() or campinas["CD_SETOR"].duplicated().any():
    raise ValueError("Código de setor vazio ou duplicado no Básico de Campinas.")
if populacao.eq(0).sum() != 69:
    raise ValueError("Esperados 69 setores com população zero. Confira a base.")


# 4 - PREPARAR AS CHAVES, SEM RELACIONAR POR NOME OU POSIÇÃO.
demografia = demografia.rename(columns={"CD_setor": "CD_SETOR"})
demografia["CD_SETOR"] = demografia["CD_SETOR"].str.strip()
demografia_campinas = demografia.loc[
    demografia["CD_SETOR"].isin(campinas["CD_SETOR"])
].copy()
for tabela in [campinas, demografia_campinas]:
    if not tabela["CD_SETOR"].str.fullmatch(r"\d{15}").all():
        raise ValueError("Código de setor fora do formato de 15 dígitos.")
    if tabela["CD_SETOR"].duplicated().any():
        raise ValueError("Código de setor duplicado; relacionamento interrompido.")
print(f"Registros demográficos de Campinas: {len(demografia_campinas)}")


# 5 - LEFT MERGE: mantém todos os setores do Básico.
# validate evita multiplicar linhas por códigos duplicados.
# indicator distingue uma linha ausente de uma célula com X.
filtrada = campinas.merge(
    demografia_campinas, on="CD_SETOR", how="left",
    validate="one_to_one", indicator=True
)
filtrada["sem_linha_demografica"] = filtrada["_merge"].eq("left_only")
populacao = pd.to_numeric(filtrada["v0001"], errors="raise")
filtrada["sem_demografia_pop_zero"] = (
    filtrada["sem_linha_demografica"] & populacao.eq(0)
)
filtrada["revisar_sem_demografia"] = (
    filtrada["sem_linha_demografica"] & populacao.ne(0)
)
print(f"Com registro demográfico: {(~filtrada['sem_linha_demografica']).sum()}")
print(f"Sem registro demográfico: {filtrada['sem_linha_demografica'].sum()}")
if filtrada["revisar_sem_demografia"].any():
    print(filtrada.loc[filtrada["revisar_sem_demografia"], ["CD_SETOR", "v0001"]])
    raise ValueError("Setor populado sem linha demográfica. Revisar antes de continuar.")
if len(filtrada) != 2592 or filtrada["CD_SETOR"].duplicated().any():
    raise ValueError("Quantidade ou unicidade dos setores alterada na junção.")
if len(demografia_campinas) != 2523 or filtrada["sem_demografia_pop_zero"].sum() != 69:
    raise ValueError("A junção não corresponde aos 2.523 registros e 69 ausências esperados.")


# 6 - PRESERVAR O X E A AUSÊNCIA DE LINHA.
# Nenhum preenchimento com zero neste script; os marcadores orientam o script 2.
colunas_demograficas = list(demografia_campinas.columns.drop("CD_SETOR"))
print("Células com X preservadas:", filtrada[colunas_demograficas].eq("X").sum().sum())
filtrada = filtrada.drop(columns="_merge")


# 7 - SALVAR A BASE INTERMEDIÁRIA EM UTF-8.
filtrada.to_csv(arquivo_saida, sep=";", index=False, encoding="utf-8-sig")
print(f"Script 1 concluído: {arquivo_saida}")
