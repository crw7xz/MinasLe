from flask import Blueprint, request, jsonify, session
from datetime import datetime
from src.models.minasle_models import db, Leitura, Usuario, Livro, AtividadeGamificacao, ConquistaUsuario

leituras_bp = Blueprint('leituras', __name__)

@leituras_bp.route('/leituras', methods=['GET'])
def get_leituras():
    """Endpoint para obter leituras do usuário logado"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'erro': 'Usuário não autenticado'}), 401
        
        leituras = Leitura.query.filter_by(usuario_id=user_id).all()
        
        # Incluir informações do livro em cada leitura
        leituras_com_livros = []
        for leitura in leituras:
            leitura_dict = leitura.to_dict()
            livro = Livro.query.get(leitura.livro_id)
            if livro:
                leitura_dict['livro'] = livro.to_dict()
            leituras_com_livros.append(leitura_dict)
        
        return jsonify({
            'sucesso': True,
            'leituras': leituras_com_livros,
            'total': len(leituras)
        }), 200
        
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@leituras_bp.route('/leituras/<int:usuario_id>', methods=['GET'])
def get_leituras_usuario(usuario_id):
    """Endpoint para pedagogos obterem leituras de um aluno específico"""
    try:
        user_id = session.get('user_id')
        user_type = session.get('user_type')
        
        if not user_id:
            return jsonify({'erro': 'Usuário não autenticado'}), 401
        
        # Verificar se é pedagogo ou o próprio usuário
        if user_type != 'pedagogo' and user_id != usuario_id:
            return jsonify({'erro': 'Acesso negado'}), 403
        
        leituras = Leitura.query.filter_by(usuario_id=usuario_id).all()
        
        # Incluir informações do livro em cada leitura
        leituras_com_livros = []
        for leitura in leituras:
            leitura_dict = leitura.to_dict()
            livro = Livro.query.get(leitura.livro_id)
            if livro:
                leitura_dict['livro'] = livro.to_dict()
            leituras_com_livros.append(leitura_dict)
        
        return jsonify({
            'sucesso': True,
            'leituras': leituras_com_livros,
            'total': len(leituras)
        }), 200
        
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@leituras_bp.route('/leituras', methods=['POST'])
def iniciar_leitura():
    """Endpoint para iniciar uma nova leitura"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'erro': 'Usuário não autenticado'}), 401
        
        data = request.get_json()
        livro_id = data.get('livro_id')
        
        if not livro_id:
            return jsonify({'erro': 'ID do livro é obrigatório'}), 400
        
        # Verificar se o livro existe
        livro = Livro.query.get(livro_id)
        if not livro:
            return jsonify({'erro': 'Livro não encontrado'}), 404
        
        # Verificar se já existe uma leitura em andamento para este livro
        leitura_existente = Leitura.query.filter_by(
            usuario_id=user_id, 
            livro_id=livro_id
        ).first()
        
        if leitura_existente:
            return jsonify({
                'sucesso': True,
                'leitura': leitura_existente.to_dict(),
                'mensagem': 'Leitura já iniciada anteriormente'
            }), 200
        
        # Criar nova leitura
        nova_leitura = Leitura(
            usuario_id=user_id,
            livro_id=livro_id,
            progresso=0
        )
        
        db.session.add(nova_leitura)
        db.session.commit()
        
        return jsonify({
            'sucesso': True,
            'leitura': nova_leitura.to_dict(),
            'mensagem': 'Leitura iniciada com sucesso'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': str(e)}), 500

@leituras_bp.route('/leituras/<int:leitura_id>', methods=['PUT'])
def atualizar_progresso(leitura_id):
    """Endpoint para atualizar o progresso de uma leitura"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'erro': 'Usuário não autenticado'}), 401
        
        leitura = Leitura.query.get(leitura_id)
        if not leitura:
            return jsonify({'erro': 'Leitura não encontrada'}), 404
        
        # Verificar se a leitura pertence ao usuário
        if leitura.usuario_id != user_id:
            return jsonify({'erro': 'Acesso negado'}), 403
        
        data = request.get_json()
        novo_progresso = data.get('progresso')
        
        if novo_progresso is None or novo_progresso < 0 or novo_progresso > 100:
            return jsonify({'erro': 'Progresso deve ser um valor entre 0 e 100'}), 400
        
        leitura.progresso = novo_progresso
        
        # Se completou a leitura (100%), marcar data de conclusão e dar pontos
        if novo_progresso == 100 and not leitura.data_conclusao:
            leitura.data_conclusao = datetime.utcnow()
            leitura.pontuacao = 100  # Pontos base por completar um livro
            
            # Verificar se deve ganhar conquista de leitura completa
            atividade_leitura = AtividadeGamificacao.query.filter_by(tipo='leitura_completa').first()
            if atividade_leitura:
                conquista_existente = ConquistaUsuario.query.filter_by(
                    usuario_id=user_id,
                    atividade_id=atividade_leitura.id
                ).first()
                
                if not conquista_existente:
                    nova_conquista = ConquistaUsuario(
                        usuario_id=user_id,
                        atividade_id=atividade_leitura.id
                    )
                    db.session.add(nova_conquista)
        
        db.session.commit()
        
        return jsonify({
            'sucesso': True,
            'leitura': leitura.to_dict(),
            'mensagem': 'Progresso atualizado com sucesso'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': str(e)}), 500

@leituras_bp.route('/leituras/estatisticas', methods=['GET'])
def get_estatisticas_leitura():
    """Endpoint para obter estatísticas de leitura do usuário"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'erro': 'Usuário não autenticado'}), 401
        
        # Estatísticas gerais
        total_leituras = Leitura.query.filter_by(usuario_id=user_id).count()
        leituras_completas = Leitura.query.filter_by(usuario_id=user_id).filter(Leitura.progresso == 100).count()
        pontuacao_total = db.session.query(db.func.sum(Leitura.pontuacao)).filter_by(usuario_id=user_id).scalar() or 0
        
        # Progresso médio
        progresso_medio = db.session.query(db.func.avg(Leitura.progresso)).filter_by(usuario_id=user_id).scalar() or 0
        
        # Livros regionais lidos
        livros_regionais = db.session.query(Leitura).join(Livro).filter(
            Leitura.usuario_id == user_id,
            Livro.obra_regional == True,
            Leitura.progresso == 100
        ).count()
        
        return jsonify({
            'sucesso': True,
            'estatisticas': {
                'total_leituras': total_leituras,
                'leituras_completas': leituras_completas,
                'pontuacao_total': int(pontuacao_total),
                'progresso_medio': round(float(progresso_medio), 2),
                'livros_regionais_completos': livros_regionais,
                'taxa_conclusao': round((leituras_completas / total_leituras * 100), 2) if total_leituras > 0 else 0
            }
        }), 200
        
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

