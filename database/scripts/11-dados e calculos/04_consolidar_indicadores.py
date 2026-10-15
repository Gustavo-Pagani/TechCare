
from pathlib import Path
import pandas as pd

PASTA = Path(__file__).resolve().parent
ENTRADAS = PASTA / 'Arquivos Originais'
SAIDAS = PASTA / 'Arquivos Gerados'

print('4/5 - Consolidando perfis e demanda potencial...')
base = pd.read_csv(SAIDAS / 'populacao_idosa_apg_2022.csv')
projecoes = pd.read_csv(SAIDAS / 'projecoes_apg.csv')
perfis = pd.read_csv(SAIDAS / 'perfis_cuidado_apg.csv')

pivot = perfis.pivot(index=['id_apg', 'codigo_apg', 'nome_apg', 'ano', 'pop_60_mais_apg'],
                     columns='perfil_cuidado', values='pop_perfil_estimada').reset_index()
pivot.columns.name = None
pivot = pivot.rename(columns={
    'autonomo': 'autonomos', 'apoio_leve': 'apoio_leve',
    'dependencia_parcial': 'dependencia_parcial',
    'dependencia_elevada': 'dependencia_elevada',
})
pivot['dificuldade_ou_dependencia'] = (
    pivot.apoio_leve + pivot.dependencia_parcial + pivot.dependencia_elevada
)
pivot['necessidade_ajuda_declarada'] = pivot.dependencia_parcial + pivot.dependencia_elevada
pivot['percentual_dificuldade_ou_dependencia'] = (
    100 * pivot.dificuldade_ou_dependencia / pivot.pop_60_mais_apg
).round(4)
pivot['percentual_necessidade_ajuda_declarada'] = (
    100 * pivot.necessidade_ajuda_declarada / pivot.pop_60_mais_apg
).round(4)
pivot['interpretacao'] = (
    'Dificuldade e necessidade de ajuda estimadas; não equivalem a vagas SAD/ILPI.'
)
pivot['natureza'] = 'estimativa_techcare'
demanda = pivot.sort_values(['ano', 'id_apg'])
demanda.to_csv(SAIDAS / 'demanda_potencial_apg.csv', index=False, encoding='utf-8-sig')
print('Salvo: demanda_potencial_apg.csv')

print('Organizando os indicadores disponíveis da oferta municipal...')
servicos = pd.read_csv(ENTRADAS / 'servico_publico_integrado.csv', dtype={'cnpj': str})
indicadores = pd.read_csv(ENTRADAS / 'indicador_publico_integrado.csv', dtype={'numero_meta': str})
assert servicos.chave_servico.is_unique and indicadores.chave_indicador.is_unique
assert indicadores.id_apg.isna().all(), 'Existem indicadores territorializados: rever regras municipais.'
campos = ['chave_servico', 'nome_servico', 'tipo_servico', 'nivel_registro']
indicadores = indicadores.merge(servicos[campos], on='chave_servico', how='left', validate='many_to_one')
assert indicadores.loc[indicadores.chave_servico.notna(), 'nome_servico'].notna().all()

oferta = []
for _, r in indicadores.iterrows():
    oferta.append({
        'nivel_territorial': 'MUNICIPIO',
        'origem': r.origem,
        'tipo_registro': 'indicador_documental',
        'chave_indicador_origem': r.chave_indicador,
        'chave_servico_origem': r.chave_servico,
        'nome_servico': r.nome_servico,
        'tipo_servico': r.tipo_servico,
        'nome_indicador': r.nome_indicador,
        'valor': r.valor,
        'unidade': r.unidade,
        'ano_referencia': r.ano_referencia,
        'periodo_referencia': r.periodo_referencia,
        'fonte': r.fonte,
        'observacao': str(r.observacao) if pd.notna(r.observacao) else '',
        'limite_interpretacao': 'Dado documental municipal; metas, atendimentos e outros indicadores não equivalem automaticamente a vagas disponíveis.',
    })

# Entidades CMI são cadastradas: contar registros NÃO determina se são vagas públicas.
cmi = servicos[servicos.chave_servico.str.startswith('CMI:', na=False)]
for tipo, grupo in cmi.groupby('tipo_servico'):
    oferta.append({
        'nivel_territorial': 'MUNICIPIO',
        'origem': 'CMI',
        'tipo_registro': 'contagem_cadastros_CMI',
        'chave_indicador_origem': '',
        'chave_servico_origem': '',
        'nome_servico': '',
        'tipo_servico': tipo,
        'nome_indicador': 'quantidade_entidades_registradas_CMI',
        'valor': len(grupo),
        'unidade': 'entidades_registradas',
        'ano_referencia': 2025,
        'periodo_referencia': '2025-11-28',
        'fonte': 'Entidades Registradas CMI 28.11.2025',
        'observacao': 'Contagem dos cadastros da Etapa 10.',
        'limite_interpretacao': 'Entidades registradas não indicam vagas, capacidade, vínculo público ou oferta efetivamente disponível.',
    })

oferta_df = pd.DataFrame(oferta)
oferta_df.to_csv(SAIDAS / 'oferta_publica_municipal.csv', index=False, encoding='utf-8-sig')
print(f'Salvo: oferta_publica_municipal.csv ({len(oferta_df)} registros)')

