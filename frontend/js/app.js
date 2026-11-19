// Endereço compartilhado da API do TechCare
const API_BASE = "http://127.0.0.1:8000/api/v1";

document.addEventListener("DOMContentLoaded", function () {

    const elementoSidebar = document.getElementById("sidebar");

    if (!elementoSidebar) {
        return;
    }

    /* =========================
       1. CARREGAR A SIDEBAR
    ========================= */

    fetch("/frontend/componentes/sidebar.html")

        .then(function (resposta) {

            if (!resposta.ok) {
                throw new Error("Não foi possível carregar a sidebar.");
            }

            return resposta.text();

        })

        .then(function (html) {

            elementoSidebar.innerHTML = html;

            /* =========================
               2. IDENTIFICAR A PÁGINA
            ========================= */

            const paginaAtual = window.location.pathname;

            const links = elementoSidebar.querySelectorAll(
                ".sidebar nav a"
            );

            /* =========================
               3. DESTACAR O ITEM ATIVO
            ========================= */

            links.forEach(function (link) {

                const paginaLink = new URL(link.href).pathname;

                const selecionado = paginaAtual === paginaLink;

                link.classList.toggle("active", selecionado);

                if (selecionado) {
                    link.setAttribute("aria-current", "page");
                } else {
                    link.removeAttribute("aria-current");
                }

            });

        })

        .catch(function (erro) {

            console.error("Erro ao carregar sidebar:", erro);

        });

});


// Aviso compartilhado de falha no carregamento dos dados.
function mostrarErroDados() {
    let aviso = document.getElementById("aviso-erro-dados");

    if (!aviso) {
        aviso = document.createElement("p");
        aviso.id = "aviso-erro-dados";
        aviso.className = "aviso-erro-dados";
        aviso.setAttribute("role", "alert");

        document.querySelector("main").prepend(aviso);
    }

    aviso.textContent = "Não foi possível carregar os dados.";
    aviso.hidden = false;
}

function limparErroDados() {
    const aviso = document.getElementById("aviso-erro-dados");

    if (aviso) {
        aviso.hidden = true;
        aviso.textContent = "";
    }
}