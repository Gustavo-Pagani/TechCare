# TechCare — Product Backlog inicial e Kanban da 2ª entrega

Fonte: **TechCare_Dossie_Backlog_Kanban.pdf**, 15 páginas. Estado de referência: **15/09/2026**. Este planejamento foi elaborado exclusivamente com base no dossiê e depende da revisão dos status e responsáveis pelo grupo.

## Escopo e referência

O MVP é uma plataforma web de apoio ao planejamento público de Campinas, destinada a gestores municipais de saúde e assistência social. Trabalha com população idosa, indicadores 60+ e 80+, 17 APGs, situação atual e projeções para 2030, 2040 e 2050, utilizando dados oficiais.

O planejamento de demanda contempla atendimento domiciliar/SUS e acolhimento institucional público ou cofinanciado, com uma estimativa principal por período. O ajuste socioeconômico por renda é um refinamento metodológico dessa estimativa. O corte de alta renda ainda depende de definição e documentação.

Não fazem parte do MVP: cadastro individual de idosos, prontuários, agendamento, diagnóstico, chatbot clínico, gestão de instituições privadas, expansão para outras cidades ou três cenários complexos. Autenticação não é necessária.

## Como ler o backlog

Os IDs abaixo são próprios desta organização: alguns itens do backlog-base do dossiê foram agrupados, e entregas já realizadas foram separadas das funcionalidades completas.

- **P0 — Essencial:** necessário ao MVP ou à entrega acadêmica.
- **P1 — Importante:** executar após os P0, conforme capacidade do grupo, seguindo a classificação do dossiê.
- **C:** Concluído conforme relato do PDF; o grupo deve apresentar a evidência.
- **EA:** Em Andamento conforme relato do PDF.
- **AF:** A Fazer conforme planejamento do PDF.
- **★:** status especialmente sujeito a confirmação, por ausência de informação específica ou descrição ambígua.

Todos os status representam a referência de 15/09/2026 e devem ser atualizados pelo grupo. “Concluído” aqui não significa verificação independente do código. Os responsáveis permanecem **a preencher**, sem atribuição presumida.

## Product Backlog — P0: bases já concluídas segundo o documento

| ID | Épico | Item | Objetivo | Critério de aceite | Dependências | Responsável | Status |
|---|---|---|---|---|---|---|---|
| PB-01 | Escopo | Definir problema, público e MVP | Delimitar o planejamento público do envelhecimento em Campinas | Escopo registra gestores públicos, população idosa, APGs, horizontes e serviços contemplados, com exclusões explícitas | — | A preencher | C — definição |
| PB-02 | Protótipo | Consolidar protótipo das seis telas | Demonstrar telas e fluxo inicial | Protótipo apresenta Razão do Projeto, Visão Geral, Perfis de Cuidado, Análise por APG, Soluções Públicas e Metodologia, com sidebar e navegação livre | PB-01 | A preencher | C — apenas protótipo |
| PB-03 | Base técnica | Criar estrutura inicial de pastas | Organizar o início da implementação | Estrutura do projeto existe e pode ser demonstrada, separando front-end, back-end, banco, dados, scripts e documentação | — | A preencher | C — estrutura inicial |
| PB-04 | Front-end inicial | Criar página inicial e componente de navegação | Comprovar implementação iniciada | Existem `index.html`, `sidebar.html` e `app.js`; o carregamento inicial da sidebar pode ser demonstrado | PB-03 | A preencher | C — arquivos iniciais |

A conclusão de PB-02 e PB-04 **não representa a implementação completa das seis telas**, dos seus conteúdos ou da navegação final. O CSS também foi criado, mas permanece em evolução, representado em PB-28.

## Product Backlog — P0: implementação e entregas pendentes

