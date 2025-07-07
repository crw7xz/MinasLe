from flask import Blueprint, request, jsonify, session
from src.models.minasle_models import db, Livro, Usuario

livros_bp = Blueprint('livros', __name__)

@livros_bp.route('/livros', methods=['GET'])
def get_livros():
    """Endpoint para listar todos os livros"""
    try:
        # Parâmetros de filtro opcionais
        genero = request.args.get('genero')
        obra_regional = request.args.get('obra_regional')
        autor = request.args.get('autor')
        
        query = Livro.query
        
        if genero:
            query = query.filter(Livro.genero.ilike(f'%{genero}%'))
        
        if obra_regional is not None:
            obra_regional_bool = obra_regional.lower() == 'true'
            query = query.filter(Livro.obra_regional == obra_regional_bool)
        
        if autor:
            query = query.filter(Livro.autor.ilike(f'%{autor}%'))
        
        livros = query.all()
        
        return jsonify({
            'sucesso': True,
            'livros': [livro.to_dict() for livro in livros],
            'total': len(livros)
        }), 200
        
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@livros_bp.route('/livros/<int:livro_id>', methods=['GET'])
def get_livro(livro_id):
    """Endpoint para obter detalhes de um livro específico"""
    try:
        livro = Livro.query.get(livro_id)
        
        if not livro:
            return jsonify({'erro': 'Livro não encontrado'}), 404
        
        return jsonify({
            'sucesso': True,
            'livro': livro.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@livros_bp.route('/livros', methods=['POST'])
def criar_livro():
    """Endpoint para criar um novo livro (apenas pedagogos)"""
    try:
        # Verificar autenticação
        user_id = session.get('user_id')
        user_type = session.get('user_type')
        
        if not user_id or user_type != 'pedagogo':
            return jsonify({'erro': 'Acesso negado. Apenas pedagogos podem adicionar livros'}), 403
        
        data = request.get_json()
        titulo = data.get('titulo')
        autor = data.get('autor')
        genero = data.get('genero')
        url_conteudo = data.get('url_conteudo')
        capa_url = data.get('capa_url')
        obra_regional = data.get('obra_regional', False)
        descricao = data.get('descricao')
        
        if not all([titulo, autor]):
            return jsonify({'erro': 'Título e autor são obrigatórios'}), 400
        
        novo_livro = Livro(
            titulo=titulo,
            autor=autor,
            genero=genero,
            url_conteudo=url_conteudo,
            capa_url=capa_url,
            obra_regional=obra_regional,
            descricao=descricao
        )
        
        db.session.add(novo_livro)
        db.session.commit()
        
        return jsonify({
            'sucesso': True,
            'livro': novo_livro.to_dict(),
            'mensagem': 'Livro adicionado com sucesso'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': str(e)}), 500

@livros_bp.route('/livros/<int:livro_id>', methods=['PUT'])
def atualizar_livro(livro_id):
    """Endpoint para atualizar um livro (apenas pedagogos)"""
    try:
        # Verificar autenticação
        user_id = session.get('user_id')
        user_type = session.get('user_type')
        
        if not user_id or user_type != 'pedagogo':
            return jsonify({'erro': 'Acesso negado. Apenas pedagogos podem editar livros'}), 403
        
        livro = Livro.query.get(livro_id)
        if not livro:
            return jsonify({'erro': 'Livro não encontrado'}), 404
        
        data = request.get_json()
        
        # Atualizar campos se fornecidos
        if 'titulo' in data:
            livro.titulo = data['titulo']
        if 'autor' in data:
            livro.autor = data['autor']
        if 'genero' in data:
            livro.genero = data['genero']
        if 'url_conteudo' in data:
            livro.url_conteudo = data['url_conteudo']
        if 'capa_url' in data:
            livro.capa_url = data['capa_url']
        if 'obra_regional' in data:
            livro.obra_regional = data['obra_regional']
        if 'descricao' in data:
            livro.descricao = data['descricao']
        
        db.session.commit()
        
        return jsonify({
            'sucesso': True,
            'livro': livro.to_dict(),
            'mensagem': 'Livro atualizado com sucesso'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': str(e)}), 500

@livros_bp.route('/livros/<int:livro_id>', methods=['DELETE'])
def deletar_livro(livro_id):
    """Endpoint para deletar um livro (apenas pedagogos)"""
    try:
        # Verificar autenticação
        user_id = session.get('user_id')
        user_type = session.get('user_type')
        
        if not user_id or user_type != 'pedagogo':
            return jsonify({'erro': 'Acesso negado. Apenas pedagogos podem deletar livros'}), 403
        
        livro = Livro.query.get(livro_id)
        if not livro:
            return jsonify({'erro': 'Livro não encontrado'}), 404
        
        db.session.delete(livro)
        db.session.commit()
        
        return jsonify({
            'sucesso': True,
            'mensagem': 'Livro deletado com sucesso'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': str(e)}), 500

@livros_bp.route('/livros/regionais', methods=['GET'])
def get_livros_regionais():
    """Endpoint específico para obter livros regionais"""
    try:
        livros = Livro.query.filter_by(obra_regional=True).all()
        
        return jsonify({
            'sucesso': True,
            'livros': [livro.to_dict() for livro in livros],
            'total': len(livros)
        }), 200
        
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

