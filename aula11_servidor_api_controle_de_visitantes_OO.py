from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from flask import Flask, jsonify, request, Response


class Visitante:
    """Representa um visitante registrado no prédio empresarial."""

    def __init__(
        self,
        visitante_id: int,
        nome: str,
        documento: str,
        empresa_destino: str,
        motivo: str = "Reunião",
    ) -> None:
        self.id: int = visitante_id
        self.nome: str = nome.strip()
        self.documento: str = documento.strip()
        self.empresa_destino: str = empresa_destino.strip()
        self.motivo: str = motivo.strip() if motivo else "Reunião"
        self.hora_entrada: str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.hora_saida: Optional[str] = None
        self.no_predio: bool = True

    def registrar_saida(self) -> bool:
        """Registra a saída do visitante. Retorna False se já tiver saído."""
        if not self.no_predio:
            return False
        self.no_predio = False
        self.hora_saida = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return True

    def to_dict(self) -> Dict[str, Any]:
        """Serializa o objeto Visitante para dicionário (JSON)."""
        return {
            "id": self.id,
            "nome": self.nome,
            "documento": self.documento,
            "empresa_destino": self.empresa_destino,
            "motivo": self.motivo,
            "hora_entrada": self.hora_entrada,
            "hora_saida": self.hora_saida,
            "no_predio": self.no_predio,
        }


class ControleVisitantesService:
    """Gerencia o repositório em memória e as regras de negócio dos visitantes."""

    def __init__(self) -> None:
        self._visitantes: List[Visitante] = []
        self._proximo_id: int = 1
        self._popular_dados_iniciais()

    def _popular_dados_iniciais(self) -> None:
        """Insere registros iniciais para facilitar os testes dos alunos em aula."""
        self.cadastrar(
            nome="Carlos Mendes",
            documento="123.456.789-00",
            empresa_destino="TechSol",
            motivo="Manutenção de Servidores",
        )
        self.cadastrar(
            nome="Fernanda Lima",
            documento="987.654.321-11",
            empresa_destino="InovaCorp",
            motivo="Entrevista",
        )

    def listar(self, apenas_ativos: Optional[bool] = None) -> List[Dict[str, Any]]:
        """Retorna a lista de visitantes, com filtro opcional por presença no prédio."""
        resultado = self._visitantes
        if apenas_ativos is not None:
            resultado = [v for v in resultado if v.no_predio == apenas_ativos]
        return [v.to_dict() for v in resultado]

    def buscar_por_id(self, visitante_id: int) -> Optional[Visitante]:
        """Busca um visitante pelo identificador numérico."""
        for visitante in self._visitantes:
            if visitante.id == visitante_id:
                return visitante
        return None

    def cadastrar(
        self,
        nome: str,
        documento: str,
        empresa_destino: str,
        motivo: str = "Reunião",
    ) -> Visitante:
        """Cria e armazena um novo visitante."""
        novo = Visitante(
            visitante_id=self._proximo_id,
            nome=nome,
            documento=documento,
            empresa_destino=empresa_destino,
            motivo=motivo,
        )
        self._visitantes.append(novo)
        self._proximo_id += 1
        return novo

    def encerrar_visita(self, visitante_id: int) -> Tuple[Optional[Visitante], str]:
        """
        Tenta registrar a saída de um visitante.
        Retorna (visitante, status_code_str): 'ok', 'nao_encontrado' ou 'ja_saiu'.
        """
        visitante = self.buscar_por_id(visitante_id)
        if not visitante:
            return None, "nao_encontrado"
        if not visitante.registrar_saida():
            return visitante, "ja_saiu"
        return visitante, "ok"

    @property
    def total_registros(self) -> int:
        return len(self._visitantes)

    @property
    def total_no_predio(self) -> int:
        return sum(1 for v in self._visitantes if v.no_predio)


