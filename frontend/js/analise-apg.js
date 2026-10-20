/* =========================================================
   TECHCARE - ANÁLISE POR APG

   APIs reais utilizadas:
   GET /api/v1/territorio/geojson?ano=2022
   GET /api/v1/territorio/apg/{id_apg}?ano=2022
   GET /api/v1/cuidados/perfis-apg?ano=2022&id_apg=2

   O mapa usa Leaflet e as geometrias GeoJSON do PostgreSQL.
   NÃO utiliza imagens ou números inventados.
========================================================= */

const API_APG = "http://127.0.0.1:8000/api/v1";
const ANOS_APG = [2022, 2030, 2040, 2050];

const numeroBR = new Intl.NumberFormat("pt-BR");
const percentualBR = new Intl.NumberFormat("pt-BR", {
    minimumFractionDigits: 1,
    maximumFractionDigits: 2
});

const CORES_POPULACAO = {
    baixa: "#58bd80",       // Até 40 mil
    moderada: "#f6c94e",   // Acima de 40 mil até 70 mil
    alta: "#ffa33c",       // Acima de 70 mil até 100 mil
    muitoAlta: "#ee535b"   // Acima de 100 mil
};

let mapaAPG = null;
let camadaAPGs = null;
let limitesCampinas = null;
let anoAtualAPG = 2022;
let idAPGSelecionada = null;
let dadosMapaAtual = null;
let carregandoAnoAPG = false;
let versaoConsultaDetalhe = 0;

// Guarda respostas do mapa para evitar consultas repetidas.
const cacheMapas = new Map();


/* =========================
   1. FUNÇÕES AUXILIARES
========================= */

function porId(id) {
    const elemento = document.getElementById(id);

    if (!elemento) {
        throw new Error(`Elemento HTML não encontrado: ${id}`);
    }

    return elemento;
}

function inteiro(valor, nome) {
    const convertido = Number(valor);

    if (!Number.isFinite(convertido) || convertido < 0) {
        throw new Error(`Valor inválido da API: ${nome}`);
    }

    return Math.round(convertido);
}

function porcentagem(valor, nome) {
    const convertido = Number(valor);

    if (!Number.isFinite(convertido) || convertido < 0 || convertido > 100) {
        throw new Error(`Percentual inválido da API: ${nome}`);
    }

    return convertido;
}

function formatarNumero(valor) {
    return numeroBR.format(valor);
}

function formatarPorcentagem(valor) {
    return percentualBR.format(valor) + "%";
}

// Evita interpretar nomes e textos provenientes do banco como HTML.
function escaparHTML(valor) {
    return String(valor ?? "").replace(/[&<>"']/g, function (caractere) {
        return {
            "&": "&amp;",
            "<": "&lt;",
            ">": "&gt;",
            '"': "&quot;",
            "'": "&#39;"
        }[caractere];
    });
}

function informarErro(mensagem) {
    const aviso = porId("erro-apg");
    aviso.textContent = mensagem;
    aviso.hidden = false;
}

function limparErro() {
    const aviso = porId("erro-apg");
    aviso.textContent = "";
    aviso.hidden = true;
}

async function buscarAPG(caminho) {
    const resposta = await fetch(API_APG + caminho);

    if (!resposta.ok) {
        throw new Error(`API ${caminho}: HTTP ${resposta.status}`);
    }

    return resposta.json();
}

async function obterMapa(ano) {
    if (!cacheMapas.has(ano)) {
        const dados = await buscarAPG(`/territorio/geojson?ano=${ano}`);
        validarGeoJSON(dados, ano);
        cacheMapas.set(ano, dados);
    }

    return cacheMapas.get(ano);
}

function validarGeoJSON(dados, ano) {
    if (
        !dados ||
        dados.type !== "FeatureCollection" ||
        !Array.isArray(dados.features) ||
        dados.features.length !== 17
    ) {
        throw new Error("A API não retornou as 17 geometrias das APGs.");
    }

    const ids = new Set();

    dados.features.forEach(function (feature) {
        const propriedades = feature.properties;
        const id = Number(propriedades?.id_apg);

        if (
            !Number.isInteger(id) ||
            !propriedades.codigo_apg ||
            !feature.geometry ||
            Number(propriedades.ano) !== ano ||
            ids.has(id)
        ) {
            throw new Error("GeoJSON territorial incompleto ou duplicado.");
        }

        inteiro(propriedades.populacao_total, "populacao_total");
        inteiro(propriedades.populacao_60_mais, "populacao_60_mais");
        porcentagem(propriedades.percentual_60_mais, "percentual_60_mais");
        ids.add(id);
    });
}