| ID | Épico | Item | Objetivo | Critério de aceite | Dependências | Responsável | Status |
|---|---|---|---|---|---|---|---|
| PB-05 | Navegação | Criar os esqueletos HTML das seis páginas | Disponibilizar a estrutura das telas | As seis páginas abrem no navegador, exibem títulos corretos e utilizam o CSS comum | PB-02, PB-04 | A preencher | EA★ — PDF indica “em criação / próximos passos” |
| PB-06 | Navegação | Conectar as seis páginas | Permitir percorrer o produto | Cada link abre a página correspondente sem erro e permite navegação livre | PB-05, PB-07 | A preencher | EA |
| PB-07 | Navegação | Completar o uso da sidebar reutilizável | Manter navegação comum entre telas | Sidebar é carregada nas seis páginas sem duplicar sua marcação HTML | PB-04, PB-05 | A preencher | AF★ — componente existe; uso em todas as telas não está confirmado |
| PB-08 | Razão do Projeto | Implementar conteúdo da tela inicial | Explicar o problema e a decisão pública | Tela apresenta o envelhecimento de Campinas e a jornada Hoje → 2050 → Decisão, conforme o protótipo | PB-01, PB-05 | A preencher | AF |
| PB-09 | Pipeline de dados | Consolidar organização e rastreabilidade do processamento | Viabilizar dados reproduzíveis e explicáveis | Fluxo registra originais → extraídos → tratados → banco → cálculos → site; originais são preservados e scripts ficam separados por extração e tratamento | PB-03 | A preencher | EA★ — andamento sugerido no Kanban; execução precisa ser confirmada |
| PB-10 | Dados de serviços | Extrair e revisar CMI e PMAS | Identificar entidades e capacidade pública/cofinanciada | CMI gera tabela com entidade, tipo, CNPJ, endereço, bairro, telefone e fonte; PMAS tem informações relevantes de capacidade e metas estruturadas; extração passa por revisão humana | PB-09; PDFs de origem | A preencher | AF |
| PB-11 | Dados de cuidado | Estruturar PNS 2019 | Preparar a base para estimar necessidade de cuidado | TXT é lido com layout e dicionário oficiais; variáveis úteis são identificadas e documentadas | PB-09; PNS e arquivos auxiliares | A preencher | AF |
| PB-12 | Dados demográficos | Tratar agregados básicos e demográficos do IBGE | Obter população e faixas etárias por setor | Dados são filtrados para Campinas; identificadores e variáveis são interpretados com dicionário correto; colunas e totais são conferidos | PB-09; bases e dicionários IBGE | A preencher | AF |
| PB-13 | Projeções | Tratar bases SEADE | Preparar evolução e projeções municipais | Tabelas identificam Campinas, anos, sexo e idades necessários para indicadores 60+ e 80+, incluindo 2030, 2040 e 2050 | PB-09; bases e dicionário SEADE | A preencher | AF |
| PB-14 | Geografia | Preparar camada das 17 APGs | Preservar a base territorial do mapa | Camada tratada contém as 17 APGs, com identificadores, geometrias válidas e sistema de referência documentado | PB-09; APG_Campinas | A preencher | AF — scripts de referência não equivalem a tratamento concluído |
| PB-15 | Geografia | Associar setores censitários às APGs | Produzir indicadores territoriais agregados | Setores de Campinas estão associados às APGs; procedimento de associação e conferência está documentado, preservando a geometria | PB-12, PB-14; SP_setores_CD2022 | A preencher | AF |
| PB-16 | Modelo de cuidado | Calcular os quatro perfis com a PNS | Estimar necessidade agregada de cuidado | Percentuais calculados e método documentado para autonomia, apoio leve, dependência parcial e dependência elevada/fragilidade; idade isolada não define dependência | PB-11 | A preencher | AF |
| PB-17 | Banco | Definir DER, criar banco e carregar dados | Disponibilizar dados tratados para cálculo e consulta | DER representa entidades, chaves e relações; PostgreSQL/PostGIS cria tabelas e suporta geometrias; carga dos dados tratados é reproduzível e validada | PB-10 a PB-15; PB-16 quando houver resultados a armazenar | A preencher | AF |
| PB-18 | Back-end | Criar estrutura inicial FastAPI | Disponibilizar o serviço de API | Servidor inicia no ambiente do grupo e endpoint de teste responde | PB-03 | A preencher | AF |
| PB-19 | Modelo de demanda | Estruturar estimativas de demanda e comparação com capacidade | Apoiar planejamento de atendimento domiciliar e acolhimento institucional | Método documenta necessidade estimada, capacidade pública/cofinanciada e déficit ou expansão por período, com uma estimativa principal; não apresenta resultado sem ajuste como se já estivesse ajustado por renda | PB-10, PB-12, PB-13, PB-16; PB-29 para informações do PMS; PB-32 para versão ajustada | A preencher | AF |
| PB-20 | API | Disponibilizar indicadores gerais e territoriais | Entregar dados ao front-end | Endpoints retornam JSON válido e documentado, com indicadores gerais e dados territoriais necessários; resultados correspondem ao banco e aos cálculos disponíveis | PB-17, PB-18; PB-19 para indicadores de demanda | A preencher | AF |
| PB-21 | Visão Geral | Implementar cards com dados do modelo | Mostrar indicadores principais | Cards exibem valores provenientes do modelo de dados, com correspondência conferida à API e identificação do período | PB-05, PB-20 | A preencher | AF |
| PB-22 | Visualizações | Implementar e integrar gráficos 60+ e 80+ | Mostrar evolução e projeções separadamente | Dois gráficos distintos em Chart.js mostram os grupos 60+ e 80+, incluindo projeções 2030/2040/2050; valores correspondem aos dados reais da API | PB-13, PB-20, PB-21 | A preencher | AF |
| PB-23 | Perfis de Cuidado | Exibir perfis e substituir percentuais simulados | Apresentar resultados calculados | Tela mostra os quatro perfis e sua distribuição calculada; os percentuais simulados 60%, 23%, 12% e 5% não aparecem como resultados reais | PB-05, PB-16, PB-20 | A preencher | AF |
| PB-24 | Análise por APG | Implementar e integrar mapa Leaflet | Permitir leitura territorial de Campinas | Mapa apresenta as 17 APGs com dados geográficos tratados, responde a clique/hover e associa corretamente os indicadores disponíveis | PB-05, PB-14, PB-15, PB-20 | A preencher | AF |
| PB-25 | Metodologia | Documentar fontes, cálculos e limitações na tela | Permitir compreender e defender os resultados | Tela explica fontes oficiais, pipeline, projeções, perfis, associação territorial e limitações; informa a situação do ajuste por renda e seu corte quando definido | PB-05, PB-09 a PB-16, PB-19; PB-30 a PB-32 para renda | A preencher | AF |
| PB-26 | Qualidade | Validar dados, cálculos e integração | Garantir coerência entre fontes e resultados exibidos | Totais-chave têm conferência documentada; outra pessoa revisa cálculos e dados oficiais; gráficos, cards e mapa correspondem às respostas da API e não apresentam simulações como dados reais | PB-17, PB-19 a PB-25; PB-32 quando integrado | A preencher | AF |
| PB-27 | Entrega acadêmica | Organizar evidências da 2ª entrega | Demonstrar protótipo, planejamento e implementação iniciada | Documento reúne protótipo, backlog priorizado, Kanban revisado, responsáveis preenchidos pelo grupo, tecnologias por situação, evidências do código inicial, evolução no semestre e justificativa de viabilidade | PB-01 a PB-04; atualização do backlog e Kanban | A preencher | AF★ — montagem da entrega não tem conclusão informada |

