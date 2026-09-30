import pandas as pd
from pathlib import Path


BASE = Path(__file__).resolve().parents[3]
INPUT_DIR = BASE / "01_CSVs_Etapa1"
OUTPUT_DIR = BASE / "02_Arquivos_Gerados"

ENTRADA = INPUT_DIR / "pmas_servicos_idosos.csv"
SAIDA = OUTPUT_DIR / "pmas_servicos_idosos_tratado.csv"

COLS_TEXTO = ["servico", "publico_alvo", "periodo", "pagina", "fonte"]
COLS_INT = ["quantidade_atendida", "capacidade_anterior", "capacidade",
            "variacao_absoluta", "numero_metas", "numero_grupos",
            "usuarios_por_grupo", "numero_entidades_parceiras"]

MESES = {
    "janeiro": 1, "fevereiro": 2, "marco": 3, "março": 3, "abril": 4,
    "maio": 5, "junho": 6, "julho": 7, "agosto": 8, "setembro": 9,
    "outubro": 10, "novembro": 11, "dezembro": 12,
}


df = pd.read_csv(ENTRADA, dtype=str, keep_default_na=False)
print("Colunas:", list(df.columns))
print("Total de linhas:", len(df))


for col in COLS_TEXTO:
    df[col] = df[col].str.strip().str.replace(r"\s{2,}", " ", regex=True)


for col in COLS_INT:
    df[col] = pd.to_numeric(df[col].replace("", None), errors="coerce").astype("Int64")

df["variacao_percentual"] = (
    pd.to_numeric(df["variacao_percentual"].replace("", None), errors="coerce").astype("Float64")
)

mapa_bool = {"True": True, "False": False, "": pd.NA}
df["demanda_ampliacao"] = df["demanda_ampliacao"].map(mapa_bool).astype("boolean")


def parse_periodo(texto):
    nome_mes, ano = texto.split("/")
    return int(ano), MESES[nome_mes.strip().lower()]

anos, meses = [], []
for valor in df["periodo"]:
    ano, mes = parse_periodo(valor)
    anos.append(ano)
    meses.append(mes)

df["ano_referencia"] = pd.array(anos, dtype="Int64")
df["mes_referencia"] = pd.array(meses, dtype="Int64")
df["periodo_referencia"] = [f"{a}-{m:02d}" for a, m in zip(anos, meses)]


TOLERANCIA_PCT = 0.1

def valida_linha(row):
    if not pd.isna(row["capacidade"]) and not pd.isna(row["capacidade_anterior"]) \
       and not pd.isna(row["variacao_absoluta"]):
        if (row["capacidade"] - row["capacidade_anterior"]) != row["variacao_absoluta"]:
            return True
    if not pd.isna(row["variacao_percentual"]) and not pd.isna(row["capacidade_anterior"]) \
       and row["capacidade_anterior"] != 0:
        esperado = (row["capacidade"] - row["capacidade_anterior"]) / row["capacidade_anterior"] * 100
        if abs(esperado - float(row["variacao_percentual"])) > TOLERANCIA_PCT:
            return True
    return False

df["review_required"] = df.apply(valida_linha, axis=1)


assert len(df) == 3, "Esperado 3 linhas"
servicos_orig = set(pd.read_csv(ENTRADA, dtype=str, keep_default_na=False)["servico"].str.strip())
assert set(df["servico"]) == servicos_orig, "Surgiu ou sumiu servico!"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
df.to_csv(SAIDA, index=False, encoding="utf-8-sig")

print("-" * 50)
print("Linhas finais:", len(df))
print("Tipos das colunas numericas:")
print(df[COLS_INT + ["variacao_percentual", "demanda_ampliacao"]].dtypes.to_string())
print("Linhas marcadas para revisao:", int(df["review_required"].sum()))
print("Salvo em:", SAIDA)
