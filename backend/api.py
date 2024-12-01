from flask import Flask, request, jsonify, send_from_directory
import os
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
from gensim.models import Word2Vec
import pandas as pd
from collections import defaultdict
import re

app = Flask(__name__)

# Directorios de documentos
train_dir = '../material/content/reuters/training'
test_dir = '../material/content/reuters/test'
cats_file = '../material/content/reuters/cats.txt'
ruta_stopwords = '../material/content/reuters/stopwords'

# Función para cargar categorías
def cargar_categorias(filepath):
    categorias = {}
    try:
        with open(filepath, 'r', encoding='latin-1') as file:
            for linea in file:
                partes = linea.strip().split()  # Divide la línea en partes separadas por espacios
                if len(partes) >= 2:
                    doc_id = partes[0]  # Primer elemento es el id del documento (test/14826, training/1)
                    etiquetas = partes[1:]  # Resto de elementos son categorías
                    categorias[doc_id] = etiquetas
    except Exception as e:
        print(f"Error al leer el archivo de categorías {filepath}: {e}")
    return categorias

# Función para cargar los documentos
def cargar_documentos(directorio, tipo, categorias_dict):
    data = []
    archivos = os.listdir(directorio)
    if not archivos:
        print(f"No se encontraron archivos en {directorio}")
    for archivo in archivos:
        filepath = os.path.join(directorio, archivo)
        doc_id = f"{tipo}/{archivo}"
        try:
            with open(filepath, 'r', encoding='latin-1') as file:
                texto = file.read().strip()  # Elimina espacios en blanco
            categorias = categorias_dict.get(doc_id, [])  # Obtener categorías
            data.append({"doc_id": doc_id, "texto": texto, "categorias": categorias})
        except Exception as e:
            print(f"Error al leer el archivo {filepath}: {e}")
    return data

# Limpiar texto
def limpiar_texto(texto):
    texto = texto.lower()
    texto = re.sub(r'[^a-z\s]', '', texto)  # Elimina caracteres especiales
    texto = re.sub(r'\s+', ' ', texto).strip()  # Elimina espacios extra
    return texto

# Tokenizar texto
def tokenizar_texto(texto):
    return texto.split()

# Cargar stopwords
def cargar_stopwords():
    stopwords_personalizadas = set()
    with open(ruta_stopwords, 'r') as archivo:
        for linea in archivo:
            palabra = linea.strip().lower()
            if palabra:
                stopwords_personalizadas.add(palabra)
    return stopwords_personalizadas

# Eliminar stopwords
def eliminar_stopwords(tokens, stopwords):
    return [token for token in tokens if token.lower() not in stopwords]

# Inicializar el modelo Word2Vec
def entrenar_modelo_w2v(corpus):
    model_w2v = Word2Vec(sentences=corpus, vector_size=100, window=5, min_count=1, workers=4)
    return model_w2v

# Obtener vector promedio de un documento
def obtener_vector_promedio(tokens, model_w2v):
    vector_promedio = np.zeros(model_w2v.vector_size)
    count = 0
    for token in tokens:
        if token in model_w2v.wv:
            vector_promedio += model_w2v.wv[token]
            count += 1
    if count > 0:
        vector_promedio /= count
    return vector_promedio

# Crear el vectorizador TF-IDF
def vectorizar_tfidf(corpus):
    tfidf_vectorizer = TfidfVectorizer()
    tfidf_matrix = tfidf_vectorizer.fit_transform(corpus)
    return tfidf_vectorizer, tfidf_matrix

# Función para procesar consulta con TF-IDF
def procesar_tfidf(query, tfidf_vectorizer, tfidf_matrix):
    query_vector = tfidf_vectorizer.transform([query])
    similitudes = cosine_similarity(query_vector, tfidf_matrix)
    return similitudes[0]

# Función para procesar consulta con Word2Vec
def procesar_w2v(query, model_w2v, corpus_tokens):
    query_tokens = tokenizar_texto(query)
    query_vector = obtener_vector_promedio(query_tokens, model_w2v)
    similitudes = []
    for doc_tokens in corpus_tokens:
        doc_vector = obtener_vector_promedio(doc_tokens, model_w2v)
        similitud = cosine_similarity([query_vector], [doc_vector])[0][0]
        similitudes.append(similitud)
    return similitudes

# Cargar y procesar documentos
categorias_dict = cargar_categorias(cats_file)
data_train = cargar_documentos(train_dir, 'training', categorias_dict)
data_test = cargar_documentos(test_dir, 'test', categorias_dict)

# Preprocesar documentos
stopwords = cargar_stopwords()
corpus = [limpiar_texto(doc['texto']) for doc in data_train + data_test]
corpus_tokens = [tokenizar_texto(text) for text in corpus]
corpus_tokens = [eliminar_stopwords(tokens, stopwords) for tokens in corpus_tokens]

# Crear modelo Word2Vec y vectorizador TF-IDF
model_w2v = entrenar_modelo_w2v(corpus_tokens)
tfidf_vectorizer, tfidf_matrix = vectorizar_tfidf(corpus)

# Rutas para servir archivos estáticos (HTML, JS, CSS)
@app.route('/')
def index():
    return send_from_directory('templates', 'index.html')

@app.route('/script.js')
def serve_js():
    return send_from_directory('static', 'script.js')

# Rutas de la API
@app.route('/process/tfidf/', methods=['POST'])
def tfidf_query():
    query = request.json.get('query')
    if not query:
        return jsonify({'error': 'Se requiere una consulta'}), 400
    similitudes = procesar_tfidf(query, tfidf_vectorizer, tfidf_matrix)
    indice_maximo = np.argmax(similitudes)
    doc_relevante = (data_train + data_test)[indice_maximo]
    return jsonify({
        'similitudes': similitudes.tolist(),
        'documento_relevante': doc_relevante['texto'],
        'doc_id': doc_relevante['doc_id']
    })

@app.route('/process/w2v/', methods=['POST'])
def w2v_query():
    query = request.json.get('query')
    if not query:
        return jsonify({'error': 'Se requiere una consulta'}), 400
    similitudes = procesar_w2v(query, model_w2v, corpus_tokens)
    indice_maximo = np.argmax(similitudes)
    doc_relevante = (data_train + data_test)[indice_maximo]
    return jsonify({
        'similitudes': similitudes,
        'documento_relevante': doc_relevante['texto'],
        'doc_id': doc_relevante['doc_id']
    })

if __name__ == '__main__':
    app.run(debug=True)