"""Trata exclusivamente a base APG conforme GUIA_TRATAMENTO_APGS.md.

Uso: python tratar_apgs.py caminho/arquivo.shp --saida pasta_destino
Dependências: geopandas, shapely, pyproj, pyogrio, pandas.
"""
from pathlib import Path
import argparse
import hashlib
import json
from datetime import datetime, timezone
import geopandas as gpd
import pandas as pd
import shapely
from shapely import make_valid
from shapely.geometry import MultiPolygon

MAPA = {'ID': 'id_apg', 'APG': 'codigo_apg', 'NOME_COMPL': 'nome_apg',
        **{f'POP_{ano}': f'pop_{ano}' for ano in [1970, 1980, 1991, 1996, 2000, 2010, 2022]}}

def exigir(condicao, mensagem):
    if not condicao:
        raise ValueError(mensagem)

def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def multipoligono(geom):
    if geom.geom_type == 'Polygon':
        return MultiPolygon([geom])
    exigir(geom.geom_type == 'MultiPolygon',
           f'Tipo {geom.geom_type} não pode ser convertido sem revisão; nenhuma parte será descartada.')
    return geom

def validar(g, padronizada=False):
    campos = ['id_apg', 'codigo_apg', 'nome_apg'] if padronizada else ['ID', 'APG', 'NOME_COMPL']
    pop = 'pop_2022' if padronizada else 'POP_2022'
    exigir(len(g) == 17, 'A base deve conter 17 APGs.')
    exigir('geometry' in g.columns and g.crs is not None, 'Geometria ou CRS ausente.')
    for col in campos:
        exigir(col in g.columns and not g[col].isna().any(), f'Campo ausente ou nulo: {col}')
        exigir(g[col].astype(str).str.strip().ne('').all(), f'Campo vazio: {col}')
        exigir(g[col].nunique() == 17, f'Valores duplicados: {col}')
    exigir(pd.to_numeric(g[pop], errors='raise').sum() == 1139047, 'Total de 2022 divergente.')
    exigir(not g.geometry.isna().any(), 'Geometria nula; necessária revisão da origem.')
    exigir(not g.geometry.is_empty.any(), 'Geometria vazia; necessária revisão da origem.')
    if padronizada:
        exigir(g.crs.to_epsg() == 31983, 'CRS final incorreto.')
        exigir(g.geom_type.eq('MultiPolygon').all(), 'Tipo final incorreto.')
        exigir(g.is_valid.all(), 'Geometria final inválida.')

