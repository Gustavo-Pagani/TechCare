# TechCare - Backlog e Kanban (2a entrega)

Atualizado em 22/09/2026.

Equipe: Gustavo Sampaio, Gustavo Henrique, Leonardo e André.


## 1. Escopo do MVP

Plataforma web para apoiar o planejamento público do envelhecimento
em Campinas. Público-alvo: gestores municipais de saúde e assistência
social.

O que entra:

- população 60+ e 80+ de Campinas, hoje e nas projeções de 2030, 2040 e 2050
- análise por APG (as 17 Áreas de Planejamento e Gestão)
- quatro perfis de necessidade de cuidado, estimados a partir da PNS 2019
- demanda estimada de SAD e ILPI, comparada com a capacidade pública
- seis telas: Razão do Projeto, Visão Geral, Perfis de Cuidado,
  Análise por APG, Soluções Públicas e Metodologia

## 2. Prioridades

- P0: precisa estar pronto para o MVP funcionar
- P1: melhora o MVP, entra se der tempo no semestre


## 3. Kanban

### Concluído

- [x] 01 - Definir problema, público e escopo do MVP
      Responsável: Grupo
- [x] 02 - Protótipo navegável das seis telas
      Responsável: Grupo
- [x] 03 - Estrutura de pastas: frontend, backend, database, docs
      Responsável: Gustavo Pagani
- [x] 04 - Sidebar como componente reutilizável, carregada pelo app.js
      Responsável: Gustavo Pagani
- [x] 05 - Esqueleto HTML das seis páginas, todas com sidebar e ligadas entre si
      Responsável: Gustavo Pagani
- [x] 06 - DER do banco
      Responsável: Leonardo
- [X] 07 - CSS geral e identidade visual: cores, tipografia, cards, item ativo da sidebar
      Responsável: Grupo
Front-end
- [x] 10 - Conteúdo da tela Soluções Públicas: os cinco eixos (prevenção, apoio domiciliar,
      serviços comunitários, cuidado de longa duração, cidade amiga do idoso)
      Responsável: Gustavo Henrique

### Em andamento

- [ ] 08 - Documento da 2a entrega: protótipo, backlog, kanban, evidências
      Responsável: Grupo
- [ ] 15 - Etapa 1: extrair os 3 PDFs (CMI, PMAS e PMS)
      Responsável: Gustavo Henrique
- [ ] 16 - Etapa 2: tratar o mapa das APGs
      Responsável: Leonardo

### Revisão

(vazio)

### A fazer - P0

Front-end

- [ ] 09 - Conteúdo da tela Razão do Projeto: problema e jornada Hoje -> 2050 -> Decisão
      Responsável:
- [ ] 11 - Visão Geral: cards e dois gráficos Chart.js, 60+ e 80+, lendo da API
      Responsável:
- [ ] 12 - Análise por APG: mapa Leaflet com as 17 APGs e painel de detalhes
      Responsável:
- [ ] 13 - Perfis de Cuidado: trocar os percentuais simulados 60/23/12/5 pelos calculados
      Responsável:
- [ ] 14 - Metodologia: fontes, cálculos e limitações
      Responsável:

Dados - 13 etapas, nesta ordem. As etapas 1 e 2 já estão em andamento (ver acima).
O banco só começa depois da etapa 13.

- [ ] 17 - Etapa 3: tratar os setores censitários
      Responsável:
- [ ] 18 - Etapa 4: relacionar setor censitário -> APG
      Responsável:
- [ ] 19 - Etapa 5: tratar dados demográficos do Censo 2022
      Responsável:
- [ ] 20 - Etapa 6: tratar dados do SEADE
      Responsável:
- [ ] 21 - Etapa 7: tratar a PNS 2019
      Responsável:
- [ ] 22 - Etapa 8: tratar microdados de renda do Censo 2022
      Responsável:
- [ ] 23 - Etapa 9: tratar os CSVs gerados dos PDFs
      Responsável:
- [ ] 24 - Etapa 10: integrar todas as bases
      Responsável:
- [ ] 25 - Etapa 11: calcular os indicadores do TechCare
      Responsável:
- [ ] 26 - Etapa 12: validar todos os dados e cálculos
      Responsável:
- [ ] 27 - Etapa 13: gerar os arquivos finais para o database
      Responsável:

Banco e API

- [ ] 28 - Criar banco PostgreSQL/PostGIS a partir do DER e carregar os arquivos da etapa 13
      Responsável:
- [ ] 29 - API FastAPI com endpoints de indicadores gerais e por APG
      Responsável:

Qualidade

- [ ] 30 - Conferir se cards, gráficos e mapa batem com o que a API devolve
      Responsável:

### A fazer - P1

- [ ] 31 - Definir corte de alta renda e aplicar o ajuste socioeconômico na demanda
      Responsável:
- [ ] 32 - Índice de pressão territorial e cores no mapa
      Responsável:
- [ ] 33 - Testar navegação e layout em desktop e celular
      Responsável:
- [ ] 34 - README final e apresentação
      Responsável:


## 4. Dependências

- As 13 etapas de dados (15 a 27) seguem a ordem numerada.
  Em particular: a etapa 4 precisa das etapas 2 e 3; a etapa 9 precisa da etapa 1;
  a etapa 10 precisa de tudo até a 9.
- 28 (banco) só começa depois de 27 (etapa 13)
- 29 (API) depende de 28
- 11, 12 e 13 (telas com dados) dependem de 29
- 31 (ajuste por renda) depende de 22 (etapa 8) e de 25 (etapa 11)



## 5. Tecnologias

Em uso:

- HTML5, CSS3, JavaScript
- Python com Pandas, GeoPandas, Shapely, Pyproj e openpyxl
- Git e GitHub
- Visual Studio Code

Planejadas:

- PostgreSQL com PostGIS
- FastAPI
- SQLAlchemy e psycopg
- Chart.js
- Leaflet
- OpenStreetMap
- NumPy
- pdfplumber


## 6. Incrementos do semestre

1. Base navegável: estrutura, sidebar, seis páginas e identidade visual
2. Dados preparados: as 13 etapas, da extração dos PDFs aos arquivos finais
3. Banco e API
4. Visualizações: cards, gráficos e mapa
5. Modelo final: perfis, projeções, demanda e ajuste por renda
6. Validação, testes, documentação e apresentação


## 8. Como usamos o quadro

- Um cartão só vai para "Em andamento" quando alguém realmente começou.
- "Revisão" é para o que está pronto mas ainda não foi conferido por outra pessoa.
- "Concluído" exige evidência: arquivo no repositório, tela funcionando ou script rodando.
- Dados simulados do protótipo ficam sempre identificados como simulados.
- Atualizamos o quadro antes das reuniões e antes de cada entrega.
