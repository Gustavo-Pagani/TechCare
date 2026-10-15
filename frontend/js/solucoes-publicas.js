
// Altera apenas o destaque visual dos botões
document.querySelectorAll(".years button").forEach(function (btn) {

    btn.addEventListener("click", function () {

        document.querySelectorAll(".years button").forEach(function (b) {
            b.classList.remove("selected");
        });

        btn.classList.add("selected");

    });

});

// Aguarda o menu lateral ser carregado pelo app.js
window.addEventListener("load", function () {

    var tentar = setInterval(function () {

        var link = document.querySelector(
            '.sidebar a[href*="solucoes-publicas"]'
        );

        if (link) {
            link.classList.add("active");
            clearInterval(tentar);
        }

    }, 50);

    setTimeout(function () {
        clearInterval(tentar);
    }, 3000);

});