PB-17 e PB-20 podem ser divididos em cartões menores durante a execução, preservando seus critérios: DER → schema → carga; estrutura da API → indicadores gerais → indicadores territoriais.

## Product Backlog — P1: complementos e refinamentos previstos

| ID | Épico | Item | Objetivo | Critério de aceite | Dependências | Responsável | Status |
|---|---|---|---|---|---|---|---|
| PB-28 | Interface | Finalizar identidade visual e estados da sidebar | Tornar as telas consistentes e legíveis | Cores, tipografia, espaçamento e cards seguem o protótipo; página ativa é identificável e hover funciona | PB-02, PB-05, PB-07 | A preencher | EA — CSS e sidebar em evolução |
| PB-29 | Dados de saúde | Extrair e revisar PMS | Fundamentar indicadores e metas de atenção domiciliar | Informações relevantes são estruturadas, revisadas e acompanhadas da referência de origem | PB-09; PMS 2026–2029 | A preencher | AF |
| PB-30 | Refinamento metodológico | Definir e documentar corte de alta renda | Tornar explícita a regra de ajuste | Corte é justificável e reproduzível, baseado na análise dos microdados e dicionários; nenhum valor de corte é presumido | Análise exploratória do Censo 2022 e arquivos auxiliares | A preencher | AF |
| PB-31 | Dados socioeconômicos | Tratar Censo 2022 para idade e renda | Preparar a estimativa agregada de alta renda | Tratamento documenta variáveis, corte e pesos; relação territorial usa áreas de ponderação e explicita limites da estimativa por APG, sem localizar indivíduos por APG | PB-09, PB-30; Censo 2022, dicionário e composição das áreas de ponderação | A preencher | AF |
| PB-32 | Refinamento metodológico | Aplicar ajuste socioeconômico à demanda | Refinar a estimativa principal de demanda pública | Após estimar necessidade total, modelo retira da estimativa principal o grupo enquadrado como alta renda segundo a hipótese adotada; efeito e limitações ficam documentados, sem criar gestão privada | PB-16, PB-19, PB-30, PB-31 | A preencher | AF |
| PB-33 | Análise por APG | Representar pressão territorial | Facilitar a identificação das APGs com maior pressão | Cores e painel de informações refletem o indicador calculado; critério de classificação está documentado | PB-15, PB-19, PB-24 | A preencher | AF |
| PB-34 | Soluções Públicas | Implementar conteúdo da tela | Apresentar respostas públicas previstas no projeto | Tela contempla prevenção, apoio domiciliar e familiar, serviços comunitários/intermediários, longa duração e cidade amiga da pessoa idosa | PB-02, PB-05 | A preencher | AF |
| PB-35 | Documentação técnica | Manter README e instruções iniciais | Facilitar execução e colaboração | README explica objetivo, estrutura e execução; distingue tecnologias utilizadas das planejadas | PB-03; componentes disponíveis | A preencher | AF★ — existência e conteúdo não confirmados |
| PB-36 | Testes de interface | Testar navegação em desktop e mobile | Verificar o uso das telas | Não há links quebrados nem layout inutilizável nas telas implementadas | PB-06, PB-21 a PB-25, PB-28, PB-34 | A preencher | AF |
| PB-37 | Entrega final | Preparar documentação e apresentação final | Explicar o MVP e os resultados do semestre | Grupo consegue demonstrar escopo, método, arquitetura, resultados e limitações com evidências da implementação | MVP integrado; PB-25, PB-26, PB-35, PB-36 | A preencher | AF |

