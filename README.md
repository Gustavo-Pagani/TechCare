# TechCare

O TechCare é um projeto acadêmico de programação web voltado ao apoio do planejamento público diante do envelhecimento da população de Campinas-SP.

A proposta é reunir, tratar e organizar dados oficiais para apresentar informações sobre crescimento da população idosa, perfis estimados de necessidade de cuidado, distribuição territorial por APG e serviços públicos relacionados ao envelhecimento.

## Objetivo

Desenvolver uma plataforma web capaz de transformar dados públicos em informações úteis para gestores municipais, auxiliando no planejamento de políticas e serviços voltados à população idosa.

## Principais funcionalidades

- Apresentação do problema e da proposta do projeto
- Visualização de indicadores demográficos da população idosa
- Consulta de dados do Censo 2022
- Visualização de projeções populacionais municipais da Fundação Seade
- Seleção dos anos de 2022, 2030, 2040 e 2050 nos painéis correspondentes
- Análise territorial das 17 Áreas de Planejamento e Gestão de Campinas
- Mapa interativo com seleção de APGs e consulta de indicadores
- Estimativa de quatro perfis de necessidade de cuidado
- Apresentação de soluções públicas para o planejamento da longevidade
- Consulta da metodologia e das fontes utilizadas

Os perfis de cuidado apresentados são:

- Autônomo
- Apoio leve
- Dependência parcial
- Dependência elevada

Os perfis são estimativas produzidas pelo TechCare a partir dos parâmetros da PNS 2019 e das bases demográficas utilizadas pelo projeto.

## Tecnologias

### Front-end

- HTML5
- CSS3
- JavaScript
- Chart.js
- Leaflet

### Tratamento e análise de dados

- Python
- pandas
- NumPy
- GeoPandas
- pdfplumber
- openpyxl

### Back-end

- Python
- FastAPI
- psycopg
- python-dotenv
- Uvicorn

O acesso ao PostgreSQL é realizado pelo psycopg, com consultas SQL implementadas nos módulos de rotas.

### Banco de dados

- PostgreSQL
- PostGIS

### Desenvolvimento e versionamento

- Git
- GitHub
- Visual Studio Code

## Estrutura do projeto

```text
TechCare/
│
├── frontend/
│   ├── index.html
│   ├── pages/
│   ├── componentes/
│   ├── css/
│   ├── js/
│   └── assets/
│
├── backend/
│   └── app/
│       ├── main.py
│       ├── database.py
│       └── routes/
│           ├── indicadores.py
│           ├── projecoes.py
│           ├── demografia.py
│           ├── cuidados.py
│           ├── territorio.py
│           └── servicos.py
│
├── database/
│   └── scripts/
│       ├── etapas de tratamento e integração/
│       ├── etapas de cálculo e preparação dos dados/
│       └── 13- Comandos sql/
│           └── criando_tabelas.sql
│
├── docs/
│   ├── TechCare-Prototipo/
│   └── kanban, backlog/
│
├── .gitignore
└── README.md
```

A estrutura acima resume as principais pastas. Em `database/scripts/`, os arquivos estão organizados em etapas numeradas de extração, tratamento, integração, cálculo e preparação para o banco.

O front-end atual está em `frontend/`. A pasta `docs/TechCare-Prototipo/` reúne materiais do protótipo.

As bases de origem e os arquivos intermediários do processamento são utilizados separadamente do código da aplicação. Para reproduzir o processamento, é necessário disponibilizar esses arquivos e conferir os caminhos configurados nos scripts.

## Fluxo dos dados

Os dados utilizados pelo TechCare seguem o seguinte processo:

```text
Dados originais
      ↓
Extração e tratamento com Python
      ↓
Integração territorial e demográfica
      ↓
Cálculo dos indicadores e estimativas
      ↓
Preparação dos CSVs para carga
      ↓
PostgreSQL / PostGIS
      ↓
Back-end FastAPI
      ↓
JSON / GeoJSON
      ↓
Front-end com gráficos, mapas e indicadores
```

Os arquivos originais são preservados durante o processamento.

Os scripts em Python realizam a extração, limpeza, filtragem, padronização e integração dos dados. As etapas seguintes produzem indicadores e arquivos preparados para carga no banco.

O back-end consulta as tabelas do PostgreSQL e disponibiliza os resultados por endpoints. O front-end utiliza essas respostas para preencher cartões, gráficos e mapas.

### Organização do banco de dados

O script SQL define oito tabelas principais:

- `apg`
- `setor_censitario`
- `dados_setor_2022`
- `projecao_populacional`
- `parametro_perfil_cuidado`
- `servico_publico`
- `indicador_publico`
- `indicador_territorial`

O PostGIS é utilizado para armazenar e consultar as geometrias territoriais. A API disponibiliza as geometrias das APGs em GeoJSON para apresentação no mapa.

## Fontes de dados

O projeto utiliza dados públicos e documentos de instituições como:

- IBGE, incluindo o Censo Demográfico 2022
- Fundação Seade
- Prefeitura Municipal de Campinas
- Conselho Municipal do Idoso
- Pesquisa Nacional de Saúde, edição de 2019
- Documentos municipais das áreas de saúde e assistência social

A página Metodologia apresenta as principais fontes e etapas do processamento.

### Interpretação dos indicadores

- Os dados observados do Censo 2022 são apresentados com sua identificação de origem
- A cobertura dos indicadores etários depende dos setores com informações publicadas
- Valores ausentes devem ser considerados na interpretação dos resultados
- As projeções municipais da Fundação Seade são utilizadas como referência demográfica
- A distribuição futura por APG é uma estimativa produzida pelo TechCare
- Os perfis de cuidado são estimativas populacionais para apoio ao planejamento

## Status do projeto

O TechCare possui front-end implementado, back-end em FastAPI e estrutura de banco de dados em PostgreSQL/PostGIS.

A aplicação integra consultas ao banco com a apresentação de indicadores, gráficos e mapas.

As páginas implementadas são:

- Razão do Projeto
- Visão Geral
- Perfis de Cuidado
- Análise por APG
- Soluções Públicas
- Metodologia

O projeto está em fase de revisão e ajustes para a apresentação final, incluindo:

- Validação dos fluxos e dos resultados apresentados
- Revisão da padronização visual
- Organização do repositório e das instruções de execução
- Atualização da documentação da disciplina
- Preparação das evidências de funcionamento

## Contexto acadêmico

Projeto desenvolvido na disciplina de Programação Web da PUC-Campinas.

O TechCare aplica conhecimentos de desenvolvimento web, tratamento de dados, banco de dados e análise territorial a um problema de interesse público, com foco no envelhecimento populacional de Campinas.
