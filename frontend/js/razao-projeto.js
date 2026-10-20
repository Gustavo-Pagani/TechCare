
/* =========================================================
   TECHCARE - RAZÃO DO PROJETO
   Indicadores e gráfico da população 60+
========================================================= */


/* =========================
   1. CONFIGURAÇÕES
========================= */

const enderecoApi = "http://127.0.0.1:8000/api/v1";

const formatoNumero = new Intl.NumberFormat("pt-BR");

const formatoPercentual = new Intl.NumberFormat("pt-BR", {
    minimumFractionDigits: 1,
    maximumFractionDigits: 1
});

let graficoPopulacao = null;
let anosDisponiveis = [];


/* =========================
   2. CONSULTAR AS APIs
========================= */

async function consultarApi(caminho) {

    const resposta = await fetch(enderecoApi + caminho);

    if (!resposta.ok) {
        throw new Error("Erro na API: " + resposta.status);
    }

    return await resposta.json();

}


/* =========================
   3. PREENCHER OS CARTÕES
========================= */

function preencherCartoes(resumo, projecoes) {

    const valores = {};

    projecoes.dados.forEach(function (item) {
        valores[item.ano] = item.populacao_60_mais;
    });

    document.getElementById("populacao-idosa-2022").textContent =
        formatoNumero.format(
            resumo.dados.populacao_60_mais_publicada
        );

    document.getElementById("populacao-idosa-2030").textContent =
        formatoNumero.format(valores[2030]);

    document.getElementById("populacao-idosa-2050").textContent =
        formatoNumero.format(valores[2050]);

    document.getElementById("crescimento-idosos").textContent =
        "+" + formatoPercentual.format(
            projecoes.crescimento_2025_2050_percentual
        ) + "%";

}


/* =========================
   4. CRIAR O GRÁFICO
========================= */

function criarGrafico(projecoes) {

    const canvas = document.getElementById(
        "grafico-populacao-idosa"
    );

    anosDisponiveis = projecoes.dados.map(function (item) {
        return Number(item.ano);
    });

    const populacoes = projecoes.dados.map(function (item) {
        return Number(item.populacao_60_mais);
    });

    graficoPopulacao = new Chart(canvas, {

        type: "line",

        data: {
            labels: anosDisponiveis,

            datasets: [{
                label: "População 60+",
                data: populacoes,

                borderColor: "#099da0",
                backgroundColor: "rgba(9, 157, 160, 0.12)",

                borderWidth: 3,
                tension: 0.3,
                fill: true,

                pointRadius: 5,
                pointHoverRadius: 9,
                pointBackgroundColor: "#099da0"
            }]
        },

        options: {
            responsive: true,
            maintainAspectRatio: false,

            plugins: {
                legend: {
                    display: false
                },

                tooltip: {
                    callbacks: {
                        label: function (contexto) {
                            return formatoNumero.format(
                                contexto.parsed.y
                            ) + " pessoas";
                        }
                    }
                }
            },

            scales: {
                x: {
                    grid: {
                        display: false
                    }
                },

                y: {
                    beginAtZero: false,

                    ticks: {
                        callback: function (valor) {
                            return formatoNumero.format(valor);
                        }
                    }
                }
            }
        }

    });

}


/* =========================
   5. BOTÕES DOS ANOS
========================= */

function selecionarAno(ano) {

    document.querySelectorAll(".botao-ano").forEach(
        function (botao) {

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
        }
    );

    if (graficoPopulacao) {

        graficoPopulacao.data.datasets[0].pointRadius =
            anosDisponiveis.map(function (anoGrafico) {
                return anoGrafico === ano ? 9 : 5;
            });

        graficoPopulacao.update();

    }

}

function configurarBotoes() {

    document.querySelectorAll(".botao-ano").forEach(
        function (botao) {

            botao.addEventListener("click", function () {
                selecionarAno(Number(botao.dataset.ano));
            });

        }
    );

    selecionarAno(2025);

}


/* =========================
   6. INICIAR A PÁGINA
========================= */

async function iniciarRazaoProjeto() {

    try {

        // Consulta as duas APIs
        const [resumo, projecoes] = await Promise.all([

            consultarApi("/indicadores/resumo-municipal"),

            consultarApi("/projecoes/municipio")

        ]);

        // Preenche os cartões
        preencherCartoes(resumo, projecoes);

        // Cria o gráfico
        criarGrafico(projecoes);

        // Ativa os botões de seleção
        configurarBotoes();

        console.log("Razão do Projeto carregada!");

    } catch (erro) {

        console.error(
            "Erro ao carregar Razão do Projeto:",
            erro
        );

        document.querySelector(".nota-grafico").textContent =
            "Não foi possível carregar os dados. " +
            "Verifique se o FastAPI está funcionando " +
            "e se a biblioteca Chart.js foi carregada.";

    }

}

document.addEventListener(
    "DOMContentLoaded",
    iniciarRazaoProjeto
);
