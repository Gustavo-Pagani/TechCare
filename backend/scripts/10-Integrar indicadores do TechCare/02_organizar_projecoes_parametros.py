from pathlib import Path
import pandas as pd

# =========================================================
# ETAPA 10 - SCRIPT 2
# ORGANIZAR PROJEÇÕES DO SEADE E PARÂMETROS DA PNS
# =========================================================

BASE = Path(__file__).resolve().parent
ENTRADA = BASE / "Arquivos Originais"
SAIDA = BASE / "Arquivos Gerados"
SAIDA.mkdir(parents=True, exist_ok=True)

print("Lendo bases do SEADE...")
sexo_idade = pd.read_csv(
    ENTRADA / "seade_campinas_sexo_idade.csv",
    encoding="utf-8-sig",
    dtype={"cod_ibge": "string"},
)
crescimento = pd.read_csv(
    ENTRADA / "seade_campinas_crescimento.csv",
    encoding="utf-8-sig",
    dtype={"cod_ibge": "string"},
)
resumo = pd.read_csv(
    ENTRADA / "seade_projecoes_campinas.csv",
    encoding="utf-8-sig",
)

print("Lendo parâmetros da PNS...")
pns = pd.read_csv(
    ENTRADA / "pns_parametros_perfil_cuidado.csv",
    encoding="utf-8-sig",
)

# ---------------------------------------------------------
# 1. Validar granularidade do SEADE
# ---------------------------------------------------------
if sexo_idade.duplicated(["cod_ibge", "ano", "sexo", "faixa_etaria"]).any():
    raise ValueError("Há duplicidade em município + ano + sexo + faixa etária no SEADE.")

if sexo_idade["cod_ibge"].nunique() != 1 or sexo_idade["cod_ibge"].iloc[0] != "3509502":
    raise ValueError("A base SEADE deve conter somente Campinas (3509502).")

# Não criar id_apg: esta fonte é municipal.
projecao = sexo_idade.copy()
projecao["fonte"] = "Fundacao Seade"

# ---------------------------------------------------------
# 2. Validar PNS
# ---------------------------------------------------------
chave_pns = ["faixa_etaria", "sexo", "perfil_cuidado"]
if pns.duplicated(chave_pns).any():
    raise ValueError("Há duplicidade na chave dos parâmetros de cuidado da PNS.")

# Cada faixa/sexo deve somar aproximadamente 1 entre os perfis.
somas = pns.groupby(["faixa_etaria", "sexo"], dropna=False)["proporcao"].sum()
if not ((somas - 1).abs() < 0.0001).all():
    raise ValueError("As proporções da PNS não somam 1 em algum grupo faixa etária + sexo.")

parametros = pns.copy()

# ---------------------------------------------------------
# 3. Salvar
# O arquivo principal da futura tabela projecao_populacional
# é por ano + sexo + faixa etária.
# Os dois resumos do SEADE ficam auxiliares para a Etapa 11.
# ---------------------------------------------------------
projecao.to_csv(
    SAIDA / "projecao_populacional_integrada.csv",
    index=False,
    encoding="utf-8-sig",
)

resumo.to_csv(
    SAIDA / "seade_resumo_cenarios.csv",
    index=False,
    encoding="utf-8-sig",
)

crescimento.to_csv(
    SAIDA / "seade_crescimento_municipal.csv",
    index=False,
    encoding="utf-8-sig",
)

parametros.to_csv(
    SAIDA / "parametro_perfil_cuidado_integrado.csv",
    index=False,
    encoding="utf-8-sig",
)

print("\nScript 2 concluído com sucesso.")
print(f"Projeções sexo/idade: {len(projecao)} linhas")
print(f"Parâmetros PNS: {len(parametros)} linhas")
