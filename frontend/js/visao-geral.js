
/* =========================================================
   TECHCARE - VISÃO GERAL

   Integração com:
   - demografia.py
   - cuidados.py

   Os gráficos utilizam somente a série da Seade.
========================================================= */


/* =========================
   1. CONFIGURAÇÕES
========================= */

const API_VISAO = "http://127.0.0.1:8000/api/v1";

const ANOS_VISAO = [2022, 2030, 2040, 2050];

const formatarInteiro = new Intl.NumberFormat("pt-BR");

const formatarPercentual = new Intl.NumberFormat("pt-BR", {
    minimumFractionDigits: 1,
    maximumFractionDigits: 2
});

// Dados consultados das APIs
let censo2022 = null;
let serieSeade = [];

// Instâncias dos gráficos
let grafico60 = null;
let grafico75 = null;

// Controle de consultas
let ultimaSolicitacao = 0;

// Guarda os dados de cuidados já consultados
const cuidadosPorAno = new Map();


/* =========================
   2. CONSULTAR E VALIDAR A API
========================= */

async function buscarJson(caminho) {

    const resposta = await fetch(API_VISAO + caminho);

    if (!resposta.ok) {
        throw new Error(
            `Falha em ${caminho}: HTTP ${resposta.status}`
        );
    }

    return resposta.json();
}


function numeroValido(valor, descricao) {

    const numero = Number(valor);

    if (
        valor === null ||
        valor === undefined ||
        !Number.isFinite(numero) ||
        numero < 0
    ) {
        throw new Error(
            `Valor inválido recebido da API: ${descricao}`
        );
    }

    return numero;
}


function escrever(id, valor) {

    const elemento = document.getElementById(id);

    if (!elemento) {
        throw new Error(
            `Elemento HTML ausente: ${id}`
        );
    }

    elemento.textContent = String(valor);
}


function percentual(valor) {
    return formatarPercentual.format(valor) + "%";
}


function numero(valor) {
    return formatarInteiro.format(valor);
}


function mostrarErro(mensagem) {

    const elemento = document.getElementById(
        "erro-visao-geral"
    );

    elemento.hidden = false;
    elemento.textContent = mensagem;
}


function limparErro() {

    const elemento = document.getElementById(
        "erro-visao-geral"
    );

    elemento.hidden = true;
    elemento.textContent = "";
}


function dadosSeadeDoAno(ano) {

    const registro = serieSeade.find(function (item) {
        return Number(item.ano) === ano;
    });

    if (!registro) {
        throw new Error(
            `Ano ${ano} ausente na série da Seade.`
        );
    }

    return registro;
}


async function obterCuidados(ano) {

    // Se já consultamos esse ano, usamos os dados guardados
    if (!cuidadosPorAno.has(ano)) {

        const dados = await buscarJson(
            `/cuidados/perfis-municipio?ano=${ano}`
        );

        if (
            Number(dados.ano) !== ano ||
            !Array.isArray(dados.perfis)
        ) {
            throw new Error(
                `Resposta de cuidados inválida para ${ano}.`
            );
        }

        cuidadosPorAno.set(ano, dados);
    }

    return cuidadosPorAno.get(ano);
}


/* =========================
   3. CRIAR OS GRÁFICOS
========================= */

