
from pathlib import Path
import math
import pandas as pd

PASTA = Path(__file__).resolve().parent
ENTRADAS = PASTA / 'Arquivos Originais'
SAIDAS = PASTA / 'Arquivos Gerados'


def distribuir_inteiros(total, pesos, ids):
    """Distribui um total inteiro respeitando a soma, pelo maior resto."""
    soma = sum(pesos)
    if soma <= 0:
        raise ValueError('Pesos nulos: impossível distribuir projeção.')
    quotas = [total * peso / soma for peso in pesos]
    inteiros = [math.floor(q) for q in quotas]
    faltam = total - sum(inteiros)
    ordem = sorted(range(len(ids)), key=lambda i: (-(quotas[i] - inteiros[i]), ids[i]))
    for i in ordem[:faltam]:
        inteiros[i] += 1
    return inteiros


print('2/5 - Lendo população de 2022 e SEADE...')
base = pd.read_csv(SAIDAS / 'populacao_idosa_apg_2022.csv')
seade = pd.read_csv(ENTRADAS / 'seade_resumo_cenarios.csv')
assert len(base) == 17 and base.id_apg.is_unique
anos = [2030, 2040, 2050]
assert set(anos).issubset(set(seade.ano)), 'Falta cenário SEADE.'

ids = base.id_apg.tolist()
pesos_idosos = base.pop_60_mais_publicada.tolist()
pesos_total = base.populacao_total_apg_setores.tolist()
linhas = []
for ano in anos:
    mun = seade.loc[seade.ano == ano]
    assert len(mun) == 1, f'Ano duplicado ou ausente no SEADE: {ano}'
    pop_60_mun = int(mun.iloc[0].populacao_60_mais)
    pop_total_mun = int(mun.iloc[0].populacao_total)
    idosos_apg = distribuir_inteiros(pop_60_mun, pesos_idosos, ids)
    total_apg = distribuir_inteiros(pop_total_mun, pesos_total, ids)
    assert sum(idosos_apg) == pop_60_mun
    assert sum(total_apg) == pop_total_mun
    for i, r in base.reset_index(drop=True).iterrows():
        assert idosos_apg[i] <= total_apg[i], f'Inconsistência na APG {ids[i]}, {ano}'
        linhas.append({
            'id_apg': ids[i], 'codigo_apg': r.codigo_apg, 'nome_apg': r.nome_apg,
            'ano': ano,
            'populacao_total_apg_projetada': total_apg[i],
            'pop_60_mais_apg_projetada': idosos_apg[i],
            'percentual_60_mais_apg': round(100 * idosos_apg[i] / total_apg[i], 4),
            'populacao_total_seade_municipal': pop_total_mun,
            'pop_60_mais_seade_municipal': pop_60_mun,
            'metodo': 'distribuicao_proporcional_60_mais_publicada_censo2022',
            'natureza': 'estimativa_territorial_techcare',
        })
    print(f'  {ano}: {pop_60_mun:,} habitantes 60+ distribuídos em 17 APGs.')

saida = pd.DataFrame(linhas).sort_values(['ano', 'id_apg'])
arquivo = SAIDAS / 'projecoes_apg.csv'
saida.to_csv(arquivo, index=False, encoding='utf-8-sig')
print(f'Salvo: {arquivo.name} ({len(saida)} registros)')
