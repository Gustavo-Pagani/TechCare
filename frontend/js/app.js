fetch("/frontend/componentes/sidebar.html")
    .then(response => response.text())
    .then(data => {
        document.getElementById("sidebar").innerHTML = data;
    });


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
