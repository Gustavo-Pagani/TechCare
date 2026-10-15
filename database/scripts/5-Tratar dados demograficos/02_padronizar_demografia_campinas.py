import pandas as pd
from pathlib import Path


# 1 - ABRIR SOMENTE O RESULTADO DO SCRIPT 1.
pasta_saida = Path(__file__).resolve().parents[3] / "02_Arquivos_Gerados"
arquivo_entrada = pasta_saida / "demografia_campinas_filtrada.csv"
arquivo_saida = pasta_saida / "demografia_campinas_tratada.csv"
dados = pd.read_csv(arquivo_entrada, sep=";", encoding="utf-8-sig", dtype="string")
print(f"Base intermediária: {dados.shape[0]} linhas e {dados.shape[1]} colunas")
print("Colunas disponíveis:", list(dados.columns))
if len(dados) != 2592:
    raise ValueError("A base intermediária deve conter 2.592 setores.")


# 2 - SELECIONAR OS CAMPOS INDICADOS NO GUIA.
identificacao = ["CD_SETOR", "CD_MUN", "NM_MUN", "CD_DIST", "NM_DIST", "v0001"]
variaveis = [
    "V01006", "V01007", "V01008", "V01018", "V01019", "V01029", "V01030",
    "V01031", "V01032", "V01033", "V01034", "V01035", "V01036",
    "V01037", "V01038", "V01039", "V01040", "V01041"
]
marcadores = ["sem_linha_demografica", "sem_demografia_pop_zero", "revisar_sem_demografia"]
tratada = dados[identificacao + variaveis + marcadores].copy()

# Identificar X ANTES de convertê-lo em ausente.
tratada["possui_valor_inibido"] = tratada[variaveis].eq("X").any(axis=1)


# 3 - RENOMEAR: conferido no dicionário oficial fornecido, versão 20260520.
# Básico: V0001 (linha 2). Não PCT: V01006 a V01041 (linhas 1007 a 1042).
nomes = {
    "CD_SETOR": "codigo_setor",
    "CD_MUN": "codigo_municipio",
    "NM_MUN": "nome_municipio",
    "CD_DIST": "codigo_distrito",
    "NM_DIST": "nome_distrito",
    "v0001": "populacao_total",
    "V01006": "moradores_demografia",
    "V01007": "homens_total",
    "V01008": "mulheres_total",
    "V01018": "homens_60_69",
    "V01019": "homens_70_mais",
    "V01029": "mulheres_60_69",
    "V01030": "mulheres_70_mais",
    "V01031": "pop_0_4",
    "V01032": "pop_5_9",
    "V01033": "pop_10_14",
    "V01034": "pop_15_19",
    "V01035": "pop_20_24",
    "V01036": "pop_25_29",
    "V01037": "pop_30_39",
    "V01038": "pop_40_49",
    "V01039": "pop_50_59",
    "V01040": "pop_60_69",
    "V01041": "pop_70_mais"
}
tratada = tratada.rename(columns=nomes)
colunas_demograficas = [nomes[coluna] for coluna in variaveis]


# 4 - PADRONIZAR TIPOS E DIFERENCIAR ZERO DE VALOR AUSENTE.
for coluna in ["codigo_setor", "codigo_municipio", "codigo_distrito"]:
    tratada[coluna] = tratada[coluna].astype("string").str.strip()
tratada["populacao_total"] = pd.to_numeric(tratada["populacao_total"], errors="raise").astype("Int64")
if tratada["populacao_total"].isna().any():
    raise ValueError("População total ausente no Básico.")

for coluna in marcadores:
    if tratada[coluna].isna().any() or not tratada[coluna].isin(["True", "False"]).all():
        raise ValueError(f"Marcador inválido: {coluna}")
    tratada[coluna] = tratada[coluna].map({"True": True, "False": False}).astype(bool)

for coluna in colunas_demograficas:
    valores = tratada[coluna].replace("X", pd.NA)
    # Int64 (I maiúsculo) permite números inteiros e valores ausentes.
    # errors=raise impede que outros textos sejam ocultados como ausentes.
    tratada[coluna] = pd.to_numeric(valores, errors="raise").astype("Int64")

zerar = tratada["sem_linha_demografica"] & tratada["populacao_total"].eq(0)
if not zerar.equals(tratada["sem_demografia_pop_zero"].astype("boolean")):
    raise ValueError("Marcador de setor sem população inconsistente.")
if tratada["revisar_sem_demografia"].any() or (tratada["sem_linha_demografica"] & ~zerar).any():
    raise ValueError("Há setor populado sem registro demográfico. Revisar a origem.")

# Preenchimento restrito à ausência de linha nos setores com população zero.
tratada.loc[zerar, colunas_demograficas] = tratada.loc[zerar, colunas_demograficas].fillna(0)
print(f"Setores sem linha e sem população: {zerar.sum()}")
print(f"Setores com X nas variáveis selecionadas: {tratada['possui_valor_inibido'].sum()}")


# 5 - CRIAR SOMENTE OS TRÊS INDICADORES 60+.
# A soma direta mantém o resultado ausente se um componente estiver ausente.
tratada["pop_60_mais"] = tratada["pop_60_69"] + tratada["pop_70_mais"]
tratada["homens_60_mais"] = tratada["homens_60_69"] + tratada["homens_70_mais"]
tratada["mulheres_60_mais"] = tratada["mulheres_60_69"] + tratada["mulheres_70_mais"]
# Não calcular 80+: esta fonte não separa essa faixa dentro de 70+.


# 6 - CONFERÊNCIA FINAL. Não corrigir dados manualmente se algo divergir.
if len(tratada) != 2592:
    raise ValueError("Quantidade final diferente de 2.592 setores.")
if tratada["codigo_setor"].isna().any() or not tratada["codigo_setor"].str.fullmatch(r"\d{15}").all():
    raise ValueError("Código de setor ausente ou fora do formato esperado.")
if tratada["codigo_setor"].duplicated().any():
    raise ValueError("Código de setor duplicado.")
if not tratada["codigo_municipio"].eq("3509502").all():
    raise ValueError("Há registros de outro município.")
if tratada["populacao_total"].sum() != 1139047:
    raise ValueError("População total diferente de 1.139.047.")
if tratada["populacao_total"].eq(0).sum() != 69 or zerar.sum() != 69:
    raise ValueError("Esperados 69 setores sem população e sem linha demográfica.")
if any("80" in coluna for coluna in tratada.columns):
    raise ValueError("Não deve existir indicador de 80+ nesta etapa.")

# Cada X selecionado deve continuar ausente após o tratamento.
for original in variaveis:
    era_x = dados[original].eq("X").fillna(False)
    if not tratada.loc[era_x, nomes[original]].isna().all():
        raise ValueError(f"Um X foi convertido em número: {original}")


# 7 - SALVAR RESULTADO. Células vazias representam valores indisponíveis.
tratada.to_csv(arquivo_saida, sep=";", index=False, encoding="utf-8-sig", na_rep="")
print(f"Setores finais: {len(tratada)}")
print(f"População total: {tratada['populacao_total'].sum()}")
print(f"Setores com pop_60_mais ausente: {tratada['pop_60_mais'].isna().sum()}")
print(f"Script 2 concluído: {arquivo_saida}")
