# TechCare

O TechCare é um projeto acadêmico de programação web voltado ao apoio do planejamento público diante do envelhecimento da população de Campinas-SP.

A proposta é reunir, tratar e organizar dados oficiais para apresentar informações sobre crescimento da população idosa, perfis estimados de necessidade de cuidado, distribuição territorial por APG e capacidade dos serviços públicos.

## Objetivo

Desenvolver uma plataforma web capaz de transformar dados públicos em informações úteis para gestores municipais, auxiliando no planejamento de políticas e serviços voltados à população idosa.

## Principais funcionalidades previstas

- Visualização da população idosa atual;
- Projeções populacionais para 2030, 2040 e 2050;
- Análise territorial por APG;
- Estimativa de perfis de necessidade de cuidado;
- Indicadores relacionados à atenção domiciliar e cuidados de longa duração;
- Visualização de possíveis pressões futuras sobre os serviços públicos;
- Apresentação de soluções e alternativas para o planejamento da longevidade.

## Tecnologias

### Front-end
- HTML
- CSS
- JavaScript

### Tratamento de dados
- Python

### Banco de dados
- PostgreSQL / SQL

### Desenvolvimento futuro
- Back-end e API em Python
- Integração entre banco de dados e interface web

## Estrutura do projeto

```text
TechCare/
│
├── frontend/
│   ├── pages/
│   ├── css/
│   ├── js/
│   └── assets/
│       └── images/
│
├── backend/
│
├── database/
│
├── data/
│   ├── originais/
│   ├── extraidos/
│   └── tratados/
│
├── scripts/
│   ├── extracao/
│   └── tratamento/
│
└── docs/
````

## Fluxo dos dados

Os dados utilizados pelo TechCare seguem o seguinte processo:

```text
Dados originais
      ↓
Extração com Python
      ↓
Dados extraídos
      ↓
Tratamento e padronização
      ↓
Dados tratados
      ↓
Banco de dados
      ↓
Back-end / API
      ↓
Plataforma TechCare
```

Os arquivos originais são preservados sem alterações.

Os scripts em Python serão responsáveis pela extração, limpeza, filtragem e padronização dos dados antes da inserção no banco de dados.

## Fontes de dados

O projeto utiliza principalmente dados públicos provenientes de instituições como:

* IBGE;
* Fundação SEADE;
* Prefeitura Municipal de Campinas;
* Conselho Municipal do Idoso;
* Sistema Único de Saúde;
* Pesquisa Nacional de Saúde.

As fontes específicas utilizadas serão documentadas no arquivo `FONTES.md`.

## Status do projeto

Projeto em desenvolvimento.

Atualmente estão sendo realizadas as etapas de:

* organização da estrutura do projeto;
* desenvolvimento do protótipo;
* início da implementação do front-end;
* organização e preparação dos dados;
* definição da estrutura futura do banco de dados.

## Contexto acadêmico

Projeto desenvolvido como atividade acadêmica na disciplina de Programação Web.

```

Eu usaria esse README agora porque ele explica o projeto sem fingir que partes que ainda não fizemos já estão funcionando. Depois vamos atualizando o **Status do projeto** conforme o TechCare ganhar banco, API e integração real. 
```
