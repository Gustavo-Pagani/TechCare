/* =========================================================
   TECHCARE - ANÁLISE POR APG - PÁGINA

   Responsabilidades:
   1. Iniciar a página e configurar os botões
   2. Coordenar as consultas e o mapa
   3. Atualizar o ano selecionado
   4. Exibir os detalhes, a legenda e as fontes
   5. Tratar as falhas de carregamento
========================================================= */

import {
    ANOS_APG,
    FAIXAS_CUIDADO,
    obterMapa,
    consultarDetalhes,
    validarDetalhes,
    formatarNumero,
    formatarPorcentagem,
    escaparHTML
} from "./dados.js";

import {
    criarMapa,
    configurarCamadaGeoJSON,
    destacarSelecaoNoMapa,
    mostrarCampinasInteira
} from "./mapa.js";

let anoAtualAPG = 2022;
let idAPGSelecionada = null;
let dadosMapaAtual = null;
let carregandoAnoAPG = false;
let versaoConsultaDetalhe = 0;


/* =========================
   1. ELEMENTOS E AVISOS
========================= */

function porId(id) {
    const elemento = document.getElementById(id);

    if (!elemento) {
        throw new Error(`Elemento HTML não encontrado: ${id}`);
    }

    return elemento;
}

function informarErro() {
    mostrarErroDados();
}

function limparErro() {
    limparErroDados();
}


/* =========================
   2. LEGENDA E PAINEL SEM SELEÇÃO
========================= */

function atualizarLegenda(ano) {

    const legenda = document.querySelector(".legenda-mapa");

    const faixasHTML = FAIXAS_CUIDADO.map(function (faixa) {
        return `
            <div>
                <span class="cor-legenda"
                      style="background: ${faixa.cor};"></span>
                ${faixa.texto}
            </div>
        `;
    }).join("");

    legenda.innerHTML = `
        <strong id="titulo-legenda">
            DEMANDA ESTIMADA DE CUIDADO · ${ano}
        </strong>
        <small>Dependência parcial + elevada</small>
        ${faixasHTML}
    `;

    legenda.hidden = false;
}

function preencherEstadoVazio() {
    porId("titulo-apg-selecionada").textContent = "Selecione uma APG";
    porId("descricao-selecao").textContent =
        "Clique em uma região no mapa para abrir os detalhes territoriais.";

    let maioresTexto = "";

    if (dadosMapaAtual?.features?.length) {
        const maiores = dadosMapaAtual.features
            .map(function (feature) {
                return feature.properties;
            })
            .slice()
            .sort(function (a, b) {
                return Number(b.demanda_cuidado) - Number(a.demanda_cuidado);
            })
            .slice(0, 2);

        maioresTexto = "Maiores demandas estimadas de cuidado em " +
            anoAtualAPG + ": " +
            maiores.map(function (item) {
                return item.codigo_apg + " (" +
                    formatarNumero(item.demanda_cuidado) +
                    " pessoas)";
            }).join(" e ") + ".";
    }

    // O template é fixo; somente o texto dinâmico é inserido com textContent.
    porId("conteudo-apg").innerHTML = `
        <div class="estado-vazio">
            <svg viewBox="0 0 24 24" class="icone-mapa-vazio" aria-hidden="true">
                <path d="m3 6 6-3 6 3 6-3v15l-6 3-6-3-6 3V6Z"/>
                <path d="M9 3v15M15 6v15"/>
            </svg>
            <h3>Nenhuma APG selecionada.</h3>
            <p>Escolha uma região do mapa para visualizar população,
               indicadores e perfis estimados de cuidado.</p>
            <p class="resumo-municipal" id="maiores-apgs"></p>
        </div>
    `;

    porId("maiores-apgs").textContent = maioresTexto;
}


/* =========================
   3. EXIBIR E SELECIONAR UMA APG
========================= */

