
from flask import Flask, request, jsonify
import unicodedata

app = Flask(__name__)

def remover_acentos(texto):
    normalizado = unicodedata.normalize('NFD', texto)
    return ''.join(
        c for c in normalizado
        if unicodedata.category(c) != 'Mn'
    )

@app.route('/contar', methods=['GET'])
def contar_letras():

    texto = request.args.get('texto', '')

    if not texto:
        return jsonify({
            'erro': 'Informe um texto.'
        }), 400

    texto = remover_acentos(texto.lower())

    vogais = 'aeiou'
    quantidade_vogais = 0
    quantidade_consoantes = 0

    for caractere in texto:
        if caractere in vogais:
            quantidade_vogais += 1
        elif 'a' <= caractere <= 'z':
            quantidade_consoantes += 1

    return jsonify({
        'texto': texto,
        'vogais': quantidade_vogais,
        'consoantes': quantidade_consoantes,
        'total_letras': quantidade_vogais + quantidade_consoantes
    })


@app.route('/')
def inicio():
    return jsonify({
        'mensagem': 'API de contagem de letras',
        'endpoint': '/contar'
    })


if __name__ == '__main__':
    print("Iniciando servidor da API...")
    print("Endereço: http://127.0.0.1:5000")
    print("Pressione CTRL+C para encerrar.")

    app.run(
        host='127.0.0.1',
        port=5000,
        debug=False
    )