function configuracaoGrafico(
    rotulo,
    chave,
    cor,
    fundo,
    canvasId
) {

    const anos = serieSeade.map(function (item) {
        return Number(item.ano);
    });

    const valores = serieSeade.map(function (item) {
        return numeroValido(item[chave], chave);
    });

    return new Chart(
        document.getElementById(canvasId),
        {
            type: "line",

            data: {
                labels: anos.map(String),

                datasets: [{
                    label: rotulo,
                    data: valores,

                    borderColor: cor,
                    backgroundColor: fundo,

                    borderWidth: 3,
                    tension: 0.18,
                    fill: true,

                    pointRadius: anos.map(() => 5),
                    pointHoverRadius: 8,

                    pointBackgroundColor: cor,
                    pointBorderColor: "#fff",
                    pointBorderWidth: 2
                }]
            },

            options: {
                responsive: true,
                maintainAspectRatio: false,

                interaction: {
                    intersect: false,
                    mode: "index"
                },

                plugins: {
                    legend: {
                        display: false
                    },

                    tooltip: {
                        callbacks: {
                            label: function (contexto) {
                                return (
                                    numero(contexto.parsed.y) +
                                    " pessoas"
                                );
                            }
                        }
                    }
                },

                scales: {
                    x: {
                        grid: {
                            display: false
                        },

                        ticks: {
                            color: "#5d7598"
                        }
                    },

                    y: {
                        beginAtZero: false,

                        grid: {
                            color: "#e8eef3"
                        },

                        ticks: {
                            maxTicksLimit: 5,
                            color: "#5d7598",

                            callback: function (valor) {
                                return numero(valor);
                            }
                        }
                    }
                }
            }
        }
    );
}


function criarGraficos() {

    if (typeof Chart === "undefined") {
        throw new Error(
            "Chart.js não foi carregado. Confira chart.umd.js."
        );
    }

    // Gráfico 1: população 60+
    grafico60 = configuracaoGrafico(
        "População 60+",
        "populacao_60_mais",
        "#099da0",
        "rgba(9,157,160,0.13)",
        "grafico-60"
    );

    // Gráfico 2: população 75+
    grafico75 = configuracaoGrafico(
        "População 75+",
        "populacao_75_mais",
        "#0968c9",
        "rgba(9,104,201,0.12)",
        "grafico-75"
    );

    // Crescimento entre 2025 e 2050
    const inicio = dadosSeadeDoAno(
        2025
    ).populacao_60_mais;

    const fim = dadosSeadeDoAno(
        2050
    ).populacao_60_mais;

    const aumento = fim - inicio;

    escrever(
        "indicador-crescimento",
        "+" + percentual(100 * aumento / inicio)
    );

    escrever(
        "indicador-crescimento-absoluto",
        "+" + numero(aumento)
    );
}


/* =========================
   4. DESTACAR O ANO NO GRÁFICO
========================= */

function destacarAnoNosGraficos(ano) {

    const anos = serieSeade.map(function (item) {
        return Number(item.ano);
    });

    [grafico60, grafico75].forEach(function (grafico) {

        if (!grafico) {
            return;
        }

        grafico.data.datasets[0].pointRadius =
            anos.map(function (anoGrafico) {
                return anoGrafico === ano ? 9 : 5;
            });

        grafico.update();

    });
}


/* =========================
   5. ATUALIZAR BOTÕES
========================= */

function atualizarBotoes(ano) {

    const botoes = document.querySelectorAll(
        ".seletor-anos .botao-ano"
    );

    botoes.forEach(function (botao) {

        const selecionado =
            Number(botao.dataset.ano) === ano;

        botao.classList.toggle(
            "selecionado",
            selecionado
        );

        botao.setAttribute(
            "aria-pressed",
            String(selecionado)
        );

    });
}


/* =========================
   6. ATUALIZAR INDICADORES
========================= */