def executar(entrada, saida):
    entrada, saida = Path(entrada), Path(saida)
    originais = [entrada.with_suffix(ext) for ext in ['.shp', '.dbf', '.shx', '.prj', '.cpg']]
    exigir(all(p.is_file() for p in originais), 'Os cinco componentes do shapefile são necessários.')
    exigir(saida.resolve() != entrada.parent.resolve(), 'Use pasta de saída separada dos originais.')
    hashes_antes = {p.name: sha256(p) for p in originais}
    g = gpd.read_file(entrada, engine='pyogrio')
    validar(g)
    exigir(set(MAPA).issubset(g.columns), 'Faltam atributos pedidos pelo guia.')
    invalida_inicial = ~g.is_valid
    t = g[list(MAPA) + ['geometry']].rename(columns=MAPA).copy()
    for col in [c for c in t.columns if c.startswith('pop_')]:
        n = pd.to_numeric(t[col], errors='raise')
        exigir(n.notna().all() and n.ge(0).all() and (n % 1 == 0).all(), f'População não inteira/válida: {col}')
        t[col] = n.astype('int64')
    if t.crs.to_epsg() != 31983:
        t = t.to_crs(31983)
    referencia = t.geometry.copy()
    t.geometry = t.geometry.map(multipoligono)
    exigir(all(a.equals_exact(b.geoms[0], 0) if a.geom_type == 'Polygon' else a.equals_exact(b, 0)
               for a, b in zip(referencia, t.geometry)), 'Conversão de tipo alterou coordenadas.')
    invalidas = ~t.is_valid
    correcoes = []
    for idx in t.index[invalidas]:
        antes = t.at[idx, 'geometry']
        depois = multipoligono(make_valid(antes))
        correcoes.append({'id_apg': int(t.at[idx, 'id_apg']), 'motivo': shapely.is_valid_reason(antes),
                         'area_antes_m2': antes.area, 'area_depois_m2': depois.area})
        t.at[idx, 'geometry'] = depois
    validar(t, True)
    saida.mkdir(parents=True, exist_ok=True)
    gpkg = saida / 'apg_campinas_tratada.gpkg'
    csv = saida / 'apg_campinas_atributos.csv'
    exigir(not gpkg.exists() and not csv.exists(), 'Saídas já existem; use uma pasta nova para preservar versões.')
    t.to_file(gpkg, layer='apg_campinas', driver='GPKG', engine='pyogrio', index=False)
    atributos = pd.DataFrame(t.drop(columns='geometry'))
    atributos.to_csv(csv, index=False, encoding='utf-8-sig', sep=',')
    reaberto = gpd.read_file(gpkg, layer='apg_campinas', engine='pyogrio')
    validar(reaberto, True)
    pd.testing.assert_frame_equal(pd.DataFrame(reaberto.drop(columns='geometry')), atributos, check_dtype=False)
    csv_reaberto = pd.read_csv(csv, encoding='utf-8-sig')
    pd.testing.assert_frame_equal(csv_reaberto, atributos, check_dtype=False)
    exigir(all(a.equals_exact(b, 0) for a, b in zip(t.geometry, reaberto.geometry)), 'Gravação alterou coordenadas.')
    hashes_depois = {p.name: sha256(p) for p in originais}
    exigir(hashes_antes == hashes_depois, 'Arquivos originais foram alterados.')
    preservadas = all(a.equals(b) for a, b in zip(referencia, reaberto.geometry))
    relatorio = {
        'execucao_utc': datetime.now(timezone.utc).isoformat(),
        'fonte': 'Shapefile fornecido em TechCare_APGs_para_Tratamento.zip; sem consulta ou substituição por bases externas.',
        'registros': len(reaberto), 'apgs_unicas': int(reaberto.codigo_apg.nunique()),
        'ids_unicos': int(reaberto.id_apg.nunique()), 'identificadores_vazios_ou_nulos': 0,
        'populacao_2022': int(reaberto.pop_2022.sum()), 'crs_original': str(g.crs),
        'crs_final': str(reaberto.crs), 'tipos_originais': g.geom_type.value_counts().to_dict(),
        'tipos_finais': reaberto.geom_type.value_counts().to_dict(),
        'geometrias_invalidas_iniciais': int(invalida_inicial.sum()),
        'geometrias_invalidas_finais': int((~reaberto.is_valid).sum()),
        'geometrias_nulas_finais': int(reaberto.geometry.isna().sum()),
        'geometrias_vazias_finais': int(reaberto.geometry.is_empty.sum()),
        'correcoes': correcoes, 'territorios_preservados': preservadas,
        'coordenadas_preservadas_na_conversao_e_gravacao': True,
        'atributos_csv_e_gpkg_iguais': True, 'originais_inalterados': hashes_antes == hashes_depois,
        'campos_removidos_na_copia_tratada': [c for c in g.columns if c not in MAPA and c != 'geometry'],
        'campos': MAPA, 'sha256_originais': hashes_antes,
        'sha256_resultados': {p.name: sha256(p) for p in [gpkg, csv]},
        'observacoes': [
            'APG contém nomes textuais na origem. codigo_apg preserva esses valores, seguindo a renomeação pedida pelo guia; não foram inventados códigos.',
            'Nova Europa possui ID 13059 no arquivo original. Valor preservado; confirmar com a fonte antes de qualquer renumeração.',
            'POP_2022 representa população total, não população idosa.',
            'Relacionamento de setores censitários com APGs não realizado nesta etapa.'
        ]
    }
    (saida / 'validacao_apgs.json').write_text(json.dumps(relatorio, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(relatorio, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('entrada', help='Caminho do .shp original')
    parser.add_argument('--saida', required=True, help='Pasta dos resultados')
    args = parser.parse_args()
    executar(args.entrada, args.saida)
