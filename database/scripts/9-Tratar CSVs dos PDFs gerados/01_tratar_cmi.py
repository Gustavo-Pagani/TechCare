import re
import pandas as pd
from pathlib import Path


BASE = Path(__file__).resolve().parents[3]
INPUT_DIR = BASE / "01_CSVs_Etapa1"
OUTPUT_DIR = BASE / "02_Arquivos_Gerados"

ENTRADA = INPUT_DIR / "cmi_entidades.csv"
SAIDA = OUTPUT_DIR / "cmi_entidades_tratado.csv"

COLS_TEXTO = ["registro", "entidade", "tipo", "cnpj", "unidade_executora",
              "endereco", "bairro", "telefone", "fonte"]

PADRAO_CNPJ = re.compile(r"^\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}$")


df = pd.read_csv(ENTRADA, dtype=str, keep_default_na=False)

print("Colunas:", list(df.columns))
print("Total de linhas:", len(df))

duplicados = df[df.duplicated("registro", keep=False)]
print("Registros duplicados:", len(duplicados))


def limpar_texto(valor: str) -> str:
    valor = valor.strip()
    valor = re.sub(r"\s{2,}", " ", valor)
    return valor

for col in COLS_TEXTO:
    df[col] = df[col].map(limpar_texto)


df["cnpj_formato_valido"] = df["cnpj"].str.match(PADRAO_CNPJ)
df["review_required"] = (df["cnpj"] != "") & (~df["cnpj_formato_valido"])


for col in COLS_TEXTO:
    df[col] = df[col].replace("", pd.NA)


df["pagina"] = pd.to_numeric(df["pagina"], errors="coerce").astype("Int64")

df["tipo"] = df["tipo"].str.strip()
print("Contagem por tipo:", df["tipo"].value_counts(dropna=False).to_dict())


assert len(df) == 73, "Esperado 73 linhas"
assert df.duplicated("registro").sum() == 0, "Ha registro duplicado"

originais = pd.read_csv(ENTRADA, dtype=str, keep_default_na=False)["cnpj"].map(limpar_texto)
assert (df["cnpj"].fillna("") == originais).all(), "Algum CNPJ foi alterado!"

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
df.to_csv(SAIDA, index=False, encoding="utf-8-sig")

print("-" * 50)
print("Linhas finais:", len(df))
print("Registros marcados para revisao:", int(df["review_required"].sum()))
print("Salvo em:", SAIDA)
