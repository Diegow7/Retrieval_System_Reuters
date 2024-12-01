// Función para realizar la consulta al servidor
async function realizarConsulta() {
    const query = document.getElementById('query').value;
    const metodo = document.querySelector('input[name="metodo"]:checked').value;

    if (!query) {
        alert('Por favor, ingrese una consulta');
        return;
    }

    const response = await fetch(`http://127.0.0.1:5000/process/${metodo}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ query })
    });

    const data = await response.json();

    if (data.error) {
        alert(data.error);
    } else {
        document.getElementById('resultado').textContent = data.documento_relevante;
    }
}

// Agregar evento de clic para ejecutar la consulta
document.getElementById('buscar-btn').addEventListener('click', realizarConsulta);