function atualizarTela(ano, cuidados) {

    // 2022 usa IBGE, os demais anos usam Seade
    const censo = ano === 2022;

    const base = censo
        ? censo2022.dados
        : dadosSeadeDoAno(ano);

    // Dados demográficos
    const pop60 = numeroValido(
        base.populacao_60_mais,
        "populacao_60_mais"
    );

    const perc60 = numeroValido(
        base.percentual_60_mais,
        "percentual_60_mais"
    );

    const popAvancada = numeroValido(
        censo
            ? base.populacao_70_mais
            : base.populacao_75_mais,
        "populacao da faixa avançada"
    );

    // Confere se os dados de cuidado usam a mesma população
    const totalCuidados = numeroValido(
        cuidados.populacao_60_mais_base,
        "populacao_60_mais_base"
    );

    if (totalCuidados !== pop60) {
        throw new Error(
            `As bases 60+ de demografia e cuidados diferem em ${ano}.`
        );
    }

    // Necessidade estimada de ajuda
    const necessidadeAjuda = numeroValido(
        cuidados.indicadores_complementares
            ?.necessidade_ajuda_declarada,
        "necessidade_ajuda_declarada"
    );

    // Perfil de dependência elevada
    const elevado = cuidados.perfis.find(
        function (perfil) {
            return perfil.codigo === "dependencia_elevada";
        }
    );

    if (!elevado) {
        throw new Error(
            "Perfil de dependência elevada ausente."
        );
    }

    const dependenciaElevada = numeroValido(
        elevado.quantidade_estimada,
        "dependencia_elevada"
    );

    // Percentuais calculados para os cartões
    const percAvancada = 100 * popAvancada / pop60;

    const percAjuda = 100 * necessidadeAjuda / pop60;

    const percElevada = 100 * dependenciaElevada / pop60;


    /* -------------------------
       CARTÃO 1: POPULAÇÃO 60+
    ------------------------- */

    escrever(
        "populacao-60",
        numero(pop60)
    );

    escrever(
        "percentual-60",

        censo
            ? `${percentual(perc60)} nos setores com dados publicados`
            : `${percentual(perc60)} da população projetada`
    );


    /* -------------------------
   CARTÃO 2: COMPOSIÇÃO ETÁRIA
    ------------------------- */

    // Título do cartão
    escrever(
        "titulo-faixa-avancada",
        censo
            ? "Pessoas com 70+ entre os idosos"
            : "Pessoas com 75+ entre os idosos"
    );

    // Percentual em destaque
    escrever(
        "populacao-faixa-avancada",
        percentual(percAvancada)
    );

    // Quantidade de pessoas abaixo do percentual
    escrever(
        "descricao-faixa-avancada",
        `${numero(popAvancada)} pessoas · ` +
        `${censo ? "IBGE 2022" : "Seade"}`
    );

    /* -------------------------
       CARTÃO 3: AJUDA
    ------------------------- */

    escrever(
        "necessidade-ajuda",
        numero(necessidadeAjuda)
    );

    escrever(
        "descricao-ajuda",

        `${percentual(percAjuda)} das pessoas 60+ · estimativa`
    );


    /* -------------------------
       CARTÃO 4: DEPENDÊNCIA
    ------------------------- */

    escrever(
        "dependencia-elevada",
        numero(dependenciaElevada)
    );

    escrever(
        "descricao-dependencia",

        `${percentual(percElevada)} das pessoas 60+ · estimativa`
    );


    /* -------------------------
       CONTEXTO METODOLÓGICO
    ------------------------- */

    escrever(
        "contexto-ano",

        censo
            ? (
                "2022: Censo IBGE com cobertura etária de " +
                percentual(
                    censo2022.cobertura.percentual_populacional
                ) +
                " da população dos setores; " +
                "perfis estimados pelo TechCare."
            )
            : (
                `${ano}: projeção municipal da Seade; ` +
                "perfis de cuidado estimados pelo TechCare, " +
                "sem equivaler a demanda por vagas ou serviços."
            )
    );


    /* -------------------------
       LEITURA DO CENÁRIO
    ------------------------- */

    escrever(
        "subtitulo-leitura",

        `Interpretação dos indicadores selecionados para ${ano}.`
    );

    escrever(
        "leitura-estrutura",

        `São ${numero(popAvancada)} pessoas de ` +
        `${censo ? "70" : "75"} anos ou mais, ` +
        `${percentual(percAvancada)} da população 60+ de referência.`
    );

    escrever(
        "leitura-cuidados",

        `Estima-se que ${numero(necessidadeAjuda)} ` +
        "pessoas necessitem de ajuda e " +
        `${numero(dependenciaElevada)} estejam no perfil ` +
        "de dependência elevada."
    );

    escrever(
        "leitura-planejamento",

        censo
            ? (
                "A cobertura censitária não é integral. " +
                "Os indicadores ajudam a planejar ações, " +
                "mas não medem vagas disponíveis."
            )
            : (
                "As estimativas ajudam a planejar prevenção " +
                "e suporte; não são projeções oficiais " +
                "de demanda por SAD ou ILPI."
            )
    );


    /* -------------------------
       FONTES
    ------------------------- */

    escrever(
        "fonte-visao",

        censo
            ? (
                "Fontes: IBGE, Censo 2022 " +
                "(setores com dados etários publicados); " +
                "PNS 2019 e cálculos do TechCare para os perfis. " +
                "A série dos gráficos é exclusivamente " +
                "da Seade (2025–2050)."
            )
            : (
                `Fontes: Fundação Seade ` +
                `(projeção municipal para ${ano}); ` +
                "PNS 2019 e estimativas do TechCare para " +
                "os perfis de cuidado. Os gráficos apresentam " +
                "a série Seade de 2025 a 2050."
            )
    );

    // Destaca o ano escolhido
    atualizarBotoes(ano);

    // Destaca o ponto correspondente nos gráficos
    destacarAnoNosGraficos(ano);
}


