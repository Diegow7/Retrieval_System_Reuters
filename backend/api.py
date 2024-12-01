from flask import Flask, render_template, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Ruta para servir el archivo index.html
@app.route('/')
def home():
    return render_template('index.html')

# Ruta GET
@app.route('/get_data', methods=['GET'])
def get_data():
    return jsonify({"message": "Esta eass una respuesta GET"}), 200

# Ruta POST
@app.route('/post_data', methods=['POST'])
def post_data():
    data = request.get_json()  # Obtener los datos JSON enviados en la petición
    return jsonify({"message": "Datos recibidos", "data": data}), 200

if __name__ == '__main__':
    app.run(debug=True)