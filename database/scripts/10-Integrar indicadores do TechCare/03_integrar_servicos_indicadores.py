from pathlib import Path
import pandas as pd

# =========================================================
# ETAPA 10 - SCRIPT 3
# INTEGRAR SERVIÇOS E INDICADORES PÚBLICOS
# =========================================================

BASE = Path(__file__).resolve().parent
ENTRADA = BASE / "Arquivos Originais"
SAIDA = BASE / "Arquivos Gerados"
SAIDA.mkdir(parents=True, exist_ok=True)

cmi = pd.read_csv(ENTRADA / "cmi_entidades_tratado.csv", encoding="utf-8-sig", dtype=str)
pmas = pd.read_csv(ENTRADA / "pmas_servicos_idosos_tratado.csv", encoding="utf-8-sig")
pms = pd.read_csv(ENTRADA / "pms_indicadores_relevantes_tratado.csv", encoding="utf-8-sig", dtype={"numero_meta": str})

# ---------------------------------------------------------
# 1. SERVICO_PUBLICO - entidades do CMI
# ---------------------------------------------------------
servicos = []

for _, r in cmi.iterrows():
    servicos.append({
        "chave_servico": f"CMI:{r['registro']}",
        "nome_servico": r["entidade"],
        "tipo_servico": r["tipo"],
        "nivel_registro": "entidade",
        "publico_alvo": pd.NA,
        "cnpj": r["cnpj"],
        "endereco": r["endereco"],
        "bairro": r["bairro"],
        "telefone": r["telefone"],
        "id_apg": pd.NA,  # não territorializar sem geocodificação comprovada
        "fonte": r["fonte"],
        "pagina": r["pagina"],
        "review_required": r.get("review_required", False),
    })

# ---------------------------------------------------------
# 2. SERVICO_PUBLICO - três serviços municipais do PMAS
# Não são entidades físicas específicas.
# ---------------------------------------------------------
for i, r in pmas.reset_index(drop=True).iterrows():
    chave = f"PMAS:{i+1:03d}"
    servicos.append({
        "chave_servico": chave,
        "nome_servico": r["servico"],
        "tipo_servico": "servico_municipal_agregado",
        "nivel_registro": "municipal",
        "publico_alvo": r["publico_alvo"],
        "cnpj": pd.NA,
        "endereco": pd.NA,
        "bairro": pd.NA,
        "telefone": pd.NA,
        "id_apg": pd.NA,
        "fonte": r["fonte"],
        "pagina": r["pagina"],
        "review_required": r.get("review_required", False),
    })

servico_publico = pd.DataFrame(servicos)

if servico_publico["chave_servico"].duplicated().any():
    raise ValueError("Foi gerada chave de serviço duplicada.")

# ---------------------------------------------------------
# 3. INDICADOR_PUBLICO - PMAS
# Normaliza os campos numéricos em linhas de indicador.
# Só cria linha quando existe valor na fonte.
# ---------------------------------------------------------
indicadores = []

mapa_pmas = {
    "quantidade_atendida": ("quantidade_atendida", "pessoas"),
    "capacidade_anterior": ("capacidade_anterior", "metas"),
    "capacidade": ("capacidade", "metas"),
    "variacao_absoluta": ("variacao_absoluta", "metas"),
    "variacao_percentual": ("variacao_percentual", "percentual"),
    "numero_metas": ("numero_metas", "metas"),
    "numero_grupos": ("numero_grupos", "grupos"),
    "usuarios_por_grupo": ("usuarios_por_grupo", "pessoas_por_grupo"),
    "numero_entidades_parceiras": ("numero_entidades_parceiras", "entidades"),
}

contador = 1
for i, r in pmas.reset_index(drop=True).iterrows():
    chave_servico = f"PMAS:{i+1:03d}"
    for coluna, (nome, unidade) in mapa_pmas.items():
        valor = r.get(coluna)
        if pd.isna(valor):
            continue
        indicadores.append({
            "chave_indicador": f"IND:{contador:04d}",
            "chave_servico": chave_servico,
            "id_apg": pd.NA,
            "origem": "PMAS",
            "numero_meta": pd.NA,
            "nome_indicador": nome,
            "descricao": r["servico"],
            "valor": float(valor),
            "unidade": unidade,
            "ano_referencia": int(r["ano_referencia"]),
            "periodo_referencia": r["periodo_referencia"],
            "fonte": r["fonte"],
            "pagina": r["pagina"],
            "observacao": "Indicador municipal agregado; não atribuído a APG.",
            "review_required": r.get("review_required", False),
        })
        contador += 1

# ---------------------------------------------------------
# 4. INDICADOR_PUBLICO - PMS
# Uma linha por ano observado/meta.
# ---------------------------------------------------------
for _, r in pms.iterrows():
    serie = [
        (int(r["ano_linha_base"]), r["linha_base"], "linha_base"),
        (2026, r["meta_2026"], "meta"),
        (2027, r["meta_2027"], "meta"),
        (2028, r["meta_2028"], "meta"),
        (2029, r["meta_2029"], "meta"),
    ]
    for ano, valor, tipo_valor in serie:
        if pd.isna(valor):
            continue
        indicadores.append({
            "chave_indicador": f"IND:{contador:04d}",
            "chave_servico": pd.NA,
            "id_apg": pd.NA,
            "origem": "PMS",
            "numero_meta": str(r["numero_meta"]),
            "nome_indicador": r["indicador"],
            "descricao": r["descricao_meta"],
            "valor": float(valor),
            "unidade": r["unidade_medida"],
            "ano_referencia": ano,
            "periodo_referencia": str(ano),
            "fonte": r["fonte"],
            "pagina": r["pagina"],
            "observacao": tipo_valor,
            "review_required": r.get("review_required", False),
        })
        contador += 1

indicador_publico = pd.DataFrame(indicadores)

if indicador_publico["chave_indicador"].duplicated().any():
    raise ValueError("Foi gerada chave de indicador duplicada.")

# ---------------------------------------------------------
# 5. Salvar
# ---------------------------------------------------------
servico_publico.to_csv(
    SAIDA / "servico_publico_integrado.csv",
    index=False,
    encoding="utf-8-sig",
)

indicador_publico.to_csv(
    SAIDA / "indicador_publico_integrado.csv",
    index=False,
    encoding="utf-8-sig",
)

print("\nScript 3 concluído com sucesso.")
print(f"Serviços/entidades: {len(servico_publico)}")
print(f"Indicadores normalizados: {len(indicador_publico)}")
print("Nenhum serviço foi territorializado por APG sem evidência espacial.")
