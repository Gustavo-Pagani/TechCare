# TechCare · Protótipo Campinas 60+

Protótipo web acadêmico para planejamento público dos serviços destinados à população idosa de Campinas, SP.

## O que esta versão entrega

- Dashboard executivo com KPIs e cenários 2022, 2030, 2040 e 2050.
- Mapa territorial interativo das 17 APGs de Campinas.
- Painel por APG com população, estimativas demonstrativas e pressão territorial.
- Telas de SAD/SUS, ILPIs e cuidadores, comparação entre APGs e metodologia.
- Visual inspirado em plataforma pública moderna de inteligência territorial.

## Base oficial do mapa

O arquivo `apg.geojson` foi gerado a partir da camada oficial:

- Portal de Metadados Geoespaciais da Prefeitura Municipal de Campinas
- Camada: `Histórico de População por APG`
- Responsabilidade: `CDDSE / DEPLAN / SMPDU`
- Download SHP: `https://zoneamento.campinas.sp.gov.br/novo_zoneamento/exporta_shp.php?id=171`
- CRS original: `SIRGAS 2000 / UTM zone 23S` (`EPSG:31983`)

Os arquivos brutos baixados ficam em:

`data/historico_pop_apg_oficial/`

O conversor local fica em:

`scripts/convert_shp_to_geojson.py`

Para regenerar o GeoJSON:

```bash
python scripts/convert_shp_to_geojson.py
```

## Dados do protótipo

A geometria territorial e os campos históricos de população por APG vêm da camada oficial da Prefeitura. Os indicadores de SAD, ILPIs, cuidadores e pressão territorial ainda são demonstrativos, usados apenas para validar a experiência do protótipo.

## Como rodar

Abra por um servidor local, porque o navegador pode bloquear `fetch("./apg.geojson")` quando `index.html` é aberto diretamente.

```bash
python -m http.server 5500
```

Depois acesse:

`http://localhost:5500`
