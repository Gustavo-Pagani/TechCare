
/* =========================================
   TECHCARE - METODOLOGIA
   Carregamento dos indicadores municipais
========================================= */

// Endereço da API
const urlIndicadores = "http://127.0.0.1:8000/api/v1/indicadores/resumo-municipal";

// Formatação dos números brasileiros
const formatoNumero = new Intl.NumberFormat("pt-BR");

const formatoDecimal = new Intl.NumberFormat("pt-BR", {
    minimumFractionDigits: 1,
    maximumFractionDigits: 1
});

const formatoMoeda = new Intl.NumberFormat("pt-BR", {
    style: "currency",
    currency: "BRL"
});


// Busca os indicadores no backend
async function carregarIndicadores() {

    try {

        const resposta = await fetch(urlIndicadores);

        if (!resposta.ok) {
            throw new Error("Erro ao consultar a API");
        }

        // Converte a resposta JSON em objeto JavaScript
        const resultado = await resposta.json();

        const dados = resultado.dados;

        // Preenche os quatro indicadores
        document.getElementById("indicador-populacao-idosa").textContent =
            formatoDecimal.format(dados.percentual_60_mais) + "%";

        document.getElementById("indicador-populacao-70").textContent =
            formatoDecimal.format(dados.percentual_70_entre_idosos) + "%";

        document.getElementById("indicador-geracao-chegando").textContent =
            formatoNumero.format(dados.geracao_chegando);

        document.getElementById("indicador-renda-responsavel").textContent =
            formatoMoeda.format(dados.renda_media_responsavel);

    } catch (erro) {

        console.error("Erro ao carregar indicadores:", erro);

    }
}

// Executa quando a página é carregada
carregarIndicadores();