print('Criando indicadores territoriais no formato longo (para futura tabela 8)...')
saida = []

def adicionar(nivel, apg_id, ano, indicador, valor, unidade, origem, natureza):
    saida.append({
        'nivel_territorial': nivel,
        'id_apg': apg_id,
        'ano': ano,
        'nome_indicador': indicador,
        'valor': float(valor),
        'unidade': unidade,
        'fonte_base': origem,
        'natureza_valor': natureza,
    })

for _, r in base.iterrows():
    i = int(r.id_apg)
    adicionar('APG', i, 2022, 'populacao_total', r.populacao_total_apg_setores, 'pessoas', 'Censo 2022 (agregacao setores)', 'dado_publicado_agregado')
    adicionar('APG', i, 2022, 'populacao_60_mais', r.pop_60_mais_publicada, 'pessoas', 'Censo 2022: setores com divulgacao', 'dado_publicado_cobertura_parcial')
    adicionar('APG', i, 2022, 'percentual_60_mais_setores_com_dado', r.percentual_60_mais_setores_com_dado, 'percentual', 'Censo 2022: denominador apenas setores com divulgacao', 'percentual_cobertura_parcial')
    adicionar('APG', i, 2022, 'cobertura_populacional_dado_60_mais', r.percentual_cobertura_populacional_60_mais, 'percentual', 'Censo 2022: cobertura populacional dos setores com dado 60+', 'cobertura_dados')

for _, r in projecoes.iterrows():
    i = int(r.id_apg)
    adicionar('APG', i, int(r.ano), 'populacao_total', r.populacao_total_apg_projetada, 'pessoas', 'SEADE municipal + rateio TechCare', 'estimativa_territorial_techcare')
    adicionar('APG', i, int(r.ano), 'populacao_60_mais', r.pop_60_mais_apg_projetada, 'pessoas', 'SEADE municipal + rateio TechCare', 'estimativa_territorial_techcare')
    adicionar('APG', i, int(r.ano), 'percentual_60_mais', r.percentual_60_mais_apg, 'percentual', 'SEADE municipal + rateio TechCare', 'estimativa_territorial_techcare')

for _, r in demanda.iterrows():
    i, ano = int(r.id_apg), int(r.ano)
    for nome in ['autonomos', 'apoio_leve', 'dependencia_parcial', 'dependencia_elevada',
                 'dificuldade_ou_dependencia', 'necessidade_ajuda_declarada']:
        adicionar('APG', i, ano, nome, r[nome], 'pessoas', 'PNS 2019 + SEADE + base territorial', 'estimativa_techcare')

# Consolida também o MUNICÍPIO: em 2030/2040/2050 preserva os totais oficiais SEADE.
for ano in [2022, 2030, 2040, 2050]:
    if ano == 2022:
        total = int(base.populacao_total_apg_setores.sum())
        idosos = int(base.pop_60_mais_publicada.sum())
        populacao_coberta = int(base.populacao_setores_com_60_mais_publicada.sum())
        natureza = 'censo_2022_dados_publicados_cobertura_parcial'
    else:
        periodo = projecoes.loc[projecoes.ano == ano]
        total = int(periodo.populacao_total_seade_municipal.iloc[0])
        idosos = int(periodo.pop_60_mais_seade_municipal.iloc[0])
        natureza = 'projecao_oficial_municipal_SEADE'
    adicionar('MUNICIPIO', None, ano, 'populacao_total', total, 'pessoas', 'Censo 2022' if ano == 2022 else 'SEADE', natureza)
    adicionar('MUNICIPIO', None, ano, 'populacao_60_mais', idosos, 'pessoas', 'Censo 2022: apenas setores com dado' if ano == 2022 else 'SEADE', natureza)
    if ano == 2022:
        adicionar('MUNICIPIO', None, ano, 'percentual_60_mais_setores_com_dado', round(100 * idosos / populacao_coberta, 4), 'percentual', 'Censo 2022: denominador apenas setores com divulgacao', 'percentual_cobertura_parcial')
        adicionar('MUNICIPIO', None, ano, 'cobertura_populacional_dado_60_mais', round(100 * populacao_coberta / total, 4), 'percentual', 'Censo 2022: cobertura populacional dos setores com dado 60+', 'cobertura_dados')
    else:
        adicionar('MUNICIPIO', None, ano, 'percentual_60_mais', round(100 * idosos / total, 4), 'percentual', 'SEADE', natureza)
    for nome in ['autonomos', 'apoio_leve', 'dependencia_parcial', 'dependencia_elevada',
                 'dificuldade_ou_dependencia', 'necessidade_ajuda_declarada']:
        adicionar('MUNICIPIO', None, ano, nome, int(demanda.loc[demanda.ano == ano, nome].sum()), 'pessoas', 'PNS 2019 + SEADE + base territorial', 'estimativa_techcare')

ind = pd.DataFrame(saida)
# IDs das APGs como inteiros no CSV (e vazios para os agregados municipais).
ind['id_apg'] = pd.Series(ind['id_apg'], dtype='Int64')
ind.to_csv(SAIDAS / 'indicadores_territoriais.csv', index=False, encoding='utf-8-sig')
print(f'Salvo: indicadores_territoriais.csv ({len(ind)} registros)')
print('Não foram fabricados déficits, vagas, projeções oficiais por APG ou vínculos de serviços.')
