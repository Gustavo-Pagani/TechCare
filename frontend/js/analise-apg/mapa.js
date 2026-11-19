/* =========================================================
   TECHCARE - ANÁLISE POR APG - MAPA

   Responsabilidades:
   1. Criar o mapa Leaflet
   2. Colorir as APGs pela demanda estimada de cuidado
   3. Encaminhar a seleção de uma região para a página
   4. Destacar a APG selecionada
========================================================= */

import {
    FAIXAS_CUIDADO,
    inteiro,
    formatarNumero,
    escaparHTML
} from "./dados.js";

let mapaAPG = null;
let camadaAPGs = null;
let limitesCampinas = null;
let idAPGSelecionada = null;


/* =========================
   1. DEFINIR AS CORES
========================= */

function corPorDemanda(valor) {

    const demanda = inteiro(valor, "demanda_cuidado");

    const faixa = FAIXAS_CUIDADO.find(function (item) {
        return demanda <= item.limite;
    });

    return faixa.cor;
}


/* =========================
   2. CRIAR E ATUALIZAR O MAPA
========================= */

export function criarMapa() {
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

export function configurarCamadaGeoJSON(geojson, aoSelecionarAPG) {
    if (camadaAPGs) {
        mapaAPG.removeLayer(camadaAPGs);
    }

    camadaAPGs = L.geoJSON(geojson, {
        style: function (feature) {
            return {
                color: "#ffffff",
                weight: 2.2,
                opacity: 1,
                fillColor: corPorDemanda(feature.properties.demanda_cuidado),
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
                aoSelecionarAPG(idAPG);
            });

            camada.on("mouseover", function () {

                camada.setStyle({
                    weight: idAPG === idAPGSelecionada ? 4 : 3,
                    color: idAPG === idAPGSelecionada ? "#0b2859" : "#fff",
                    fillOpacity: 1
                });
            });

            camada.on("mouseout", function () {

                camada.setTooltipContent(escaparHTML(nome));

                destacarSelecaoNoMapa(idAPGSelecionada);

            });

            // Permite ativar a região com Enter ou espaço quando
            // o elemento vetorial receber foco pelo teclado.
            camada.on("keypress", function (evento) {
                const tecla = evento.originalEvent?.key;

                if (tecla === "Enter" || tecla === " ") {
                    evento.originalEvent.preventDefault();
                    aoSelecionarAPG(idAPG);
                }
            });
        }
    }).addTo(mapaAPG);

    limitesCampinas = camadaAPGs.getBounds();

    if (!limitesCampinas.isValid()) {
        throw new Error("Os limites geográficos das APGs são inválidos.");
    }

    // Aplica o destaque depois de criar os polígonos.
    destacarSelecaoNoMapa(idAPGSelecionada);
}


/* =========================
   3. SELEÇÃO E ENQUADRAMENTO
========================= */

export function destacarSelecaoNoMapa(idAPG) {
    idAPGSelecionada = idAPG;

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

export function mostrarCampinasInteira() {
    if (mapaAPG && limitesCampinas?.isValid()) {
        mapaAPG.fitBounds(limitesCampinas, {
            padding: [24, 24],
            maxZoom: 12,
            animate: true
        });
    }
}