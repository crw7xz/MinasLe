import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS
from src.models.minasle_models import db
from src.routes.auth import auth_bp
from src.routes.livros import livros_bp
from src.routes.biblioteca import biblioteca_bp
from src.routes.admin import admin_bp
from src.routes.leituras import leituras_bp
from src.routes.gamificacao import gamificacao_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'minasle_secret_key_2024'

# Habilitar CORS para permitir requisições do frontend
CORS(app, supports_credentials=True)

# Registrar blueprints
app.register_blueprint(auth_bp, url_prefix='/api')
ap    app.register_blueprint(auth_bp)
    app.register_blueprint(livros_bp)
    app.register_blueprint(biblioteca_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(leituras_bp)
    app.register_blueprint(gamificacao_bp)bp, url_prefix='/api')

# Configuração do banco de dados
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Criar tabelas do banco de dados
with app.app_context():
    db.create_all()

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    """Servir arquivos estáticos do frontend"""
    static_folder_path = app.static_folder
    if static_folder_path is None:
        return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404

@app.route('/api/health', methods=['GET'])
def health_check():
    """Endpoint para verificar se a API está funcionando"""
    return {'status': 'OK', 'message': 'MinasLê API está funcionando!'}, 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
