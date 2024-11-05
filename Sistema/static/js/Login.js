document.addEventListener("DOMContentLoaded", function () {
    const togglePassword = document.querySelector("#togglePassword");
    const passwordField = document.querySelector("input[type='password']");

    togglePassword.addEventListener("click", function () {
        // Cambia el tipo de campo entre password y text
        const type = passwordField.getAttribute("type") === "password" ? "text" : "password";
        passwordField.setAttribute("type", type);

        // Cambia el ícono del ojo para mostrar si la contraseña está visible u oculta
        togglePassword.src = type === "password" ? "../static/assets/eye.png" : "../static/assets/eyelock.png";
    });
});
