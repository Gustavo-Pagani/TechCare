from pathlib import Path
import pandas as pd
import geopandas as gpd

# =========================================================
# ETAPA 10 - SCRIPT 4
# VALIDAÇÃO GERAL DA INTEGRAÇÃO
# =========================================================

BASE = Path(__file__).resolve().parent
SAIDA = BASE / "Arquivos Gerados"
RELATORIO = SAIDA / "VALIDACAO_ETAPA10.txt"

erros = []
avisos = []
linhas = []

def ok(texto):
    linhas.append(f"OK - {texto}")

def falha(texto):
    erros.append(texto)
    linhas.append(f"ERRO - {texto}")

def aviso(texto):
    avisos.append(texto)
    linhas.append(f"AVISO - {texto}")

# ---------------------------------------------------------
# 1. Arquivos obrigatórios
# ---------------------------------------------------------
obrigatorios = [
    "apg_integrada.gpkg",
    "apg_integrada_atributos.csv",
    "setor_censitario_integrado.gpkg",
    "setor_censitario_integrado_atributos.csv",
    "dados_setor_2022_integrados.csv",
    "projecao_populacional_integrada.csv",
    "seade_resumo_cenarios.csv",
    "seade_crescimento_municipal.csv",
    "parametro_perfil_cuidado_integrado.csv",
    "servico_publico_integrado.csv",
    "indicador_publico_integrado.csv",
]

for nome in obrigatorios:
    if not (SAIDA / nome).exists():
        falha(f"Arquivo ausente: {nome}")

if erros:
    RELATORIO.write_text("\n".join(linhas), encoding="utf-8")
    raise FileNotFoundError("Faltam arquivos gerados. Rode os scripts 1, 2 e 3 antes do script 4.")

# ---------------------------------------------------------
# 2. Território
# ---------------------------------------------------------
apg = gpd.read_file(SAIDA / "apg_integrada.gpkg")
setor = gpd.read_file(SAIDA / "setor_censitario_integrado.gpkg")
dados = pd.read_csv(SAIDA / "dados_setor_2022_integrados.csv", dtype={"codigo_setor": str})

if len(apg) == 17 and apg["id_apg"].nunique() == 17:
    ok("17 APGs únicas")
else:
    falha("Quantidade/chave das APGs incorreta")

if str(apg.crs).upper().endswith("31983"):
    ok("CRS das APGs = EPSG:31983")
else:
    falha(f"CRS das APGs inesperado: {apg.crs}")

if apg.geometry.is_valid.all() and not apg.geometry.isna().any() and not apg.geometry.is_empty.any():
    ok("Geometrias das APGs válidas")
else:
    falha("Problema nas geometrias das APGs")

if len(setor) == 2592 and setor["codigo_setor"].nunique() == 2592:
    ok("2.592 setores únicos")
else:
    falha("Quantidade/chave dos setores incorreta")

if setor["id_apg"].isna().sum() == 0 and setor["id_apg"].nunique() == 17:
    ok("Todos os setores possuem APG e as 17 APGs aparecem")
else:
    falha("Há setor sem APG ou APGs ausentes")

if str(setor.crs).upper().endswith("31983"):
    ok("CRS dos setores = EPSG:31983")
else:
    falha(f"CRS dos setores inesperado: {setor.crs}")

if setor.geometry.is_valid.all() and not setor.geometry.isna().any() and not setor.geometry.is_empty.any():
    ok("Geometrias dos setores válidas")
else:
    falha("Problema nas geometrias dos setores")

if len(dados) == 2592 and dados["codigo_setor"].nunique() == 2592:
    ok("dados_setor_2022 possui uma linha por setor")
else:
    falha("dados_setor_2022 não possui uma linha por setor")

if set(dados["codigo_setor"]) == set(setor["codigo_setor"].astype(str)):
    ok("Chaves de setor iguais entre território e dados_setor_2022")
else:
    falha("Chaves divergentes entre território e dados_setor_2022")

