import pandas as pd
from pathlib import Path


BASE = Path(__file__).resolve().parents[3]
INPUT_DIR = BASE / "01_CSVs_Etapa1"
OUTPUT_DIR = BASE / "02_Arquivos_Gerados"

ENTRADA = INPUT_DIR / "pms_indicadores_relevantes.csv"
SAIDA = OUTPUT_DIR / "pms_indicadores_relevantes_tratado.csv"

COLS_MILHAR = ["linha_base", "meta_plano", "meta_2026", "meta_2027",
               "meta_2028", "meta_2029"]
COLS_TEXTO = ["numero_meta", "descricao_meta", "indicador",
              "unidade_medida_linha_base", "unidade_medida", "fonte"]


df = pd.read_csv(ENTRADA, dtype=str, keep_default_na=False)
print("Colunas:", list(df.columns))
print("Total de linhas:", len(df))
print("numero_meta:", repr(df.loc[0, "numero_meta"]))


for col in COLS_TEXTO:
    df[col] = df[col].str.strip().str.replace(r"\s{2,}", " ", regex=True)


def milhar_para_int(valor: str):
    valor = valor.strip()
    if valor == "":
        return pd.NA
    return int(valor.replace(".", ""))

for col in COLS_MILHAR:
    df[col] = pd.array([milhar_para_int(v) for v in df[col]], dtype="Int64")

df["ano_linha_base"] = pd.to_numeric(df["ano_linha_base"], errors="coerce").astype("Int64")
df["pagina"] = pd.to_numeric(df["pagina"], errors="coerce").astype("Int64")


df["review_required"] = df["meta_plano"] != df["meta_2029"]


assert len(df) == 1, "Esperado 1 linha"
assert df.loc[0, "numero_meta"] == "3.1.1", "numero_meta deveria ser 3.1.1 (texto)"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
df.to_csv(SAIDA, index=False, encoding="utf-8-sig")

print("-" * 50)
print("Linha final:")
print(df[["numero_meta", "linha_base", "meta_plano",
          "meta_2026", "meta_2027", "meta_2028", "meta_2029"]].to_string(index=False))
print("Tipos:", df[COLS_MILHAR].dtypes.unique().tolist())
print("review_required:", bool(df.loc[0, "review_required"]))
print("Salvo em:", SAIDA)
