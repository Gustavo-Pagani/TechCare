"""Prepara os registros municipais de servicos e indicadores publicos."""
from pathlib import Path
import pandas as pd

PASTA = Path(__file__).resolve().parent
ORIGINAIS = PASTA / "Arquivos Originais"
GERADOS = PASTA / "Arquivos Gerados"
GERADOS.mkdir(exist_ok=True)

# As chaves textuais existentes sao mantidas sem criar IDs novos.
servicos = pd.read_csv(
    ORIGINAIS / "servico_publico_integrado.csv", dtype=str
)
indicadores = pd.read_csv(
    ORIGINAIS / "indicador_publico_integrado.csv", dtype=str
)

# Referencias de pagina podem incluir intervalos (69-70) ou listas.
servicos = servicos.rename(columns={"pagina": "pagina_fonte"})
indicadores = indicadores.rename(columns={"pagina": "pagina_fonte"})

for tabela in [servicos, indicadores]:
    # Indicadores municipais nao recebem APG inventada: campo vazio e valido.
    tabela["id_apg"] = pd.to_numeric(
        tabela["id_apg"], errors="raise"
    ).astype("Int64")
    tabela["review_required"] = tabela["review_required"].str.lower()

servicos.to_csv(GERADOS / "servico_publico.csv", index=False, encoding="utf-8")
indicadores.to_csv(
    GERADOS / "indicador_publico.csv", index=False, encoding="utf-8"
)
print(f"servico_publico.csv: {len(servicos)} linhas")
print(f"indicador_publico.csv: {len(indicadores)} linhas")