function corPorPopulacao(valor) {
    const populacao = inteiro(valor, "populacao_total");

    if (populacao <= 40000) return CORES_POPULACAO.baixa;
    if (populacao <= 70000) return CORES_POPULACAO.moderada;
    if (populacao <= 100000) return CORES_POPULACAO.alta;
    return CORES_POPULACAO.muitoAlta;
}


/* =========================
   2. CONFIGURAÇÃO DO MAPA
========================= */

function criarMapa() {
    if (typeof L === "undefined") {
        throw new Error(
            "A biblioteca Leaflet não foi carregada. Verifique a conexão com a internet."
        );
    }

    mapaAPG = L.map("mapa-apgs", {
        zoomControl: true,
        attributionControl: false,
        scrollWheelZoom: true,
        zoomSnap: 0.25,
        preferCanvas: false
    });

    // Não usamos mapas de terceiros como fundo.
    // Somente os polígonos territoriais disponíveis no banco TechCare.
}

function configurarCamadaGeoJSON(geojson) {
    if (camadaAPGs) {
        mapaAPG.removeLayer(camadaAPGs);
    }

    camadaAPGs = L.geoJSON(geojson, {
        style: function (feature) {
            return {
                color: "#ffffff",
                weight: 2.2,
                opacity: 1,
                fillColor: corPorPopulacao(feature.properties.populacao_total),
                fillOpacity: .96
            };
        },

        onEachFeature: function (feature, camada) {
            const propriedade = feature.properties;
            const idAPG = Number(propriedade.id_apg);
            const nome = String(propriedade.codigo_apg);

            camada.bindTooltip(escaparHTML(nome), {
                permanent: true,
                direction: "center",
                className: "etiqueta-apg",
                opacity: 1,
                interactive: false
            });

            camada.on("click", function () {
                if (!carregandoAnoAPG) {
                    selecionarAPG(idAPG);
                }
            });

            camada.on("mouseover", function () {
                camada.setStyle({
                    weight: idAPG === idAPGSelecionada ? 4 : 3,
                    color: idAPG === idAPGSelecionada ? "#0b2859" : "#fff",
                    fillOpacity: 1
                });
            });

            camada.on("mouseout", destacarSelecaoNoMapa);

            // Permite ativar a região com Enter ou espaço quando
            // o elemento vetorial receber foco pelo teclado.
            camada.on("keypress", function (evento) {
                const tecla = evento.originalEvent?.key;
                if (tecla === "Enter" || tecla === " ") {
                    evento.originalEvent.preventDefault();
                    selecionarAPG(idAPG);
                }
            });
        }
    }).addTo(mapaAPG);

    limitesCampinas = camadaAPGs.getBounds();

    if (!limitesCampinas.isValid()) {
        throw new Error("Os limites geográficos das APGs são inválidos.");
    }

    // Aplica o destaque depois de criar os polígonos.
    destacarSelecaoNoMapa();
}

function destacarSelecaoNoMapa() {
    if (!camadaAPGs) return;

    camadaAPGs.eachLayer(function (camada) {
        const id = Number(camada.feature?.properties?.id_apg);
        const selecionada = id === idAPGSelecionada;

        camada.setStyle({
            color: selecionada ? "#0b2859" : "#fff",
            weight: selecionada ? 4 : 2.2,
            fillOpacity: selecionada ? 1 : .96
        });

        if (selecionada) {
            camada.bringToFront();
        }
    });
}

function mostrarCampinasInteira() {
    if (mapaAPG && limitesCampinas?.isValid()) {
        mapaAPG.fitBounds(limitesCampinas, {
            padding: [24, 24],
            maxZoom: 12,
            animate: true
        });
    }
}

function atualizarLegenda(ano) {
    porId("titulo-legenda").textContent =
        ano === 2022
            ? "POPULAÇÃO TOTAL · 2022"
            : `POPULAÇÃO ESTIMADA · ${ano}`;
}


