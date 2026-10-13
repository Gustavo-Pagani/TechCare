
from pathlib import Path
import math
import pandas as pd

PASTA = Path(__file__).resolve().parent
ENTRADAS = PASTA / 'Arquivos Originais'
SAIDAS = PASTA / 'Arquivos Gerados'

IDADE = {'60 a 64': '60-64', '65 a 69': '65-69', '70 a 74': '70-74', '75 e +': '75+'}
SEXO = {'Homens': 'Homem', 'Mulheres': 'Mulher'}
PERFIS = ['autonomo', 'apoio_leve', 'dependencia_parcial', 'dependencia_elevada']


def distribuir_perfis(total, pesos):
    """Arredondamento do maior resto: mantém a soma dos quatro perfis."""
    partes = [total * p / sum(pesos) for p in pesos]
    inteiros = [math.floor(n) for n in partes]
    ordem = sorted(range(len(pesos)), key=lambda i: (-(partes[i] - inteiros[i]), i))
    for i in ordem[:total - sum(inteiros)]:
        inteiros[i] += 1
    return inteiros


print('3/5 - Lendo projeções, PNS e composição do SEADE...')
base = pd.read_csv(SAIDAS / 'populacao_idosa_apg_2022.csv')
projecoes = pd.read_csv(SAIDAS / 'projecoes_apg.csv')
seade = pd.read_csv(ENTRADAS / 'projecao_populacional_integrada.csv')
pns = pd.read_csv(ENTRADAS / 'parametro_perfil_cuidado_integrado.csv')

# Não usar '60+' nem 'Todos' para não misturar total agregado com faixas específicas.
pns = pns.loc[pns.faixa_etaria.isin(IDADE.values()) & pns.sexo.isin(SEXO.values())].copy()
assert len(pns) == 32, 'Esperados 4 faixas x 2 sexos x 4 perfis da PNS.'
assert pns.groupby(['faixa_etaria', 'sexo']).size().eq(4).all()
assert (pns.groupby(['faixa_etaria', 'sexo']).proporcao.sum() - 1).abs().max() < 0.00001

# Um único peso por perfil para cada ano, derivado da estrutura etária/sexo SEADE.
composicao = {}
for ano_apg in [2022, 2030, 2040, 2050]:
    ano_seade = 2020 if ano_apg == 2022 else ano_apg
    atual = seade[(seade.ano == ano_seade) & (seade.faixa_etaria.isin(IDADE))].copy()
    assert len(atual) == 8, f'SEADE: ano {ano_seade} sem 8 estratos idade/sexo.'
    atual['faixa_pns'] = atual.faixa_etaria.map(IDADE)
    atual['sexo_pns'] = atual.sexo.map(SEXO)
    pesos_perfil = dict.fromkeys(PERFIS, 0.0)
    total_municipal = atual.populacao.sum()
    assert total_municipal > 0
    for _, r in atual.iterrows():
        probabilidades = pns[(pns.faixa_etaria == r.faixa_pns) & (pns.sexo == r.sexo_pns)]
        for _, p in probabilidades.iterrows():
            pesos_perfil[p.perfil_cuidado] += r.populacao / total_municipal * p.proporcao
    # Corrigir apenas os resíduos numéricos da soma de probabilidades.
    normalizador = sum(pesos_perfil.values())
    composicao[ano_apg] = [pesos_perfil[perfil] / normalizador for perfil in PERFIS]

linhas = []
for ano in [2022, 2030, 2040, 2050]:
    if ano == 2022:
        referencia = base[['id_apg', 'codigo_apg', 'nome_apg', 'pop_60_mais_publicada']].rename(
            columns={'pop_60_mais_publicada': 'pop_60_mais'}
        )
    else:
        referencia = projecoes.loc[projecoes.ano == ano, ['id_apg', 'codigo_apg', 'nome_apg', 'pop_60_mais_apg_projetada']].rename(
            columns={'pop_60_mais_apg_projetada': 'pop_60_mais'}
        )
    for _, apg in referencia.iterrows():
        total = int(apg.pop_60_mais)
        numeros = distribuir_perfis(total, composicao[ano])
        for idx, perfil in enumerate(PERFIS):
            linhas.append({
                'id_apg': int(apg.id_apg), 'codigo_apg': apg.codigo_apg,
                'nome_apg': apg.nome_apg, 'ano': ano,
                'perfil_cuidado': perfil,
                'pop_60_mais_apg': total,
                'pop_perfil_estimada': numeros[idx],
                'percentual_perfil_apg': round(100 * numeros[idx] / total, 4) if total else 0,
                'ano_seade_composicao_idade_sexo': 2020 if ano == 2022 else ano,
                'origem_parametros': 'PNS 2019; composicao municipal SEADE',
                'natureza': 'estimativa_perfil_sobre_populacao_publicada_parcial' if ano == 2022 else 'estimativa_techcare',
            })
    print(f'  {ano}: perfis gerados para as 17 APGs.')

saida = pd.DataFrame(linhas).sort_values(['ano', 'id_apg', 'perfil_cuidado'])
arquivo = SAIDAS / 'perfis_cuidado_apg.csv'
saida.to_csv(arquivo, index=False, encoding='utf-8-sig')
print(f'Salvo: {arquivo.name} ({len(saida)} registros)')
