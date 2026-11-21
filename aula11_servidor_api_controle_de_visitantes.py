from datetime import datetime
from flask import Flask, jsonify, request

app = Flask(__name__)

# Banco de dados em memória para a aula prática
visitantes = [
    {
        "id": 1,
        "nome": "Mariana Silva",
        "documento": "123.456.789-00",
        "empresa": "TechSolucoes",
        "andar_destino": 5,
        "status": "NO_PREDIO",
        "entrada": "2026-11-21 08:30:00",
        "saida": None,
    },
    {
        "id": 2,
        "nome": "Carlos Eduardo Santos",
        "documento": "987.654.321-11",
        "empresa": "Consultoria Alfa",
        "andar_destino": 12,
        "status": "SAIU",
        "entrada": "2026-11-21 09:00:00",
        "saida": "2026-11-21 10:15:00",
    },
]

proximo_id = 3


# 1. GET /status - Verifica se a API está online e retorna informações gerais
@app.route("/status", methods=["GET"])
def verificar_status():
    ativos = sum(1 for v in visitantes if v["status"] == "NO_PREDIO")
    return jsonify({
        "sistema": "Controle de Acesso - Edifício Empresarial",
        "status": "online",
        "total_registros": len(visitantes),
        "visitantes_no_predio": ativos,
    }), 200


# 2. GET /visitantes - Lista todos os visitantes (aceita filtro opcional ?status=NO_PREDIO ou ?status=SAIU)
@app.route("/visitantes", methods=["GET"])
def listar_visitantes():
    filtro_status = request.args.get("status")
    if filtro_status:
        filtro_upper = filtro_status.upper()
        resultado = [v for v in visitantes if v["status"] == filtro_upper]
        return jsonify(resultado), 200
    return jsonify(visitantes), 200


# 3. GET /visitantes/<id> - Consulta os detalhes de um visitante específico pelo ID
@app.route("/visitantes/<int:visitante_id>", methods=["GET"])
def buscar_visitante(visitante_id):
    visitante = next((v for v in visitantes if v["id"] == visitante_id), None)
    if not visitante:
        return jsonify({"erro": "Visitante não encontrado."}), 404
    return jsonify(visitante), 200


# 4. POST /visitantes - Registra a entrada de um novo visitante
@app.route("/visitantes", methods=["POST"])
def registrar_entrada():
    global proximo_id
    dados = request.get_json(silent=True)

    if not dados:
        return jsonify({"erro": "Corpo da requisição deve ser um JSON válido."}), 400

    campos_obrigatorios = ["nome", "documento", "empresa", "andar_destino"]
    faltantes = [c for c in campos_obrigatorios if c not in dados or not str(dados[c]).strip()]

    if faltantes:
        return jsonify({
            "erro": "Campos obrigatórios ausentes ou vazios.",
            "campos_faltantes": faltantes,
        }), 400

    try:
        andar = int(dados["andar_destino"])
    except ValueError:
        return jsonify({"erro": "O campo 'andar_destino' deve ser um número inteiro."}), 400

    novo_visitante = {
        "id": proximo_id,
        "nome": str(dados["nome"]).strip(),
        "documento": str(dados["documento"]).strip(),
        "empresa": str(dados["empresa"]).strip(),
        "andar_destino": andar,
        "status": "NO_PREDIO",
        "entrada": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "saida": None,
    }

    visitantes.append(novo_visitante)
    proximo_id += 1

    return jsonify({
        "mensagem": "Entrada registrada com sucesso.",
        "visitante": novo_visitante,
    }), 201


# 5. PATCH /visitantes/<id>/saida - Registra a saída de um visitante que está no prédio
@app.route("/visitantes/<int:visitante_id>/saida", methods=["PATCH"])
def registrar_saida(visitante_id):
    visitante = next((v for v in visitantes if v["id"] == visitante_id), None)

    if not visitante:
        return jsonify({"erro": "Visitante não encontrado."}), 404

    if visitante["status"] == "SAIU":
        return jsonify({"erro": "A saída deste visitante já foi registrada anteriormente."}), 409

    visitante["status"] = "SAIU"
    visitante["saida"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return jsonify({
        "mensagem": "Saída registrada com sucesso.",
        "visitante": visitante,
    }), 200


if __name__ == "__main__":
    # host='0.0.0.0' permite que os computadores dos alunos na rede do laboratório acessem a máquina do professor
    app.run(host="0.0.0.0", port=5000, debug=True)