/* =========================
   7. CARREGAR UM ANO
========================= */

async function selecionarAno(ano) {

    if (!ANOS_VISAO.includes(ano)) {
        return;
    }

    const solicitacao = ++ultimaSolicitacao;

    document.querySelector(
        ".grade-indicadores"
    ).setAttribute("aria-busy", "true");

    try {

        const cuidados = await obterCuidados(ano);

        // Evita que uma resposta antiga substitua a mais recente
        if (solicitacao !== ultimaSolicitacao) {
            return;
        }

        atualizarTela(ano, cuidados);

        limparErro();

    } catch (erro) {

        if (solicitacao === ultimaSolicitacao) {

            console.error(
                "Visão Geral:",
                erro
            );

            mostrarErro(
                "Não foi possível atualizar a Visão Geral. " +
                "Verifique o FastAPI e o console do navegador."
            );
        }

    } finally {

        if (solicitacao === ultimaSolicitacao) {

            document.querySelector(
                ".grade-indicadores"
            ).removeAttribute("aria-busy");

        }

    }
}


/* =========================
   8. CONFIGURAR OS BOTÕES
========================= */

function configurarBotoes() {

    const botoes = document.querySelectorAll(
        ".seletor-anos .botao-ano"
    );

    botoes.forEach(function (botao) {

        botao.addEventListener("click", function () {

            const ano = Number(botao.dataset.ano);

            selecionarAno(ano);

        });

    });
}


/* =========================
   9. INICIAR A PÁGINA
========================= */

async function iniciarVisaoGeral() {

    configurarBotoes();

    try {

        // Consultar Censo 2022 e projeções da Seade
        const [censo, seade] = await Promise.all([

            buscarJson(
                "/demografia/faixas-etarias-2022"
            ),

            buscarJson(
                "/demografia/serie-etaria-seade"
            )

        ]);

        // Validar formatos recebidos
        if (
            !censo.dados ||
            !censo.cobertura ||
            !Array.isArray(seade.dados)
        ) {
            throw new Error(
                "Formato inesperado nas APIs de demografia."
            );
        }

        const anos = seade.dados.map(function (item) {
            return Number(item.ano);
        });

        if (
            [2025, 2030, 2040, 2050].some(
                ano => !anos.includes(ano)
            )
        ) {
            throw new Error(
                "Série Seade incompleta."
            );
        }

        // Armazena os dados
        censo2022 = censo;

        serieSeade = seade.dados.slice().sort(
            (a, b) => a.ano - b.ano
        );

        // Cria os dois gráficos
        criarGraficos();

        // Carrega os indicadores iniciais de 2022
        await selecionarAno(2022);

    } catch (erro) {

        console.error(
            "Falha ao iniciar Visão Geral:",
            erro
        );

        mostrarErro(
            "Não foi possível carregar os dados. " +
            "Confira as APIs e a biblioteca Chart.js."
        );

    }
}


// Executa após o HTML ser carregado
document.addEventListener(
    "DOMContentLoaded",
    iniciarVisaoGeral
);
