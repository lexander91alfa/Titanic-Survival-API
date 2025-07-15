import os
import sys
import atexit
from typing import Optional
from contextlib import contextmanager

from flask import Flask, jsonify, request
from moto import server

from mock_api.mock_dynamodb import create_table
from mock_api.mock_event import (
    mock_post_passenger_event,
    mock_get_all_passengers_event,
    mock_get_passenger_by_id_event,
    mock_delete_passenger_event,
    mock_health_check_event
)


class Config:
    """Configuração centralizada da aplicação mock"""
    
    DYNAMODB_PORT = 5001
    FLASK_HOST = "0.0.0.0"
    FLASK_PORT = 9091
    FLASK_DEBUG = True
    
    AWS_REGION = "us-east-1"
    DYNAMODB_TABLE_NAME = "passengers"
    AWS_ACCESS_KEY_ID = "fake_access_key"
    AWS_SECRET_ACCESS_KEY = "fake_secret_key"
    AWS_SECURITY_TOKEN = "fake_security_token"
    
    @classmethod
    def setup_environment(cls):
        """Configura variáveis de ambiente necessárias"""
        os.environ["DYNAMODB_TABLE_NAME"] = cls.DYNAMODB_TABLE_NAME
        os.environ["AWS_REGION"] = cls.AWS_REGION
        os.environ["AWS_ACCESS_KEY_ID"] = cls.AWS_ACCESS_KEY_ID
        os.environ["AWS_SECRET_ACCESS_KEY"] = cls.AWS_SECRET_ACCESS_KEY
        os.environ["AWS_SECURITY_TOKEN"] = cls.AWS_SECURITY_TOKEN
        os.environ["AWS_ENDPOINT_URL"] = f"http://localhost:{cls.DYNAMODB_PORT}"


class MockServerManager:
    """Gerenciador para o servidor Mock DynamoDB"""
    
    def __init__(self, port: int = Config.DYNAMODB_PORT):
        self.port = port
        self.server: Optional[server.ThreadedMotoServer] = None
        
    def start(self):
        """Inicia o servidor Mock DynamoDB"""
        try:
            self.server = server.ThreadedMotoServer(port=self.port)
            self.server.start()
            print(f"Mock DynamoDB server started on port {self.port}")
            
            # Registra função para parar o servidor ao sair
            atexit.register(self.stop)
            
            return True
        except Exception as e:
            print(f"Erro ao iniciar servidor Mock DynamoDB: {e}")
            return False
            
    def stop(self):
        """Para o servidor Mock DynamoDB"""
        if self.server:
            try:
                self.server.stop()
                print("Mock DynamoDB server stopped")
            except Exception as e:
                print(f"Erro ao parar servidor Mock DynamoDB: {e}")
                
    @contextmanager
    def managed_server(self):
        """Context manager para gerenciar o ciclo de vida do servidor"""
        try:
            if self.start():
                yield self
            else:
                raise RuntimeError("Falha ao iniciar servidor Mock DynamoDB")
        finally:
            self.stop()


def create_flask_app() -> Flask:
    """Factory function para criar a aplicação Flask"""
    from prediction_handler import lambda_handler
    app = Flask(__name__)
    
    @app.route("/sobreviventes", methods=["POST"])
    def predict_survival():
        """Prediz sobrevivência de passageiros"""
        try:
            mock_event = mock_post_passenger_event()
            
            if request.is_json and request.json:
                mock_event["body"] = request.get_data(as_text=True)

            result = lambda_handler(mock_event, None)
            status_code = result.get("statusCode", 200)
            return jsonify(result), status_code
        except Exception as e:
            return jsonify({"error": f"Erro na predição: {str(e)}"}), 500

    @app.route("/health", methods=["GET"])
    def health_check():
        """Endpoint de health check"""
        try:
            event = mock_health_check_event()
            result = lambda_handler(event, None)
            return jsonify(result), result.get("statusCode")
        except Exception as e:
            return jsonify({"error": f"Erro no health check: {str(e)}"}), 500

        

    @app.route("/sobreviventes", methods=["GET"])
    def get_all_passengers():
        """Recupera todos os passageiros"""
        try:
            event = mock_get_all_passengers_event()
            result = lambda_handler(event, None)
            return jsonify(result), result.get("statusCode")
        except Exception as e:
            return jsonify({"error": f"Erro ao buscar passageiros: {str(e)}"}), 500

    @app.route("/sobreviventes/<string:passenger_id>", methods=["GET"])
    def get_passenger(passenger_id: str):
        """Recupera um passageiro específico"""
        try:
            event = mock_get_passenger_by_id_event(passenger_id)
            result = lambda_handler(event, None)
            return jsonify(result), result.get("statusCode")
        except Exception as e:
            return jsonify({"error": f"Erro ao buscar passageiro: {str(e)}"}), 500

    @app.route("/sobreviventes/<string:passenger_id>", methods=["DELETE"])
    def delete_passenger(passenger_id: str):
        """Remove um passageiro"""
        try:
            event = mock_delete_passenger_event(passenger_id)
            result = lambda_handler(event, None)
            return jsonify(result), result.get("statusCode")
        except Exception as e:
            return jsonify({"error": f"Erro ao deletar passageiro: {str(e)}"}), 500
            
    @app.errorhandler(404)
    def not_found(error):
        """Handler para rotas não encontradas"""
        return jsonify({"error": "Endpoint não encontrado"}), 404
        
    @app.errorhandler(500)
    def internal_error(error):
        """Handler para erros internos"""
        return jsonify({"error": "Erro interno do servidor"}), 500

    return app


def initialize_database():
    """Inicializa o banco de dados DynamoDB mock"""
    try:
        create_table()
        print("Tabela DynamoDB criada com sucesso")
        return True
    except Exception as e:
        print(f"Aviso: Erro ao criar tabela DynamoDB - {e}")
        print("A tabela pode já existir ou será criada automaticamente")
        return False


def main():
    """Função principal para iniciar a aplicação"""
    print("🚀 Iniciando Titanic Survival API Mock...")
    
    Config.setup_environment()
    
    mock_manager = MockServerManager()
    
    try:
        with mock_manager.managed_server():
            initialize_database()
            
            app = create_flask_app()
            print(f"🌐 Servidor Flask iniciando em http://{Config.FLASK_HOST}:{Config.FLASK_PORT}")
            print("📋 Endpoints disponíveis:")
            print("  POST   /sobreviventes     - Predizer sobrevivência")
            print("  GET    /sobreviventes     - Listar passageiros")
            print("  GET    /sobreviventes/:id - Buscar passageiro")
            print("  DELETE /sobreviventes/:id - Deletar passageiro")
            print("  GET    /health           - Health check")
            print("\n⏹️  Pressione Ctrl+C para parar o servidor")
            
            app.run(
                host=Config.FLASK_HOST,
                port=Config.FLASK_PORT,
                debug=Config.FLASK_DEBUG
            )
            
    except KeyboardInterrupt:
        print("\n⏹️  Servidor interrompido pelo usuário")
    except Exception as e:
        print(f"❌ Erro crítico: {e}")
        sys.exit(1)
    finally:
        print("🏁 Aplicação finalizada")


if __name__ == "__main__":
    main()
