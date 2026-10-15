from pathlib import Path
import re
import pandas as pd


# ============================================================
# 1. CAMINHOS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
PASTA_ORIGINAIS = BASE_DIR / "Arquivos Originais"
PASTA_GERADOS = BASE_DIR / "Arquivos Gerados"
PASTA_GERADOS.mkdir(parents=True, exist_ok=True)

ARQUIVO_PNS = PASTA_ORIGINAIS / "PNS_2019.txt"
ARQUIVO_INPUT = PASTA_ORIGINAIS / "input_PNS_2019.txt"
ARQUIVO_DICIONARIO = PASTA_ORIGINAIS / "dicionario_PNS_microdados_2019.xls"

SAIDA = PASTA_GERADOS / "pns_idosos_funcionalidade.csv"


# ============================================================
# 2. VARIÁVEIS QUE O TECHCARE PRECISA
# ============================================================

# Identificação/amostragem.
VARIAVEIS_BASE = [
    "V0001",       # UF
    "V0024",       # estrato
    "UPA_PNS",     # unidade primária de amostragem
    "V0006_PNS",   # número de ordem do domicílio
    "V0025A",      # identifica o morador selecionado
    "C006",        # sexo
    "C008",        # idade
    "V00291",      # peso do morador selecionado com calibração
]

# Atividades Básicas de Vida Diária (ABVD).
# Códigos: 1=Não consegue; 2=Grande dificuldade;
#          3=Pequena dificuldade; 4=Não tem dificuldade.
VARIAVEIS_ABVD = [
    "K001",  # comer
    "K004",  # tomar banho
    "K007",  # ir ao banheiro
    "K010",  # vestir-se
    "K013",  # andar dentro de casa
    "K016",  # deitar/levantar da cama
    "K019",  # sentar/levantar da cadeira
]

# Pergunta direta: precisa de ajuda para alguma ABVD?
VARIAVEL_AJUDA_ABVD = "K01901"

# Atividades Instrumentais de Vida Diária (AIVD).
VARIAVEIS_AIVD = [
    "K022",  # fazer compras
    "K025",  # administrar finanças
    "K028",  # tomar medicamentos
    "K031",  # ir ao médico
    "K034",  # utilizar transporte
]

# Pergunta direta: precisa de ajuda para alguma AIVD?
VARIAVEL_AJUDA_AIVD = "K03401"

VARIAVEIS_NECESSARIAS = (
    VARIAVEIS_BASE
    + VARIAVEIS_ABVD
    + [VARIAVEL_AJUDA_ABVD]
    + VARIAVEIS_AIVD
    + [VARIAVEL_AJUDA_AIVD]
)


# ============================================================
# 3. DESCOBRIR AS POSIÇÕES DAS VARIÁVEIS
# ============================================================

def ler_estrutura_input(caminho):
    """
    Lê o programa de importação fornecido com a PNS.

    Uma linha típica é:
        @00117 C008 3.

    Isso significa:
        posição inicial = 117
        variável = C008
        largura = 3

    O pandas usa posições começando em zero, então fazemos a conversão.
    """

    estrutura = {}

    # Aceita formatos como $1., 3. e 14.8.
    padrao = re.compile(
        r"^@(\d+)\s+([A-Za-z0-9_]+)\s+(\$?\d+)(?:\.\d+)?\."
    )

    with open(caminho, "r", encoding="latin-1") as arquivo:
        for linha in arquivo:
            resultado = padrao.match(linha.strip())

            if not resultado:
                continue

            inicio = int(resultado.group(1)) - 1
            nome = resultado.group(2)
            largura = int(resultado.group(3).replace("$", ""))
            fim = inicio + largura

            estrutura[nome] = (inicio, fim)

    return estrutura


# ============================================================
# 4. FUNÇÕES DE APOIO
# ============================================================

def faixa_etaria_techcare(idade):

    if 60 <= idade <= 64:
        return "60-64"
    if 65 <= idade <= 69:
        return "65-69"
    if 70 <= idade <= 74:
        return "70-74"
    return "75+"


def classificar_perfil(linha):
    """
    Classificação operacional do TechCare.

    Ordem das regras:
    1. Dependência elevada: precisa de ajuda em ABVD.
    2. Dependência parcial: precisa de ajuda em AIVD, mas não em ABVD.
    3. Apoio leve: relata alguma dificuldade, mas não precisa de ajuda.
    4. Autônomo: não relata dificuldade nas atividades consideradas.

    """

    if linha["precisa_ajuda_abvd"] == 1:
        return "dependencia_elevada"

    if linha["precisa_ajuda_aivd"] == 1:
        return "dependencia_parcial"

    if (
        linha["qtd_dificuldades_abvd"] > 0
        or linha["qtd_dificuldades_aivd"] > 0
    ):
        return "apoio_leve"

    return "autonomo"


# ============================================================
# 5. CONFERIR ARQUIVOS DE ENTRADA
# ============================================================

for arquivo in [ARQUIVO_PNS, ARQUIVO_INPUT, ARQUIVO_DICIONARIO]:
    if not arquivo.exists():
        raise FileNotFoundError(
            f"Arquivo original não encontrado: {arquivo.name}"
        )


# ============================================================
# 6. LER SOMENTE AS COLUNAS NECESSÁRIAS
# ============================================================

print("Lendo a estrutura da PNS 2019...")
estrutura = ler_estrutura_input(ARQUIVO_INPUT)

