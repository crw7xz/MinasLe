from flask import Blueprint, request, jsonify, session
from src.models.minasle_models import db, Usuario, Escola

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    """Endpoint para login de usuários"""
    try:
        data = request.get_json()
        email = data.get('email')
        senha = data.get('senha')
        
        if not email or not senha:
            return jsonify({'erro': 'Email e senha são obrigatórios'}), 400
        
        usuario = Usuario.query.filter_by(email=email).first()
        
        if usuario and usuario.check_senha(senha):
            session['user_id'] = usuario.id
            session['user_type'] = usuario.tipo_usuario
            
            return jsonify({
                'sucesso': True,
                'usuario': usuario.to_dict(),
                'mensagem': 'Login realizado com sucesso'
            }), 200
        else:
            return jsonify({'erro': 'Credenciais inválidas'}), 401
            
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@auth_bp.route('/register', methods=['POST'])
def register():
    """Endpoint para registro de novos usuários"""
    try:
        data = request.get_json()
        nome = data.get('nome')
        email = data.get('email')
        senha = data.get('senha')
        tipo_usuario = data.get('tipo_usuario', 'aluno')
        escola_id = data.get('escola_id')
        
        if not all([nome, email, senha, escola_id]):
            return jsonify({'erro': 'Todos os campos são obrigatórios'}), 400
        
        # Verificar se o email já existe
        if Usuario.query.filter_by(email=email).first():
            return jsonify({'erro': 'Email já cadastrado'}), 400
        
        # Verificar se a escola existe
        escola = Escola.query.get(escola_id)
        if not escola:
            return jsonify({'erro': 'Escola não encontrada'}), 400
        
        # Criar novo usuário
        novo_usuario = Usuario(
            nome=nome,
            email=email,
            tipo_usuario=tipo_usuario,
            escola_id=escola_id
        )
        novo_usuario.set_senha(senha)
        
        db.session.add(novo_usuario)
        db.session.commit()
        
        return jsonify({
            'sucesso': True,
            'usuario': novo_usuario.to_dict(),
            'mensagem': 'Usuário cadastrado com sucesso'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': str(e)}), 500

@auth_bp.route('/logout', methods=['POST'])
def logout():
    """Endpoint para logout"""
    session.clear()
    return jsonify({'sucesso': True, 'mensagem': 'Logout realizado com sucesso'}), 200

@auth_bp.route('/me', methods=['GET'])
def get_current_user():
    """Endpoint para obter informações do usuário logado"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'erro': 'Usuário não autenticado'}), 401
        
        usuario = Usuario.query.get(user_id)
        if not usuario:
            return jsonify({'erro': 'Usuário não encontrado'}), 404
        
        return jsonify({
            'sucesso': True,
            'usuario': usuario.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

