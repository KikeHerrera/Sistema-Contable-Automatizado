document.getElementById('loginForm').addEventListener('submit', function(event) {
    event.preventDefault();

    var username = document.getElementById('username').value;
    var password = document.getElementById('password').value;

    /*if (username === "" || password === "") {
        alert("Por favor, complete ambos campos.");
    } else {
        alert("Inicio de sesión exitoso.");
        // Aquí puedes agregar la lógica para enviar los datos al servidor
    }*/
});


const togglePassword = document.querySelector('#togglePassword');
const password = document.querySelector('#password');

togglePassword.addEventListener('click', function () {
    // Alterna el tipo de input entre 'password' y 'text'
    const type = password.getAttribute('type') === 'password' ? 'text' : 'password';
    password.setAttribute('type', type);
    
    // Cambia el ícono del ojo (opcional: puedes tener un ícono diferente para cuando la contraseña se muestre)
    this.src = type === 'password' ? '../static/assets/eye.png' : '../static/assets/eyelock.png';
});
