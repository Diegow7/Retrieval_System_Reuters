document.getElementById('getButton').addEventListener('click', function() {
    fetch('http://127.0.0.1:5000/get_data')
        .then(response => response.json())
        .then(data => {
            document.getElementById('getResponse').innerText = 'Respuesta GET: ' + data.message;
        })
        .catch(error => {
            console.error('Error:', error);
        });
});

document.getElementById('postForm').addEventListener('submit', function(event) {
    event.preventDefault();

    const data = {
        message: document.getElementById('dataInput').value
    };

    fetch('http://127.0.0.1:5000/post_data', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('postResponse').innerText = 'Respuesta POST: ' + data.message + ' - ' + JSON.stringify(data.data);
    })
    .catch(error => {
        console.error('Error:', error);
    });
});