
from pathlib import Path
import pandas as pd

PASTA = Path(__file__).resolve().parent
ENTRADAS = PASTA / 'Arquivos Originais'
SAIDAS = PASTA / 'Arquivos Gerados'
SAIDAS.mkdir(exist_ok=True)

print('1/5 - Lendo APGs, setores e demografia integrada da Etapa 10...')
apg = pd.read_csv(ENTRADAS / 'apg_integrada_atributos.csv')
setores = pd.read_csv(ENTRADAS / 'setor_censitario_integrado_atributos.csv', dtype={'codigo_setor': str})
dados = pd.read_csv(ENTRADAS / 'dados_setor_2022_integrados.csv', dtype={'codigo_setor': str})

assert apg.id_apg.is_unique, 'APGs duplicadas.'
assert setores.codigo_setor.is_unique, 'Setores territoriais duplicados.'
assert dados.codigo_setor.is_unique, 'Setores demográficos duplicados.'
assert set(setores.codigo_setor) == set(dados.codigo_setor), 'Divergência de setores.'
assert set(setores.id_apg) == set(apg.id_apg), 'Divergência de APGs.'

base = setores[['codigo_setor', 'id_apg']].merge(
    dados[['codigo_setor', 'populacao_total', 'pop_60_mais']],
    on='codigo_setor', validate='one_to_one'
)
assert base.populacao_total.notna().all(), 'População total ausente.'
assert (base.populacao_total >= 0).all(), 'População total negativa.'
validos = base.pop_60_mais.notna()
assert (base.loc[validos, 'pop_60_mais'] >= 0).all(), 'População 60+ negativa.'
assert (base.loc[validos, 'pop_60_mais'] <= base.loc[validos, 'populacao_total']).all(), '60+ ultrapassa população total.'
assert (base.loc[validos, 'pop_60_mais'] % 1 == 0).all(), 'Contagem publicada 60+ não inteira.'

print('Agregando somente idosos publicados; ausências permanecem ausências...')
linhas = []
for apg_id, grupo in base.groupby('id_apg'):
    conhecidos = grupo.loc[grupo.pop_60_mais.notna()]
    sem_dado = grupo.loc[grupo.pop_60_mais.isna()]
    populacao_coberta = int(conhecidos.populacao_total.sum())
    idosos_publicados = int(conhecidos.pop_60_mais.sum())
    populacao_total = int(grupo.populacao_total.sum())
    if populacao_coberta <= 0:
        raise ValueError(f'APG {apg_id} não tem população com dado 60+ para cálculo do percentual.')
    linhas.append({
        'id_apg': int(apg_id),
        'populacao_total_apg_setores': populacao_total,
        'setores_total': int(len(grupo)),
        'setores_com_60_mais_publicado': int(len(conhecidos)),
        'setores_sem_60_mais': int(len(sem_dado)),
        'populacao_setores_com_60_mais_publicada': populacao_coberta,
        'populacao_setores_sem_60_mais_publicada': int(sem_dado.populacao_total.sum()),
        'pop_60_mais_publicada': idosos_publicados,
        'percentual_60_mais_setores_com_dado': round(100 * idosos_publicados / populacao_coberta, 4),
        'percentual_cobertura_populacional_60_mais': round(100 * populacao_coberta / populacao_total, 4) if populacao_total else 0,
        'situacao_dado_60_mais': 'cobertura_parcial' if (sem_dado.populacao_total > 0).any() else 'completo_para_setores_habitados',
        'origem_pop_60_mais': 'Censo 2022: soma exclusiva dos valores publicados',
    })

saida = pd.DataFrame(linhas).merge(
    apg[['id_apg', 'codigo_apg', 'nome_apg', 'pop_2022']],
    on='id_apg', validate='one_to_one'
).rename(columns={'pop_2022': 'populacao_2022_apg_fonte'})
saida = saida.sort_values('id_apg').reset_index(drop=True)
saida.to_csv(SAIDAS / 'populacao_idosa_apg_2022.csv', index=False, encoding='utf-8-sig')
print(f'Salvo: populacao_idosa_apg_2022.csv ({len(saida)} APGs)')
print(f'População 60+ publicada: {saida.pop_60_mais_publicada.sum():,}')
print(f'Setores sem divulgação 60+: {saida.setores_sem_60_mais.sum()}')
print(f'População TOTAL desses setores: {saida.populacao_setores_sem_60_mais_publicada.sum():,} (idade não conhecida)')
print('Nenhuma estimativa criada para os setores sem dado. Não equivale a total municipal completo.')
