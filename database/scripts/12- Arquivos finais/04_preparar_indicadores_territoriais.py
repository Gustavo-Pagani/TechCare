"""Prepara os indicadores da Etapa 11 revisada, sem recalcular valores."""
from pathlib import Path
import pandas as pd

PASTA = Path(__file__).resolve().parent
ORIGINAIS = PASTA / "Arquivos Originais"
GERADOS = PASTA / "Arquivos Gerados"
GERADOS.mkdir(exist_ok=True)

indicadores = pd.read_csv(
    ORIGINAIS / "indicadores_territoriais.csv", dtype=str
)

# Transforma 2.0 em 2; municipio permanece com id_apg vazio.
indicadores["id_apg"] = pd.to_numeric(
    indicadores["id_apg"], errors="raise"
).astype("Int64")
indicadores["ano"] = pd.to_numeric(
    indicadores["ano"], errors="raise"
).astype("Int64")

# Descricoes breves baseadas na natureza do valor ja registrada na Etapa 11.
# Esta coluna documenta os resultados, sem alterar nenhum valor calculado.
metodos = {
    "dado_publicado_agregado":
        "Agregacao dos setores censitarios por APG.",
    "dado_publicado_cobertura_parcial":
        "Soma apenas dos dados 60+ publicados no Censo 2022.",
    "percentual_cobertura_parcial":
        "Percentual apenas nos setores com dado 60+ publicado.",
    "cobertura_dados":
        "Proporcao da populacao em setores com dado 60+ publicado.",
    "estimativa_territorial_techcare":
        "Distribuicao proporcional de projecoes municipais SEADE entre APGs.",
    "estimativa_techcare":
        "Perfis PNS 2019 e composicao SEADE; para 2022 usa composicao de 2020.",
    "projecao_oficial_municipal_SEADE":
        "Projecao municipal oficial SEADE, sem projecao oficial por APG.",
    "censo_2022_dados_publicados_cobertura_parcial":
        "Dados municipais Censo 2022; cobertura 60+ parcial.",
}
indicadores["metodologia"] = indicadores["natureza_valor"].map(metodos)
if indicadores["metodologia"].isna().any():
    sem_metodo = indicadores.loc[
        indicadores["metodologia"].isna(), "natureza_valor"
    ].unique().tolist()
    raise ValueError(f"Natureza sem metodologia definida: {sem_metodo}")

indicadores.to_csv(
    GERADOS / "indicador_territorial.csv", index=False, encoding="utf-8"
)
print(f"indicador_territorial.csv: {len(indicadores)} linhas")