function mostrarDetalhes(territorio, cuidado, ano) {
    const dados = validarDetalhes(territorio, cuidado, ano);
    const nome = String(territorio.codigo_apg || territorio.nome_apg);

    porId("titulo-apg-selecionada").textContent = nome;
    porId("descricao-selecao").textContent =
        ano === 2022
            ? "Indicadores territoriais do Censo 2022 e estimativas de cuidado."
            : `Cenário territorial estimado pelo TechCare para ${ano}.`;

    const cartaoCobertura = ano === 2022
        ? `<div class="indicador-apg">
               <span>Cobertura do dado etário</span>
               <strong>${formatarPorcentagem(dados.cobertura)}</strong>
               <small>População dos setores com idade publicada</small>
           </div>`
        : `<div class="indicador-apg">
               <span>Ano do cenário</span>
               <strong>${ano}</strong>
               <small>Estimativa por APG, não projeção oficial Seade</small>
           </div>`;

    const linhasPerfis = dados.perfis.map(function (perfil) {
        return `
            <div class="linha-perfil">
                <div class="linha-texto">
                    <span>${escaparHTML(perfil.nome)}</span>
                    <b>${formatarPorcentagem(perfil.percentual)} · ${formatarNumero(perfil.quantidade)}</b>
                </div>
                <div class="trilho-perfil">
                    <div class="barra-perfil barra-${perfil.codigo}"
                         style="width: ${perfil.percentual}%;"></div>
                </div>
            </div>
        `;
    }).join("");

    const serieHTML = dados.serie.map(function (item) {
        return `
            <li class="${item.ano === ano ? "ano-atual" : ""}">
                <b>${item.ano}</b>
                <strong>${formatarNumero(item.idosos)}</strong>
                <span>${item.ano === 2022 ? "Censo parcial" : "Estimativa TechCare"}</span>
            </li>
        `;
    }).join("");

    // As informações numéricas vêm exclusivamente das duas APIs.
    porId("conteudo-apg").innerHTML = `
        <div class="grade-indicadores-apg">
            <div class="indicador-apg">
                <span>População total</span>
                <strong>${formatarNumero(dados.total)}</strong>
                <small>${ano === 2022 ? "Agregação censitária" : "Estimativa territorial"}</small>
            </div>
            <div class="indicador-apg">
                <span>População com 60+</span>
                <strong>${formatarNumero(dados.idosos)}</strong>
                <small>${ano === 2022 ? "Setores com idade divulgada" : "Estimativa territorial"}</small>
            </div>
            <div class="indicador-apg">
                <span>${ano === 2022 ? "Participação 60+*" : "Participação 60+"}</span>
                <strong>${formatarPorcentagem(dados.participacao)}</strong>
                <small>${ano === 2022 ? "Denominador: setores com dados etários" : "Da população total estimada"}</small>
            </div>
            ${cartaoCobertura}
        </div>

        <section class="bloco-detalhe">
            <h3>Perfis estimados de cuidado · ${ano}</h3>
            ${linhasPerfis}
        </section>

        <section class="bloco-detalhe">
            <h3>População 60+ por ano</h3>
            <ul class="lista-serie">${serieHTML}</ul>
            <p class="aviso-detalhe">2022 utiliza dados censitários publicados, com cobertura parcial.
               2030–2050 são estimativas territoriais; os períodos não constituem uma série homogênea de observações.</p>
        </section>

        <div class="orientacoes-apg">
            <h3>Para o planejamento público</h3>
            <p>Os indicadores podem apoiar o estudo de prevenção,
               atenção domiciliar e serviços de cuidado. Antes de decidir
               investimentos, é necessário considerar também a oferta,
               a capacidade de atendimento e a demanda efetivamente identificada.</p>
        </div>

        <p class="aviso-detalhe">*Os perfis representam estimativas populacionais
           do TechCare, baseadas em parâmetros da PNS 2019 e composição
           municipal da Seade. Não são diagnósticos nem vagas disponíveis.</p>

        <button type="button" class="botao-limpar" id="limpar-apg">
            Limpar seleção
        </button>
    `;

    porId("limpar-apg").addEventListener("click", limparSelecao);
    porId("conteudo-apg").scrollTop = 0;
}

function limparSelecao() {
    versaoConsultaDetalhe++;
    idAPGSelecionada = null;
    destacarSelecaoNoMapa(idAPGSelecionada);
    preencherEstadoVazio();
}

async function selecionarAPG(idAPG) {
    if (carregandoAnoAPG) return;

    idAPGSelecionada = idAPG;
    const minhaConsulta = ++versaoConsultaDetalhe;
    const anoConsultado = anoAtualAPG;

    const feature = dadosMapaAtual?.features.find(function (item) {
        return Number(item.properties.id_apg) === idAPG;
    });

    if (!feature) return;

    destacarSelecaoNoMapa(idAPGSelecionada);
    limparErro();
    porId("titulo-apg-selecionada").textContent = feature.properties.codigo_apg;
    porId("descricao-selecao").textContent = `Consultando indicadores de ${anoConsultado}...`;
    porId("conteudo-apg").innerHTML =
        '<p class="estado-carregando">Carregando dados da APG...</p>';

    try {
        const resultado = await consultarDetalhes(idAPG, anoConsultado);

        if (
            minhaConsulta !== versaoConsultaDetalhe ||
            idAPGSelecionada !== idAPG ||
            anoAtualAPG !== anoConsultado
        ) return;

        mostrarDetalhes(resultado.territorio, resultado.cuidado, anoConsultado);

    } catch (erro) {
        if (minhaConsulta !== versaoConsultaDetalhe) return;

        console.error("TechCare - detalhe da APG:", erro);
        informarErro("Não foi possível carregar os dados desta APG. Verifique o FastAPI.");
        porId("descricao-selecao").textContent = "Falha ao consultar a APG.";
        porId("conteudo-apg").innerHTML =
            '<p class="estado-carregando">Os indicadores estão indisponíveis no momento.</p>';
    }
}


