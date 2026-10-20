
/* =========================================================
   TECHCARE - PERFIS DE CUIDADO

   Responsabilidades:
   1. Consultar os perfis na API FastAPI
   2. Preencher os quatro cartões
   3. Atualizar as barras de porcentagem
   4. Permitir selecionar diferentes anos
   5. Atualizar informações metodológicas
   6. Tratar possíveis erros
========================================================= */


/* =========================
   1. CONFIGURAÇÕES
========================= */

// Endereço da API de perfis de cuidado
const API_CUIDADOS =
    "http://127.0.0.1:8000/api/v1/cuidados/perfis-municipio";

// Anos disponíveis na plataforma
const ANOS_PERMITIDOS = [2022, 2030, 2040, 2050];

// Formatação dos números para português brasileiro
const formatadorNumero = new Intl.NumberFormat("pt-BR");

const formatadorPercentual = new Intl.NumberFormat("pt-BR", {
    minimumFractionDigits: 1,
    maximumFractionDigits: 2
});

// Controle do carregamento
let carregandoPerfis = false;


/* =========================
   2. CONSULTAR A API
========================= */

async function consultarPerfis(ano) {

    const endereco = `${API_CUIDADOS}?ano=${ano}`;

    const resposta = await fetch(endereco);

    if (!resposta.ok) {
        throw new Error(
            `Erro ao consultar a API: ${resposta.status}`
        );
    }

    const dados = await resposta.json();

    return dados;
}


/* =========================
   3. PREENCHER OS QUATRO PERFIS
========================= */

function preencherPerfis(dados) {

    // Os códigos devem corresponder aos retornados pela API
    const codigosPerfis = [
        "autonomo",
        "apoio_leve",
        "dependencia_parcial",
        "dependencia_elevada"
    ];

    if (!Array.isArray(dados.perfis)) {
        throw new Error("A API não retornou a lista de perfis.");
    }

    // Organiza os perfis por código
    const perfisPorCodigo = {};

    dados.perfis.forEach(function (perfil) {
        perfisPorCodigo[perfil.codigo] = perfil;
    });

    // Confere os dados antes de atualizar a página
    codigosPerfis.forEach(function (codigo) {

        const perfil = perfisPorCodigo[codigo];

        if (!perfil) {
            throw new Error(`Perfil não encontrado: ${codigo}`);
        }

        const percentual = Number(perfil.percentual);
        const quantidade = Number(perfil.quantidade_estimada);

        if (
            !Number.isFinite(percentual) ||
            !Number.isFinite(quantidade) ||
            percentual < 0 ||
            percentual > 100 ||
            quantidade < 0
        ) {
            throw new Error(`Dados inválidos no perfil: ${codigo}`);
        }
    });

    // Atualiza os cartões
    codigosPerfis.forEach(function (codigo) {

        const perfil = perfisPorCodigo[codigo];

        const percentual = Number(perfil.percentual);

        const quantidade = Number(perfil.quantidade_estimada);

        // Atualiza o percentual
        document.getElementById(
            `percentual-${codigo}`
        ).textContent =
            formatadorPercentual.format(percentual) + "%";

        // Atualiza a quantidade de pessoas
        document.getElementById(
            `quantidade-${codigo}`
        ).textContent =
            formatadorNumero.format(quantidade) +
            " pessoas estimadas";

        // Atualiza a barra colorida
        document.getElementById(
            `barra-${codigo}`
        ).style.width = percentual + "%";

    });

}


/* =========================
   4. ATUALIZAR POPULAÇÃO DE REFERÊNCIA
========================= */

function atualizarPopulacaoBase(dados) {

    const populacao = Number(
        dados.populacao_60_mais_base
    );

    if (!Number.isFinite(populacao)) {
        throw new Error("População de referência inválida.");
    }

    const elemento = document.getElementById(
        "base-populacional"
    );

    elemento.textContent =
        "População 60+ de referência: " +
        formatadorNumero.format(populacao) +
        " pessoas (" + dados.ano + ")";

}


/* =========================
   5. ATUALIZAR FONTE METODOLÓGICA
========================= */

function atualizarFonte(dados) {

    const elemento = document.getElementById(
        "fonte-perfis"
    );

    const meta = dados.meta;

    if (!meta) {
        return;
    }

    elemento.textContent =
        `Fonte dos parâmetros: ${meta.fonte_parametros}. ` +
        `Composição demográfica: ${meta.fonte_composicao} ` +
        `(${meta.ano_composicao_seade}). ` +
        `População de referência: ${meta.fonte_populacao}. ` +
        `${meta.observacao || ""}`;

}


/* =========================
   6. ATUALIZAR BOTÃO SELECIONADO
========================= */

function destacarAnoSelecionado(ano) {

    const botoes = document.querySelectorAll(
        ".seletor-anos .botao-ano"
    );

    botoes.forEach(function (botao) {

        const anoBotao = Number(botao.dataset.ano);

        const selecionado = anoBotao === ano;

        // Altera a aparência visual
        botao.classList.toggle(
            "selecionado",
            selecionado
        );

        // Atualiza a informação de acessibilidade
        botao.setAttribute(
            "aria-pressed",
            String(selecionado)
        );

    });

}


/* =========================
   7. CARREGAR DADOS DO ANO
========================= */

async function carregarPerfisDoAno(ano) {

    // Impede anos que não existem
    if (!ANOS_PERMITIDOS.includes(ano)) {
        console.error("Ano inválido:", ano);
        return;
    }

    // Evita consultas simultâneas
    if (carregandoPerfis) {
        return;
    }

    carregandoPerfis = true;

    const botoes = document.querySelectorAll(
        ".seletor-anos .botao-ano"
    );

    // Desativa os botões durante o carregamento
    botoes.forEach(function (botao) {
        botao.disabled = true;
    });

    try {

        // Busca os dados no FastAPI
        const dados = await consultarPerfis(ano);

        // Confere se a resposta corresponde ao ano solicitado
        if (Number(dados.ano) !== ano) {
            throw new Error("A API retornou um ano diferente.");
        }

        // Atualiza os cartões
        preencherPerfis(dados);

        // Atualiza a população base
        atualizarPopulacaoBase(dados);

        // Atualiza a fonte metodológica
        atualizarFonte(dados);

        // Destaca o botão correspondente
        destacarAnoSelecionado(ano);

        console.log(
            `Perfis de Cuidado de ${ano} carregados com sucesso.`
        );

    } catch (erro) {

        console.error(
            "Erro ao carregar Perfis de Cuidado:",
            erro
        );

        document.getElementById(
            "base-populacional"
        ).textContent =
            "Não foi possível carregar os dados. " +
            "Verifique se o FastAPI está funcionando.";

    } finally {

        carregandoPerfis = false;

        // Reativa os botões
        botoes.forEach(function (botao) {
            botao.disabled = false;
        });

    }

}


/* =========================
   8. CONFIGURAR OS BOTÕES
========================= */

function configurarSelecaoAnos() {

    const botoes = document.querySelectorAll(
        ".seletor-anos .botao-ano"
    );

    botoes.forEach(function (botao) {

        botao.addEventListener("click", function () {

            const ano = Number(botao.dataset.ano);

            carregarPerfisDoAno(ano);

        });

    });

}


/* =========================
   9. INICIAR A PÁGINA
========================= */

function iniciarPerfisCuidado() {

    // Configura os eventos dos botões
    configurarSelecaoAnos();

    // Carrega inicialmente os dados de 2022
    carregarPerfisDoAno(2022);

}


// Executa quando o HTML estiver carregado
document.addEventListener(
    "DOMContentLoaded",
    iniciarPerfisCuidado
);