## Observações sobre prioridade e dependências

A classificação P1 de renda, PMS, pressão territorial e conteúdo de Soluções Públicas acompanha o backlog-base do dossiê. Isso não permite apresentar esses itens como implementados nem omitir suas pendências.

PB-19 contempla primeiro a estrutura do cálculo e a comparação com capacidade. PB-32 aplica posteriormente o refinamento por renda. A estimativa só pode ser descrita como **ajustada por renda** depois da conclusão de PB-30, PB-31 e PB-32.

A análise exploratória do Censo subsidia PB-30; o tratamento final com aplicação do corte fica em PB-31. Essa separação evita depender de uma estimativa final de alta renda antes de definir o próprio corte.

## Kanban inicial — referência de 15/09/2026

Cada cartão utiliza o mesmo ID, critério de aceite, dependências e campo de responsável do backlog.

| A Fazer | Em Andamento | Revisão / Teste | Concluído conforme o PDF |
|---|---|---|---|
| **Navegação e conteúdo:** PB-07★, PB-08 | **PB-05★:** esqueletos das páginas | Nenhum cartão pode ser colocado aqui com segurança a partir do dossiê | **PB-01:** definição do problema, público e MVP |
| **Dados:** PB-10, PB-11, PB-12, PB-13 | **PB-06:** ligação entre páginas | — | **PB-02:** protótipo das seis telas; não equivale a telas implementadas |
| **Geografia:** PB-14, PB-15 | **PB-09★:** organização do pipeline; confirmar trabalho efetivamente em execução | — | **PB-03:** estrutura inicial de pastas |
| **Modelo, banco e API:** PB-16, PB-17, PB-18, PB-19, PB-20 | **PB-28:** identidade visual e estilização da sidebar | — | **PB-04:** criação de página inicial, componente sidebar e carregador JavaScript |
| **Visualizações e método:** PB-21, PB-22, PB-23, PB-24, PB-25 | — | — | — |
| **Qualidade e 2ª entrega:** PB-26, PB-27★ | — | — | — |
| **Refinamentos de dados e renda:** PB-29, PB-30, PB-31, PB-32 | — | — | — |
| **Complementos e entrega final:** PB-33, PB-34, PB-35★, PB-36, PB-37 | — | — | — |

