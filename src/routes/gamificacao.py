from flask import Blueprint, request, jsonify, session
from sqlalchemy import desc, func
from src.models.minasle_models import db, Usuario, Leitura, AtividadeGamificacao, ConquistaUsuario

gamificacao_bp = Blueprint('gamificacao', __name__)

@gamificacao_bp.route('/gamificacao/ranking', methods=['GET'])
def get_ranking():
    """Endpoint para obter o ranking de pontuação dos usuários"""
    try:
        # Calcular pontuação total por usuário
        ranking = db.session.query(
            Usuario.id,
            Usuario.nome,
            func.sum(Leitura.pontuacao).label('pontuacao_total')
        ).join(Leitura, Usuario.id == Leitura.usuario_id)\
         .filter(Usuario.tipo_usuario == 'aluno')\
         .group_by(Usuario.id, Usuario.nome)\
         .order_by(desc('pontuacao_total'))\
         .limit(50).all()
        
        ranking_list = []
        for posicao, (user_id, nome, pontuacao) in enumerate(ranking, 1):
            ranking_list.append({
                'posicao': posicao,
                'usuario_id': user_id,
                'nome': nome,
                'pontuacao': int(pontuacao or 0)
            })
        
        return jsonify({
            'sucesso': True,
            'ranking': ranking_list
        }), 200
        
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@gamificacao_bp.route('/gamificacao/conquistas', methods=['GET'])
def get_conquistas():
    """Endpoint para obter todas as atividades/conquistas disponíveis"""
    try:
        atividades = AtividadeGamificacao.query.all()
        
        return jsonify({
            'sucesso': True,
            'atividades': [atividade.to_dict() for atividade in atividades]
        }), 200
        
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@gamificacao_bp.route('/gamificacao/conquistas/<int:usuario_id>', methods=['GET'])
def get_conquistas_usuario(usuario_id):
    """Endpoint para obter conquistas de um usuário específico"""
    try:
        user_id = session.get('user_id')
        user_type = session.get('user_type')
        
        if not user_id:
            return jsonify({'erro': 'Usuário não autenticado'}), 401
        
        # Verificar se é pedagogo ou o próprio usuário
        if user_type != 'pedagogo' and user_id != usuario_id:
            return jsonify({'erro': 'Acesso negado'}), 403
        
        # Obter conquistas do usuário com detalhes da atividade
        conquistas = db.session.query(ConquistaUsuario, AtividadeGamificacao)\
                              .join(AtividadeGamificacao)\
                              .filter(ConquistaUsuario.usuario_id == usuario_id)\
                              .all()
        
        conquistas_list = []
        for conquista, atividade in conquistas:
            conquista_dict = conquista.to_dict()
            conquista_dict['atividade'] = atividade.to_dict()
            conquistas_list.append(conquista_dict)
        
        return jsonify({
            'sucesso': True,
            'conquistas': conquistas_list,
            'total': len(conquistas_list)
        }), 200
        
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@gamificacao_bp.route('/gamificacao/atividades', methods=['POST'])
def criar_atividade():
    """Endpoint para criar nova atividade de gamificação (apenas pedagogos)"""
    try:
        user_id = session.get('user_id')
        user_type = session.get('user_type')
        
        if not user_id or user_type != 'pedagogo':
            return jsonify({'erro': 'Acesso negado. Apenas pedagogos podem criar atividades'}), 403
        
        data = request.get_json()
        nome = data.get('nome')
        descricao = data.get('descricao')
        pontos = data.get('pontos', 0)
        tipo = data.get('tipo')
        
        if not all([nome, descricao, tipo]):
            return jsonify({'erro': 'Nome, descrição e tipo são obrigatórios'}), 400
        
        nova_atividade = AtividadeGamificacao(
            nome=nome,
            descricao=descricao,
            pontos=pontos,
            tipo=tipo
        )
        
        db.session.add(nova_atividade)
        db.session.commit()
        
        return jsonify({
            'sucesso': True,
            'atividade': nova_atividade.to_dict(),
            'mensagem': 'Atividade criada com sucesso'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': str(e)}), 500

@gamificacao_bp.route('/gamificacao/conquistas', methods=['POST'])
def conceder_conquista():
    """Endpoint para conceder conquista a um usuário (apenas pedagogos)"""
    try:
        user_id = session.get('user_id')
        user_type = session.get('user_type')
        
        if not user_id or user_type != 'pedagogo':
            return jsonify({'erro': 'Acesso negado. Apenas pedagogos podem conceder conquistas'}), 403
        
        data = request.get_json()
        usuario_id = data.get('usuario_id')
        atividade_id = data.get('atividade_id')
        
        if not all([usuario_id, atividade_id]):
            return jsonify({'erro': 'ID do usuário e da atividade são obrigatórios'}), 400
        
        # Verificar se o usuário e a atividade existem
        usuario = Usuario.query.get(usuario_id)
        atividade = AtividadeGamificacao.query.get(atividade_id)
        
        if not usuario:
            return jsonify({'erro': 'Usuário não encontrado'}), 404
        if not atividade:
            return jsonify({'erro': 'Atividade não encontrada'}), 404
        
        # Verificar se a conquista já foi concedida
        conquista_existente = ConquistaUsuario.query.filter_by(
            usuario_id=usuario_id,
            atividade_id=atividade_id
        ).first()
        
        if conquista_existente:
            return jsonify({'erro': 'Conquista já foi concedida a este usuário'}), 400
        
        # Criar nova conquista
        nova_conquista = ConquistaUsuario(
            usuario_id=usuario_id,
            atividade_id=atividade_id
        )
        
        db.session.add(nova_conquista)
        db.session.commit()
        
        return jsonify({
            'sucesso': True,
            'conquista': nova_conquista.to_dict(),
            'mensagem': 'Conquista concedida com sucesso'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': str(e)}), 500

@gamificacao_bp.route('/gamificacao/estatisticas/escola/<int:escola_id>', methods=['GET'])
def get_estatisticas_escola(escola_id):
    """Endpoint para obter estatísticas de gamificação por escola (apenas pedagogos)"""
    try:
        user_id = session.get('user_id')
        user_type = session.get('user_type')
        
        if not user_id or user_type != 'pedagogo':
            return jsonify({'erro': 'Acesso negado. Apenas pedagogos podem ver estatísticas da escola'}), 403
        
        # Total de alunos na escola
        total_alunos = Usuario.query.filter_by(escola_id=escola_id, tipo_usuario='aluno').count()
        
        # Alunos com pelo menos uma leitura
        alunos_ativos = db.session.query(Usuario.id).join(Leitura)\
                                 .filter(Usuario.escola_id == escola_id, Usuario.tipo_usuario == 'aluno')\
                                 .distinct().count()
        
        # Pontuação média da escola
        pontuacao_media = db.session.query(func.avg(Leitura.pontuacao))\
                                   .join(Usuario)\
                                   .filter(Usuario.escola_id == escola_id, Usuario.tipo_usuario == 'aluno')\
                                   .scalar() or 0
        
        # Total de livros lidos (completos) na escola
        livros_completos = db.session.query(Leitura)\
                                    .join(Usuario)\
                                    .filter(Usuario.escola_id == escola_id, 
                                           Usuario.tipo_usuario == 'aluno',
                                           Leitura.progresso == 100)\
                                    .count()
        
        return jsonify({
            'sucesso': True,
            'estatisticas': {
                'total_alunos': total_alunos,
                'alunos_ativos': alunos_ativos,
                'taxa_engajamento': round((alunos_ativos / total_alunos * 100), 2) if total_alunos > 0 else 0,
                'pontuacao_media': round(float(pontuacao_media), 2),
                'livros_completos': livros_completos
            }
        }), 200
        
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

