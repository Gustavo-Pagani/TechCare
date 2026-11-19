/* =========================================================
   TECHCARE - ANÁLISE POR APG - DADOS

   Responsabilidades:
   1. Consultar as APIs territoriais e de cuidado
   2. Validar os dados recebidos
   3. Calcular a demanda estimada de cuidado
   4. Guardar os mapas consultados em cache
   5. Disponibilizar formatação e faixas compartilhadas
========================================================= */


/* =========================
   1. CONFIGURAÇÕES
========================= */

// API_BASE é definida no arquivo compartilhado app.js.
const API_APG = API_BASE;

export const ANOS_APG = [2022, 2030, 2040, 2050];

const numeroBR = new Intl.NumberFormat("pt-BR");

const percentualBR = new Intl.NumberFormat("pt-BR", {
    minimumFractionDigits: 1,
    maximumFractionDigits: 2
});

// Faixas fixas para comparar a demanda estimada entre os anos.
export const FAIXAS_CUIDADO = [
    {
        limite: 2000,
        cor: "#58bd80",
        texto: "Baixa: até 2.000 pessoas"
    },
    {
        limite: 4000,
        cor: "#f6c94e",
        texto: "Moderada: 2.001 a 4.000 pessoas"
    },
    {
        limite: 6000,
        cor: "#ffa33c",
        texto: "Alta: 4.001 a 6.000 pessoas"
    },
    {
        limite: Infinity,
        cor: "#ee535b",
        texto: "Muito alta: acima de 6.000 pessoas"
    }
];

// Guarda respostas do mapa para evitar consultas repetidas.
const cacheMapas = new Map();


/* =========================
   2. VALIDAÇÃO E FORMATAÇÃO
========================= */

export function inteiro(valor, nome) {
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

export function formatarNumero(valor) {
    return numeroBR.format(valor);
}

export function formatarPorcentagem(valor) {
    return percentualBR.format(valor) + "%";
}

// Evita interpretar nomes e textos provenientes do banco como HTML.
export function escaparHTML(valor) {
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


/* =========================
   3. CONSULTAR E PREPARAR O MAPA
========================= */

async function buscarAPG(caminho) {
    const resposta = await fetch(API_APG + caminho);

    if (!resposta.ok) {
        throw new Error(`API ${caminho}: HTTP ${resposta.status}`);
    }

    return resposta.json();
}

// Soma os dois perfis utilizados na classificação do mapa.
function calcularDemandaCuidado(cuidado) {

    if (!Array.isArray(cuidado.perfis)) {
        throw new Error("A API não retornou os perfis de cuidado.");
    }

    const codigos = [
        "dependencia_parcial",
        "dependencia_elevada"
    ];

    let demanda = 0;

    codigos.forEach(function (codigo) {

        const encontrados = cuidado.perfis.filter(function (perfil) {
            return perfil.codigo === codigo;
        });

        if (encontrados.length !== 1) {
            throw new Error(`Perfil ausente ou duplicado: ${codigo}`);
        }

        const valor = encontrados[0].quantidade_estimada;
        const quantidade = Number(valor);

        if (
            valor === null ||
            valor === undefined ||
            valor === "" ||
            !Number.isSafeInteger(quantidade) ||
            quantidade < 0
        ) {
            throw new Error(`Quantidade inválida no perfil: ${codigo}`);
        }

        demanda += quantidade;

    });

    return demanda;
}

export async function obterMapa(ano) {

    if (!cacheMapas.has(ano)) {

        // Consulta as geometrias e os perfis das 17 APGs.
        const [dados, cuidados] = await Promise.all([
            buscarAPG(`/territorio/geojson?ano=${ano}`),
            buscarAPG(`/cuidados/perfis-apg?ano=${ano}`)
        ]);

        validarGeoJSON(dados, ano);

        if (
            Number(cuidados.ano) !== ano ||
            !Array.isArray(cuidados.apgs) ||
            cuidados.apgs.length !== 17
        ) {
            throw new Error("Os perfis das 17 APGs estão incompletos.");
        }

        const demandasPorAPG = new Map();

        cuidados.apgs.forEach(function (cuidado) {

            const id = Number(cuidado.id_apg);

            if (
                !Number.isInteger(id) ||
                demandasPorAPG.has(id)
            ) {
                throw new Error("APG inválida ou duplicada nos perfis.");
            }

            demandasPorAPG.set(
                id,
                calcularDemandaCuidado(cuidado)
            );

        });

        // Associa a demanda à geometria da mesma APG.
        dados.features.forEach(function (feature) {

            const id = Number(feature.properties.id_apg);

            if (!demandasPorAPG.has(id)) {
                throw new Error(`Demanda não encontrada para a APG ${id}.`);
            }

            feature.properties.demanda_cuidado =
                demandasPorAPG.get(id);

        });

        // Guarda apenas respostas completas e validadas.
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


/* =========================
   4. CONSULTAR E VALIDAR OS DETALHES
========================= */

export async function consultarDetalhes(idAPG, ano) {
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

export function validarDetalhes(territorio, cuidado, ano) {
    const indicadores = territorio.indicadores;

    const total = inteiro(
        obterIndicador(indicadores, "populacao_total"),
        "populacao_total"
    );

    const idosos = inteiro(
        obterIndicador(indicadores, "populacao_60_mais"),
        "populacao_60_mais"
    );

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

    const perfis = [
        "autonomo",
        "apoio_leve",
        "dependencia_parcial",
        "dependencia_elevada"
    ].map(function (codigo) {

        const perfil = cuidado.perfis.find(function (item) {
            return item.codigo === codigo;
        });

        if (!perfil) {
            throw new Error(`Perfil de cuidado ausente: ${codigo}`);
        }

        return {
            codigo: codigo,
            nome: String(perfil.nome),
            quantidade: inteiro(perfil.quantidade_estimada, codigo),
            percentual: porcentagem(perfil.percentual, codigo)
        };

    });

    const baseCuidados = inteiro(
        cuidado.populacao_60_mais_base,
        "base de cuidados"
    );

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