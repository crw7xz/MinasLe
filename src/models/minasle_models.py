from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class Escola(db.Model):
    __tablename__ = 'escolas'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(200), nullable=False)
    cidade = db.Column(db.String(100), nullable=False)
    estado = db.Column(db.String(50), nullable=False, default='Minas Gerais')
    
    # Relacionamentos
    usuarios = db.relationship('Usuario', backref='escola', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'cidade': self.cidade,
            'estado': self.estado
        }

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha_hash = db.Column(db.String(255), nullable=False)
    tipo_usuario = db.Column(db.Enum('aluno', 'pedagogo', name='tipo_usuario_enum'), nullable=False)
    escola_id = db.Column(db.Integer, db.ForeignKey('escolas.id'), nullable=False)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    leituras = db.relationship('Leitura', backref='usuario', lazy=True)
    conquistas = db.relationship('ConquistaUsuario', backref='usuario', lazy=True)
    acompanhamentos_aluno = db.relationship('AcompanhamentoPedagogico', 
                                          foreign_keys='AcompanhamentoPedagogico.aluno_id',
                                          backref='aluno', lazy=True)
    acompanhamentos_pedagogo = db.relationship('AcompanhamentoPedagogico',
                                             foreign_keys='AcompanhamentoPedagogico.pedagogo_id',
                                             backref='pedagogo', lazy=True)
    
    def set_senha(self, senha):
        self.senha_hash = generate_password_hash(senha)
    
    def check_senha(self, senha):
        return check_password_hash(self.senha_hash, senha)
    
    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'email': self.email,
            'tipo_usuario': self.tipo_usuario,
            'escola_id': self.escola_id,
            'data_criacao': self.data_criacao.isoformat() if self.data_criacao else None
        }

class Livro(db.Model):
    __tablename__ = 'livros'
    
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(300), nullable=False)
    autor = db.Column(db.String(200), nullable=False)
    genero = db.Column(db.String(100))
    url_conteudo = db.Column(db.String(500))  # URL para PDF/ePub
    capa_url = db.Column(db.String(500))     # URL para imagem da capa
    obra_regional = db.Column(db.Boolean, default=False)
    descricao = db.Column(db.Text)
    data_adicao = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    leituras = db.relationship('Leitura', backref='livro', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'titulo': self.titulo,
            'autor': self.autor,
            'genero': self.genero,
            'url_conteudo': self.url_conteudo,
            'capa_url': self.capa_url,
            'obra_regional': self.obra_regional,
            'descricao': self.descricao,
            'data_adicao': self.data_adicao.isoformat() if self.data_adicao else None
        }

class Leitura(db.Model):
    __tablename__ = 'leituras'
    
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    livro_id = db.Column(db.Integer, db.ForeignKey('livros.id'), nullable=False)
    progresso = db.Column(db.Integer, default=0)  # Porcentagem de 0 a 100
    data_inicio = db.Column(db.DateTime, default=datetime.utcnow)
    data_conclusao = db.Column(db.DateTime)
    pontuacao = db.Column(db.Integer, default=0)
    
    def to_dict(self):
        return {
            'id': self.id,
            'usuario_id': self.usuario_id,
            'livro_id': self.livro_id,
            'progresso': self.progresso,
            'data_inicio': self.data_inicio.isoformat() if self.data_inicio else None,
            'data_conclusao': self.data_conclusao.isoformat() if self.data_conclusao else None,
            'pontuacao': self.pontuacao
        }

class ClubeLeitura(db.Model):
    __tablename__ = 'clubes_leitura'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(200), nullable=False)
    descricao = db.Column(db.Text)
    pedagogo_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    membros = db.relationship('MembroClube', backref='clube', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'descricao': self.descricao,
            'pedagogo_id': self.pedagogo_id,
            'data_criacao': self.data_criacao.isoformat() if self.data_criacao else None
        }

class MembroClube(db.Model):
    __tablename__ = 'membros_clube'
    
    clube_id = db.Column(db.Integer, db.ForeignKey('clubes_leitura.id'), primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), primary_key=True)
    data_entrada = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'clube_id': self.clube_id,
            'usuario_id': self.usuario_id,
            'data_entrada': self.data_entrada.isoformat() if self.data_entrada else None
        }

class AtividadeGamificacao(db.Model):
    __tablename__ = 'atividades_gamificacao'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(200), nullable=False)
    descricao = db.Column(db.Text)
    pontos = db.Column(db.Integer, default=0)
    tipo = db.Column(db.String(50))  # 'leitura_completa', 'tempo_leitura', 'participacao_clube', etc.
    
    # Relacionamentos
    conquistas = db.relationship('ConquistaUsuario', backref='atividade', lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'descricao': self.descricao,
            'pontos': self.pontos,
            'tipo': self.tipo
        }

class ConquistaUsuario(db.Model):
    __tablename__ = 'conquistas_usuario'
    
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), primary_key=True)
    atividade_id = db.Column(db.Integer, db.ForeignKey('atividades_gamificacao.id'), primary_key=True)
    data_conquista = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'usuario_id': self.usuario_id,
            'atividade_id': self.atividade_id,
            'data_conquista': self.data_conquista.isoformat() if self.data_conquista else None
        }

class AcompanhamentoPedagogico(db.Model):
    __tablename__ = 'acompanhamento_pedagogico'
    
    id = db.Column(db.Integer, primary_key=True)
    aluno_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    pedagogo_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    data = db.Column(db.DateTime, default=datetime.utcnow)
    observacoes = db.Column(db.Text)
    nota_engajamento = db.Column(db.Integer)  # Escala de 1 a 10
    
    def to_dict(self):
        return {
            'id': self.id,
            'aluno_id': self.aluno_id,
            'pedagogo_id': self.pedagogo_id,
            'data': self.data.isoformat() if self.data else None,
            'observacoes': self.observacoes,
            'nota_engajamento': self.nota_engajamento
        }