class VisitantesAPIServer:
    """Encapsula a aplicação Flask e o roteamento dos 5 endpoints da API."""

    def __init__(self, host: str = "0.0.0.0", port: int = 5000) -> None:
        self.host: str = host
        self.port: int = port
        self.app: Flask = Flask(__name__)
        self.service: ControleVisitantesService = ControleVisitantesService()
        self._registrar_rotas()

    def _registrar_rotas(self) -> None:
        """Associa as rotas HTTP aos métodos controladores da classe."""
        self.app.add_url_rule("/status", view_func=self.get_status, methods=["GET"])
        self.app.add_url_rule("/visitantes", view_func=self.get_visitantes, methods=["GET"])
        self.app.add_url_rule(
            "/visitantes/<int:visitante_id>",
            view_func=self.get_visitante_por_id,
            methods=["GET"],
        )
        self.app.add_url_rule("/visitantes", view_func=self.post_visitante, methods=["POST"])
        self.app.add_url_rule(
            "/visitantes/<int:visitante_id>/saida",
            view_func=self.patch_saida_visitante,
            methods=["PATCH"],
        )

    # --- Endpoints ---

    def get_status(self) -> Tuple[Response, int]:
        """Endpoint 1: Verifica disponibilidade da API e estatísticas básicas."""
        return (
            jsonify(
                {
                    "status": "online",
                    "servico": "API Controle de Visitantes",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "total_registros": self.service.total_registros,
                    "visitantes_no_predio": self.service.total_no_predio,
                }
            ),
            200,
        )

    def get_visitantes(self) -> Tuple[Response, int]:
        """Endpoint 2: Lista visitantes, aceitando ?ativos=true ou ?ativos=false."""
        filtro_ativos = request.args.get("ativos")
        apenas_ativos: Optional[bool] = None

        if filtro_ativos is not None:
            valor = filtro_ativos.strip().lower()
            if valor in ("true", "1", "sim"):
                apenas_ativos = True
            elif valor in ("false", "0", "nao", "não"):
                apenas_ativos = False
            else:
                return (
                    jsonify({"erro": "Parâmetro 'ativos' inválido. Use 'true' ou 'false'."}),
                    400,
                )

        lista = self.service.listar(apenas_ativos=apenas_ativos)
        return jsonify({"quantidade": len(lista), "visitantes": lista}), 200

    def get_visitante_por_id(self, visitante_id: int) -> Tuple[Response, int]:
        """Endpoint 3: Consulta os detalhes de um visitante específico pelo ID."""
        visitante = self.service.buscar_por_id(visitante_id)
        if not visitante:
            return jsonify({"erro": f"Visitante com ID {visitante_id} não encontrado."}), 404
        return jsonify(visitante.to_dict()), 200

    def post_visitante(self) -> Tuple[Response, int]:
        """Endpoint 4: Registra a entrada de um novo visitante."""
        dados = request.get_json(silent=True)
        if not dados:
            return jsonify({"erro": "Corpo da requisição deve ser um JSON válido."}), 400

        campos_obrigatorios = ["nome", "documento", "empresa_destino"]
        faltantes = [c for c in campos_obrigatorios if not str(dados.get(c, "")).strip()]

        if faltantes:
            return (
                jsonify(
                    {
                        "erro": "Campos obrigatórios ausentes ou vazios.",
                        "campos_faltantes": faltantes,
                    }
                ),
                400,
            )

        novo_visitante = self.service.cadastrar(
            nome=str(dados["nome"]),
            documento=str(dados["documento"]),
            empresa_destino=str(dados["empresa_destino"]),
            motivo=str(dados.get("motivo", "Reunião")),
        )

        return (
            jsonify(
                {
                    "mensagem": "Entrada registrada com sucesso.",
                    "visitante": novo_visitante.to_dict(),
                }
            ),
            201,
        )

    def patch_saida_visitante(self, visitante_id: int) -> Tuple[Response, int]:
        """Endpoint 5: Registra a saída de um visitante que está no prédio."""
        visitante, resultado = self.service.encerrar_visita(visitante_id)

        if resultado == "nao_encontrado":
            return jsonify({"erro": f"Visitante com ID {visitante_id} não encontrado."}), 404

        if resultado == "ja_saiu":
            return (
                jsonify(
                    {
                        "erro": "Saída já registrada anteriormente para este visitante.",
                        "hora_saida": visitante.hora_saida if visitante else None,
                    }
                ),
                409,
            )

        return (
            jsonify(
                {
                    "mensagem": "Saída registrada com sucesso.",
                    "visitante": visitante.to_dict(),
                }
            ),
            200,
        )

    def iniciar(self, debug: bool = False) -> None:
        """Inicia o servidor HTTP."""
        self.app.run(host=self.host, port=self.port, debug=debug)


if __name__ == "__main__":
    servidor = VisitantesAPIServer(host="0.0.0.0", port=5000)
    servidor.iniciar(debug=False)