/* =========================
   4. ALTERNAR 2022 / 2030 / 2040 / 2050
========================= */

function destacarBotaoAno(ano) {
    document.querySelectorAll(".seletor-anos .botao-ano").forEach(function (botao) {
        const ativo = Number(botao.dataset.ano) === ano;

        botao.classList.toggle("selecionado", ativo);
        botao.setAttribute("aria-pressed", String(ativo));
    });
}

function atualizarFonteAno(ano, meta) {
    const selo = porId("selo-natureza");

    selo.textContent = ano === 2022 ? "CENSO 2022" : "ESTIMATIVA TECHCARE";
    selo.classList.toggle("estimativa", ano !== 2022);

    porId("nota-metodologica").textContent =
        ano === 2022
            ? "Cores: soma estimada dos perfis de dependência parcial e elevada. " +
              "Fonte: IBGE, Censo 2022. Dados 60+ limitados aos setores com divulgação etária; " +
              "o percentual 60+ usa apenas a população desses setores como denominador. " +
              "Dados ausentes não equivalem a zero. Perfis de cuidado: estimativas TechCare/PNS 2019."
            : "Cores: soma estimada dos perfis de dependência parcial e elevada. " +
              `Fonte: Fundação Seade (projeções municipais) e TechCare (distribuição estimada por APG para ${ano}). ` +
              "Não são projeções oficiais da Seade por APG. Perfis de cuidado: estimativas do TechCare/PNS 2019.";
}

function alterarEstadoBotoes(desativados) {
    document.querySelectorAll(".seletor-anos .botao-ano").forEach(function (botao) {
        botao.disabled = desativados;
    });
}

async function mudarAno(ano) {
    if (!ANOS_APG.includes(ano) || carregandoAnoAPG) return;

    carregandoAnoAPG = true;
    versaoConsultaDetalhe++;  // Cancela respostas antigas do painel.
    alterarEstadoBotoes(true);
    limparErro();

    porId("mensagem-mapa").textContent = `Carregando dados de ${ano}...`;
    porId("mensagem-mapa").hidden = false;

    const primeiroCarregamento = !dadosMapaAtual;
    const idAnterior = idAPGSelecionada;

    try {
        // Busca geometria e, quando necessário, os dados da APG selecionada.
        const [geojson, detalhes] = await Promise.all([
            obterMapa(ano),
            idAnterior !== null ? consultarDetalhes(idAnterior, ano) : Promise.resolve(null)
        ]);

        // Validação ANTES de trocar o conteúdo, evitando exibir dados parciais.
        if (detalhes) {
            validarDetalhes(detalhes.territorio, detalhes.cuidado, ano);
        }

        anoAtualAPG = ano;
        dadosMapaAtual = geojson;

        configurarCamadaGeoJSON(geojson, selecionarAPG);
        atualizarLegenda(ano);
        atualizarFonteAno(ano, geojson.meta);
        destacarBotaoAno(ano);

        if (primeiroCarregamento) {
            mostrarCampinasInteira();
        }

        if (detalhes) {
            mostrarDetalhes(detalhes.territorio, detalhes.cuidado, ano);
        } else {
            preencherEstadoVazio();
        }

    } catch (erro) {
        console.error("TechCare - mapa de APGs:", erro);

        informarErro(
            "Não foi possível carregar o mapa ou os indicadores. " +
            "Verifique se o FastAPI está ativo e se a biblioteca Leaflet carregou."
        );

        if (primeiroCarregamento) {
            porId("mensagem-mapa").textContent = "Mapa indisponível.";
        }

    } finally {
        carregandoAnoAPG = false;
        alterarEstadoBotoes(false);

        if (dadosMapaAtual) {
            porId("mensagem-mapa").hidden = true;
        }
    }
}


/* =========================
   5. INICIAR A PÁGINA
========================= */

function iniciarAnaliseAPG() {
    document.querySelectorAll(".seletor-anos .botao-ano").forEach(function (botao) {
        botao.addEventListener("click", function () {
            mudarAno(Number(botao.dataset.ano));
        });
    });

    porId("botao-mapa-inteiro").addEventListener("click", mostrarCampinasInteira);

    try {
        criarMapa();
        mudarAno(2022);

    } catch (erro) {
        console.error("TechCare - inicialização APG:", erro);

        informarErro(erro.message);
        porId("mensagem-mapa").textContent = "Não foi possível abrir o mapa.";
    }
}

document.addEventListener("DOMContentLoaded", iniciarAnaliseAPG);