/* =========================
   3. PAINEL SEM APG SELECIONADA
========================= */

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
                return Number(b.populacao_total) - Number(a.populacao_total);
            })
            .slice(0, 2);

        maioresTexto = "Maiores populações totais em " + anoAtualAPG + ": " +
            maiores.map(function (item) {
                return item.codigo_apg + " (" +
                    formatarNumero(item.populacao_total) + ")";
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
   4. CONSULTAR OS DETALHES DA APG
========================= */

async function consultarDetalhes(idAPG, ano) {
    const [territorio, cuidados] = await Promise.all([
        buscarAPG(`/territorio/apg/${idAPG}?ano=${ano}`),
        buscarAPG(`/cuidados/perfis-apg?ano=${ano}&id_apg=${idAPG}`)
    ]);

    if (
        Number(territorio.id_apg) !== idAPG ||
        Number(territorio.ano_selecionado) !== ano ||
        !territorio.indicadores ||
        !Array.isArray(territorio.serie_populacional) ||
        territorio.serie_populacional.length !== 4 ||
        Number(cuidados.ano) !== ano ||
        !Array.isArray(cuidados.apgs) ||
        cuidados.apgs.length !== 1 ||
        Number(cuidados.apgs[0].id_apg) !== idAPG
    ) {
        throw new Error("Os detalhes recebidos da APG estão incompletos.");
    }

    return { territorio, cuidado: cuidados.apgs[0] };
}

function obterIndicador(indicadores, codigo) {
    const item = indicadores[codigo];

    if (!item || item.valor === null || item.valor === undefined) {
        throw new Error(`Indicador não encontrado: ${codigo}`);
    }

    return Number(item.valor);
}

function validarDetalhes(territorio, cuidado, ano) {
    const indicadores = territorio.indicadores;
    const total = inteiro(obterIndicador(indicadores, "populacao_total"), "populacao_total");
    const idosos = inteiro(obterIndicador(indicadores, "populacao_60_mais"), "populacao_60_mais");
    const chavePercentual = ano === 2022
        ? "percentual_60_mais_setores_com_dado"
        : "percentual_60_mais";
    const participacao = porcentagem(
        obterIndicador(indicadores, chavePercentual),
        chavePercentual
    );

    const cobertura = ano === 2022
        ? porcentagem(
            obterIndicador(indicadores, "cobertura_populacional_dado_60_mais"),
            "cobertura_populacional_dado_60_mais"
        )
        : null;

    if (!Array.isArray(cuidado.perfis) || cuidado.perfis.length !== 4) {
        throw new Error("Os quatro perfis de cuidado não foram recebidos.");
    }

    const perfis = ["autonomo", "apoio_leve", "dependencia_parcial", "dependencia_elevada"]
        .map(function (codigo) {
            const perfil = cuidado.perfis.find(function (item) {
                return item.codigo === codigo;
            });

            if (!perfil) throw new Error(`Perfil de cuidado ausente: ${codigo}`);

            return {
                codigo: codigo,
                nome: String(perfil.nome),
                quantidade: inteiro(perfil.quantidade_estimada, codigo),
                percentual: porcentagem(perfil.percentual, codigo)
            };
        });

    const baseCuidados = inteiro(cuidado.populacao_60_mais_base, "base de cuidados");

    if (baseCuidados !== idosos) {
        throw new Error("As populações 60+ das APIs territorial e de cuidados não coincidem.");
    }

    if (perfis.reduce((soma, item) => soma + item.quantidade, 0) !== baseCuidados) {
        throw new Error("A soma dos perfis de cuidado não corresponde à base 60+.");
    }

    const serie = territorio.serie_populacional.map(function (item) {
        return {
            ano: inteiro(item.ano, "ano da série"),
            idosos: inteiro(item.populacao_60_mais, "população 60+ da série")
        };
    });

    if (serie.some(item => !ANOS_APG.includes(item.ano))) {
        throw new Error("A série temporal contém anos inesperados.");
    }

    return { total, idosos, participacao, cobertura, perfis, serie };
}


/* =========================
   5. EXIBIR UMA APG SELECIONADA
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
    destacarSelecaoNoMapa();
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

    destacarSelecaoNoMapa();
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
   6. ALTERNAR 2022 / 2030 / 2040 / 2050
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
            ? "Fonte: IBGE, Censo 2022. Dados 60+ limitados aos setores com divulgação etária; " +
              "o percentual 60+ usa apenas a população desses setores como denominador. " +
              "Dados ausentes não equivalem a zero. Perfis de cuidado: estimativas TechCare/PNS 2019."
            : `Fonte: Fundação Seade (projeções municipais) e TechCare (distribuição estimada por APG para ${ano}). ` +
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

        configurarCamadaGeoJSON(geojson);
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
   7. INICIAR A PÁGINA
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
