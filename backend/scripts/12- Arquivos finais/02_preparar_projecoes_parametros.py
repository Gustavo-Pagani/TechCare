"""Prepara as projecoes municipais do SEADE e os parametros PNS."""
from pathlib import Path
import pandas as pd

PASTA = Path(__file__).resolve().parent
ORIGINAIS = PASTA / "Arquivos Originais"
GERADOS = PASTA / "Arquivos Gerados"
GERADOS.mkdir(exist_ok=True)

# Mantem cod_ibge como texto e nao inventa APG para projecoes municipais.
projecoes = pd.read_csv(
    ORIGINAIS / "projecao_populacional_integrada.csv", dtype=str
)
for coluna in ["ano", "populacao"]:
    projecoes[coluna] = pd.to_numeric(
        projecoes[coluna], errors="raise"
    ).astype("Int64")
projecoes.to_csv(
    GERADOS / "projecao_populacional.csv", index=False, encoding="utf-8"
)
print(f"projecao_populacional.csv: {len(projecoes)} linhas")

# Os parametros continuam identificados pelas faixas, sexo e perfil.
# A fonte informa PNS 2019, sem adicionar IDs artificiais.
parametros = pd.read_csv(
    ORIGINAIS / "parametro_perfil_cuidado_integrado.csv", dtype=str
)
for coluna in ["n_amostra_grupo", "n_amostra_perfil"]:
    parametros[coluna] = pd.to_numeric(
        parametros[coluna], errors="raise"
    ).astype("Int64")
parametros.to_csv(
    GERADOS / "parametro_perfil_cuidado.csv", index=False, encoding="utf-8"
)
print(f"parametro_perfil_cuidado.csv: {len(parametros)} linhas")