# ---------------------------------------------------------
# 3. Renda
# ---------------------------------------------------------
publicados = int(dados["registro_renda_publicado"].astype(str).str.lower().eq("true").sum())
sem_publicacao = len(dados) - publicados
if publicados == 2523 and sem_publicacao == 69:
    ok("Renda: 2.523 registros publicados e 69 setores sem registro publicado")
else:
    falha(f"Cobertura de renda inesperada: {publicados} publicados / {sem_publicacao} sem publicação")

sem_pub = dados[~dados["registro_renda_publicado"].astype(str).str.lower().eq("true")]
if len(sem_pub) == 69 and (sem_pub["populacao_total"].fillna(0) == 0).all():
    ok("Os 69 setores sem registro de renda têm população total zero")
else:
    aviso("Nem todos os setores sem registro de renda têm população zero; revisar")

nulos_renda_publicada = dados[
    dados["registro_renda_publicado"].astype(str).str.lower().eq("true")
]["renda_media_responsavel"].isna().sum()
if nulos_renda_publicada == 21:
    ok("21 registros publicados possuem renda média nula, preservada como NULL")
else:
    aviso(f"Quantidade de renda nula em registro publicado = {nulos_renda_publicada} (esperado no pacote atual: 21)")

# ---------------------------------------------------------
# 4. SEADE / PNS
# ---------------------------------------------------------
proj = pd.read_csv(SAIDA / "projecao_populacional_integrada.csv", dtype={"cod_ibge": str})
pns = pd.read_csv(SAIDA / "parametro_perfil_cuidado_integrado.csv")

if len(proj) == 352 and proj["cod_ibge"].nunique() == 1 and proj["cod_ibge"].iloc[0] == "3509502":
    ok("SEADE: 352 registros municipais de Campinas")
else:
    falha("Estrutura principal do SEADE divergente")

if "id_apg" not in proj.columns:
    ok("SEADE permanece municipal, sem id_apg artificial")
else:
    falha("Foi criado id_apg indevidamente na projeção SEADE")

somas = pns.groupby(["faixa_etaria", "sexo"])["proporcao"].sum()
if len(pns) == 60 and ((somas - 1).abs() < 0.0001).all():
    ok("PNS: 60 parâmetros e proporções fechando em 1 por faixa/sexo")
else:
    falha("Parâmetros PNS inconsistentes")

# ---------------------------------------------------------
# 5. Serviços / indicadores
# ---------------------------------------------------------
serv = pd.read_csv(SAIDA / "servico_publico_integrado.csv")
ind = pd.read_csv(SAIDA / "indicador_publico_integrado.csv", dtype={"numero_meta": str})

if serv["chave_servico"].duplicated().sum() == 0:
    ok("Chaves de serviço únicas")
else:
    falha("Chave de serviço duplicada")

if ind["chave_indicador"].duplicated().sum() == 0:
    ok("Chaves de indicador únicas")
else:
    falha("Chave de indicador duplicada")

if serv["id_apg"].notna().sum() == 0:
    ok("Serviços não foram territorializados artificialmente por APG")
else:
    aviso("Existem serviços com id_apg; conferir se a territorialização possui evidência")

# ---------------------------------------------------------
# 6. Relatório
# ---------------------------------------------------------
linhas.insert(0, "ETAPA 10 - VALIDACAO DA INTEGRACAO")
linhas.insert(1, "")
linhas.append("")

if erros:
    linhas.append("RESULTADO: VALIDACAO COM PENDENCIAS")
else:
    linhas.append("RESULTADO: VALIDACAO OK")

if avisos:
    linhas.append(f"Avisos: {len(avisos)}")
else:
    linhas.append("Avisos: 0")

RELATORIO.write_text("\n".join(linhas), encoding="utf-8")

print("\n".join(linhas))

if erros:
    raise ValueError("A Etapa 10 possui pendências. Consulte VALIDACAO_ETAPA10.txt")
