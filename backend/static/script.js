// Función para realizar la consulta al servidor
async function realizarConsulta() {
    const query = document.getElementById('query').value;
    const metodo = document.querySelector('input[name="metodo"]:checked').value;
    const numResultados = document.getElementById('num-resultados').value;

    if (!query) {
        alert('Por favor, ingrese una consulta');
        return;
    }

    // Mostrar el spinner
    const spinner = document.getElementById('loading-spinner');
    const resultadoDiv = document.getElementById('resultado');
    spinner.classList.remove('d-none');
    resultadoDiv.innerHTML = ""; // Limpiar resultados anteriores

    try {
        const response = await fetch(`http://127.0.0.1:5000/process/${metodo}/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ query, num_resultados: numResultados })
        });

        const data = await response.json();

        if (data.error) {
            alert(data.error);
        } else {
            let resultadoHTML = "";
            data.documentos_relevantes.forEach(doc => {
                resultadoHTML += `<p><strong>Documento ID:</strong> ${doc.doc_id}</p><p>${doc.texto}</p><hr>`;
            });
            resultadoDiv.innerHTML = resultadoHTML;
        }
    } catch (error) {
        console.error("Error al procesar la consulta:", error);
        alert("Ocurrió un error al procesar la consulta. Por favor, inténtelo de nuevo.");
    } finally {
        // Ocultar el spinner
        spinner.classList.add('d-none');
    }
}

// Agregar evento de clic para ejecutar la consulta
document.getElementById('buscar-btn').addEventListener('click', realizarConsulta);