## Confirmações necessárias antes de apresentar o quadro

- **PB-05:** identificar quais páginas já existem e quais continuam como próximos passos.
- **PB-07:** verificar em quantas páginas a sidebar já está carregada e funcionando.
- **PB-09:** confirmar se há atividade em execução além do pipeline conceitualmente definido.
- **PB-27 e PB-35:** confirmar o andamento da documentação da entrega e do README.
- **PB-01 a PB-04:** reunir as evidências das conclusões relatadas no PDF.
- **Todos os cartões:** preencher responsáveis e atualizar avanços posteriores a 15/09/2026.

## Implementado, iniciado e planejado

| Situação informada | Conteúdo |
|---|---|
| Definido ou concluído como planejamento | Problema, público, MVP e protótipo das seis telas |
| Criado como implementação inicial | Estrutura de pastas, `index.html`, `sidebar.html`, `app.js` e CSS inicial |
| Em evolução | Ligação entre páginas, criação das demais páginas, estilização da sidebar e identidade visual |
| Planejado ou em preparação | Extração e tratamento dos dados, geografia, cálculos, PostgreSQL/PostGIS, FastAPI, gráficos Chart.js, mapa Leaflet, integração e validação |
| Pendente de decisão metodológica | Corte de alta renda e sua aplicação reproduzível à estimativa principal de demanda pública |

As tecnologias já iniciadas são **HTML5, CSS3, JavaScript e a componentização da sidebar**. As demais tecnologias descritas no dossiê devem permanecer identificadas como planejadas ou em preparação, conforme sua situação. Git/GitHub está previsto para histórico e colaboração; sua utilização não foi comprovada pelo documento.

## Organização da evolução no semestre

| Incremento | Resultado esperado |
|---|---|
| 1 — Base navegável | Estrutura, sidebar, seis páginas e identidade inicial |
| 2 — Dados preparados | Extração, tratamento, associação territorial e tabelas validadas |
| 3 — Banco e API | DER, PostgreSQL/PostGIS, carga, FastAPI e endpoints |
| 4 — Visualizações | Cards, gráficos separados de 60+ e 80+ e mapa das APGs |
| 5 — Modelo final | Perfis calculados, projeções, demanda, comparação com capacidade e refinamento por renda |
| 6 — Integração e entrega | Validação, testes, responsividade, documentação e apresentação |

Os incrementos seguem o plano do dossiê, com evolução das visualizações à medida que os cálculos forem disponibilizados. Front-end, preparação dos dados e documentação podem avançar em paralelo, com coordenação sobre arquivos compartilhados.

A **2ª entrega não exige o MVP completo**: deve demonstrar protótipo, planejamento, divisão de responsabilidades e implementação concreta iniciada. O recorte em Campinas, uma estimativa por período e o processamento prévio dos dados sustentam a viabilidade prevista para o semestre.

## Regras de acompanhamento e conclusão

1. Preencher um responsável por cartão antes de iniciar sua execução.
2. Manter em **Em Andamento** somente tarefas efetivamente em execução.
3. Levar para **Revisão / Teste** os itens implementados que aguardam conferência.
4. Mover para **Concluído** apenas quando o critério de aceite estiver atendido e houver evidência: arquivo, commit, tela, script, resultado ou documento.
5. Identificar explicitamente dados simulados no protótipo. Não utilizar os percentuais ilustrativos como resultados científicos.
6. Conferir cálculos e dados oficiais com outro integrante, documentando fontes e preservando os arquivos originais.
7. Atualizar o quadro antes das reuniões e antes da entrega; registrar dependências que impeçam o avanço.

Um item concluído deve estar salvo no repositório correto, funcionar no ambiente do grupo, ter fontes documentadas e não apresentar erro conhecido que impeça seu uso.