faltantes = [
    variavel
    for variavel in VARIAVEIS_NECESSARIAS
    if variavel not in estrutura
]

if faltantes:
    raise ValueError(
        "Estas variáveis não foram encontradas no input da PNS: "
        + ", ".join(faltantes)
    )

colspecs = [estrutura[v] for v in VARIAVEIS_NECESSARIAS]

print("Lendo somente as variáveis necessárias do PNS_2019.txt...")

pns = pd.read_fwf(
    ARQUIVO_PNS,
    colspecs=colspecs,
    names=VARIAVEIS_NECESSARIAS,
    dtype=str,
    encoding="latin-1",
)

print(f"Registros existentes no arquivo bruto: {len(pns):,}")


# ============================================================
# 7. SELECIONAR OS IDOSOS DA AMOSTRA INDIVIDUAL
# ============================================================

pns["idade"] = pd.to_numeric(pns["C008"], errors="coerce")
pns["peso_amostral"] = pd.to_numeric(pns["V00291"], errors="coerce")

# Mantemos somente:
# - morador selecionado para o questionário individual;
# - idade >= 60 anos;
# - peso amostral calibrado válido e positivo.
idosos = pns[
    (pns["V0025A"] == "1")
    & (pns["idade"] >= 60)
    & (pns["peso_amostral"].notna())
    & (pns["peso_amostral"] > 0)
].copy()

idosos["idade"] = idosos["idade"].astype(int)

print(f"Idosos selecionados (60+): {len(idosos):,}")


# ============================================================
# 8. CRIAR VARIÁVEIS MAIS LEGÍVEIS
# ============================================================

idosos["sexo"] = idosos["C006"].map(
    {
        "1": "Homem",
        "2": "Mulher",
    }
)

if idosos["sexo"].isna().any():
    raise ValueError("Foi encontrado código de sexo inesperado.")

idosos["faixa_etaria"] = idosos["idade"].apply(
    faixa_etaria_techcare
)


# ============================================================
# 9. RESUMIR DIFICULDADES FUNCIONAIS
# ============================================================

# Qualquer resposta 1, 2 ou 3 significa que existe algum grau de dificuldade.
CODIGOS_COM_DIFICULDADE = {"1", "2", "3"}

idosos["qtd_dificuldades_abvd"] = idosos[
    VARIAVEIS_ABVD
].isin(CODIGOS_COM_DIFICULDADE).sum(axis=1)

idosos["qtd_dificuldades_aivd"] = idosos[
    VARIAVEIS_AIVD
].isin(CODIGOS_COM_DIFICULDADE).sum(axis=1)

# A PNS pergunta diretamente se a pessoa precisa de ajuda.
# Quando todas as atividades são realizadas sem dificuldade, a pergunta de
# ajuda é pulada. Por isso, célula vazia nesse caso equivale a não precisar.
idosos["precisa_ajuda_abvd"] = (
    idosos[VARIAVEL_AJUDA_ABVD] == "1"
).astype(int)

idosos["precisa_ajuda_aivd"] = (
    idosos[VARIAVEL_AJUDA_AIVD] == "1"
).astype(int)


# ============================================================
# 10. CLASSIFICAR O PERFIL DE CUIDADO DO TECHCARE
# ============================================================

idosos["perfil_cuidado"] = idosos.apply(
    classificar_perfil,
    axis=1,
)


# ============================================================
# 11. ORGANIZAR A TABELA FINAL
# ============================================================

# Mantemos algumas variáveis originais K para permitir auditoria futura.
colunas_saida = [
    "V0001",
    "V0024",
    "UPA_PNS",
    "V0006_PNS",
    "idade",
    "sexo",
    "faixa_etaria",
    "peso_amostral",
    *VARIAVEIS_ABVD,
    VARIAVEL_AJUDA_ABVD,
    *VARIAVEIS_AIVD,
    VARIAVEL_AJUDA_AIVD,
    "qtd_dificuldades_abvd",
    "qtd_dificuldades_aivd",
    "precisa_ajuda_abvd",
    "precisa_ajuda_aivd",
    "perfil_cuidado",
]

idosos = idosos[colunas_saida].rename(
    columns={
        "V0001": "uf",
        "V0024": "estrato",
        "UPA_PNS": "upa_pns",
        "V0006_PNS": "domicilio_pns",
    }
)

idosos = idosos.sort_values(
    ["faixa_etaria", "sexo", "upa_pns", "domicilio_pns"]
).reset_index(drop=True)


# ============================================================
# 12. SALVAR
# ============================================================

idosos.to_csv(
    SAIDA,
    index=False,
    encoding="utf-8-sig",
)


# ============================================================
# 13. RESUMO NO TERMINAL
# ============================================================

print()
print("=" * 64)
print("ETAPA 7 - LEITURA E FILTRO DA PNS CONCLUÍDOS")
print("=" * 64)
print(f"Idosos mantidos: {len(idosos):,}")
print(
    "Faixas etárias: "
    + ", ".join(sorted(idosos["faixa_etaria"].unique()))
)
print("Perfis encontrados:")
for perfil, quantidade in idosos["perfil_cuidado"].value_counts().items():
    print(f"- {perfil}: {quantidade:,}")
print()
print(f"Arquivo gerado: {SAIDA.name}")
print()
print(
    "Observação: os perfis são derivados pelo TechCare a partir das "
    "respostas de funcionalidade e necessidade de ajuda da PNS 2019."
)
