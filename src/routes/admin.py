from flask import Blueprint, request, jsonify, session, render_template_string
from src.models.minasle_models import db, Biblioteca, Usuario, Escola
from werkzeug.security import generate_password_hash
from datetime import datetime

admin_bp = Blueprint('admin', __name__)

# Template HTML para a interface de administração
ADMIN_TEMPLATE = """
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MinasLê - Administração</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        
        .header p {
            opacity: 0.9;
            font-size: 1.1em;
        }
        
        .nav-tabs {
            display: flex;
            background: #f8f9fa;
            border-bottom: 1px solid #dee2e6;
        }
        
        .nav-tab {
            flex: 1;
            padding: 20px;
            text-align: center;
            background: none;
            border: none;
            cursor: pointer;
            font-size: 1.1em;
            font-weight: 600;
            color: #6c757d;
            transition: all 0.3s ease;
        }
        
        .nav-tab.active {
            background: white;
            color: #2c3e50;
            border-bottom: 3px solid #3498db;
        }
        
        .nav-tab:hover {
            background: #e9ecef;
        }
        
        .content {
            padding: 30px;
        }
        
        .tab-content {
            display: none;
        }
        
        .tab-content.active {
            display: block;
        }
        
        .form-group {
            margin-bottom: 20px;
        }
        
        .form-group label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            color: #2c3e50;
        }
        
        .form-group input,
        .form-group select,
        .form-group textarea {
            width: 100%;
            padding: 12px;
            border: 2px solid #e9ecef;
            border-radius: 8px;
            font-size: 1em;
            transition: border-color 0.3s ease;
        }
        
        .form-group input:focus,
        .form-group select:focus,
        .form-group textarea:focus {
            outline: none;
            border-color: #3498db;
        }
        
        .form-group textarea {
            resize: vertical;
            min-height: 100px;
        }
        
        .form-row {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }
        
        .btn {
            padding: 12px 24px;
            border: none;
            border-radius: 8px;
            font-size: 1em;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            margin-right: 10px;
        }
        
        .btn-primary {
            background: #3498db;
            color: white;
        }
        
        .btn-primary:hover {
            background: #2980b9;
        }
        
        .btn-success {
            background: #27ae60;
            color: white;
        }
        
        .btn-success:hover {
            background: #229954;
        }
        
        .btn-danger {
            background: #e74c3c;
            color: white;
        }
        
        .btn-danger:hover {
            background: #c0392b;
        }
        
        .table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }
        
        .table th,
        .table td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #dee2e6;
        }
        
        .table th {
            background: #f8f9fa;
            font-weight: 600;
            color: #2c3e50;
        }
        
        .table tr:hover {
            background: #f8f9fa;
        }
        
        .badge {
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.8em;
            font-weight: 600;
        }
        
        .badge-success {
            background: #d4edda;
            color: #155724;
        }
        
        .badge-info {
            background: #d1ecf1;
            color: #0c5460;
        }
        
        .alert {
            padding: 15px;
            margin-bottom: 20px;
            border-radius: 8px;
            display: none;
        }
        
        .alert-success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        
        .alert-error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }
        
        .loading {
            text-align: center;
            padding: 20px;
            color: #6c757d;
        }
        
        .checkbox-group {
            display: flex;
            align-items: center;
            gap: 8px;
        }
        
        .checkbox-group input[type="checkbox"] {
            width: auto;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🛠️ MinasLê Admin</h1>
            <p>Painel de Administração - Gerenciar Livros e Usuários</p>
        </div>
        
        <div class="nav-tabs">
            <button class="nav-tab active" onclick="showTab('livros')">📚 Gerenciar Livros</button>
            <button class="nav-tab" onclick="showTab('usuarios')">👥 Gerenciar Usuários</button>
        </div>
        
        <div class="content">
            <div id="alert" class="alert"></div>
            
            <!-- Tab: Gerenciar Livros -->
            <div id="livros" class="tab-content active">
                <h2>📚 Gerenciamento de Livros</h2>
                
                <form id="livroForm" style="margin-bottom: 30px;">
                    <div class="form-row">
                        <div class="form-group">
                            <label for="titulo">Título *</label>
                            <input type="text" id="titulo" name="titulo" required>
                        </div>
                        <div class="form-group">
                            <label for="autor">Autor *</label>
                            <input type="text" id="autor" name="autor" required>
                        </div>
                    </div>
                    
                    <div class="form-row">
                        <div class="form-group">
                            <label for="genero">Gênero</label>
                            <select id="genero" name="genero">
                                <option value="">Selecione um gênero</option>
                                <option value="Romance">Romance</option>
                                <option value="Poesia">Poesia</option>
                                <option value="Folclore">Folclore</option>
                                <option value="Ficção Científica">Ficção Científica</option>
                                <option value="Fábula">Fábula</option>
                                <option value="Drama">Drama</option>
                                <option value="Crônica">Crônica</option>
                                <option value="Biografia">Biografia</option>
                            </select>
                        </div>
                        <div class="form-group">
                            <label for="capa_url">URL da Capa</label>
                            <input type="url" id="capa_url" name="capa_url" placeholder="https://exemplo.com/capa.jpg">
                        </div>
                    </div>
                    
                    <div class="form-group">
                        <label for="url_conteudo">URL do Conteúdo (PDF/ePub)</label>
                        <input type="url" id="url_conteudo" name="url_conteudo" placeholder="https://exemplo.com/livro.pdf">
                    </div>
                    
                    <div class="form-group">
                        <label for="descricao">Descrição</label>
                        <textarea id="descricao" name="descricao" placeholder="Descrição do livro..."></textarea>
                    </div>
                    
                    <div class="form-group">
                        <div class="checkbox-group">
                            <input type="checkbox" id="obra_regional" name="obra_regional">
                            <label for="obra_regional">Obra Regional de Minas Gerais</label>
                        </div>
                    </div>
                    
                    <button type="submit" class="btn btn-success">➕ Adicionar Livro</button>
                    <button type="button" class="btn btn-primary" onclick="carregarLivros()">🔄 Atualizar Lista</button>
                </form>
                
                <div id="livrosTable">
                    <div class="loading">Carregando livros...</div>
                </div>
            </div>
            
            <!-- Tab: Gerenciar Usuários -->
            <div id="usuarios" class="tab-content">
                <h2>👥 Gerenciamento de Usuários</h2>
                
                <form id="usuarioForm" style="margin-bottom: 30px;">
                    <div class="form-row">
                        <div class="form-group">
                            <label for="nome">Nome Completo *</label>
                            <input type="text" id="nome" name="nome" required>
                        </div>
                        <div class="form-group">
                            <label for="email">Email *</label>
                            <input type="email" id="email" name="email" required>
                        </div>
                    </div>
                    
                    <div class="form-row">
                        <div class="form-group">
                            <label for="senha">Senha *</label>
                            <input type="password" id="senha" name="senha" required>
                        </div>
                        <div class="form-group">
                            <label for="tipo_usuario">Tipo de Usuário *</label>
                            <select id="tipo_usuario" name="tipo_usuario" required>
                                <option value="">Selecione o tipo</option>
                                <option value="aluno">Aluno</option>
                                <option value="pedagogo">Pedagogo</option>
                            </select>
                        </div>
                    </div>
                    
                    <div class="form-group">
                        <label for="escola_id">Escola *</label>
                        <select id="escola_id" name="escola_id" required>
                            <option value="">Carregando escolas...</option>
                        </select>
                    </div>
                    
                    <button type="submit" class="btn btn-success">➕ Adicionar Usuário</button>
                    <button type="button" class="btn btn-primary" onclick="carregarUsuarios()">🔄 Atualizar Lista</button>
                </form>
                
                <div id="usuariosTable">
                    <div class="loading">Carregando usuários...</div>
                </div>
            </div>
        </div>
    </div>

    <script>
        // Configuração da API
        const API_BASE = window.location.origin;
        
        // Função para mostrar/esconder tabs
        function showTab(tabName) {
            // Esconder todas as tabs
            document.querySelectorAll('.tab-content').forEach(tab => {
                tab.classList.remove('active');
            });
            document.querySelectorAll('.nav-tab').forEach(tab => {
                tab.classList.remove('active');
            });
            
            // Mostrar tab selecionada
            document.getElementById(tabName).classList.add('active');
            event.target.classList.add('active');
            
            // Carregar dados da tab
            if (tabName === 'livros') {
                carregarLivros();
            } else if (tabName === 'usuarios') {
                carregarUsuarios();
                carregarEscolas();
            }
        }
        
        // Função para mostrar alertas
        function showAlert(message, type = 'success') {
            const alert = document.getElementById('alert');
            alert.className = `alert alert-${type}`;
            alert.textContent = message;
            alert.style.display = 'block';
            
            setTimeout(() => {
                alert.style.display = 'none';
            }, 5000);
        }
        
        // Gerenciamento de Livros
        async function carregarLivros() {
            try {
                const response = await fetch(`${API_BASE}/api/biblioteca`);
                const data = await response.json();
                
                if (data.sucesso) {
                    exibirLivros(data.livros);
                } else {
                    showAlert('Erro ao carregar livros', 'error');
                }
            } catch (error) {
                console.error('Erro:', error);
                showAlert('Erro de conexão ao carregar livros', 'error');
            }
        }
        
        function exibirLivros(livros) {
            const container = document.getElementById('livrosTable');
            
            if (livros.length === 0) {
                container.innerHTML = '<p>Nenhum livro encontrado.</p>';
                return;
            }
            
            const table = `
                <table class="table">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Título</th>
                            <th>Autor</th>
                            <th>Gênero</th>
                            <th>Regional</th>
                            <th>Ações</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${livros.map(livro => `
                            <tr>
                                <td>${livro.id}</td>
                                <td>${livro.titulo}</td>
                                <td>${livro.autor}</td>
                                <td>${livro.genero || 'N/A'}</td>
                                <td>
                                    ${livro.obra_regional ? 
                                        '<span class="badge badge-success">Sim</span>' : 
                                        '<span class="badge badge-info">Não</span>'
                                    }
                                </td>
                                <td>
                                    <button class="btn btn-danger" onclick="removerLivro(${livro.id})">🗑️ Remover</button>
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            `;
            
            container.innerHTML = table;
        }
        
        async function removerLivro(id) {
            if (!confirm('Tem certeza que deseja remover este livro?')) {
                return;
            }
            
            try {
                const response = await fetch(`${API_BASE}/admin/livros/${id}`, {
                    method: 'DELETE',
                    credentials: 'include'
                });
                
                const data = await response.json();
                
                if (data.sucesso) {
                    showAlert('Livro removido com sucesso!');
                    carregarLivros();
                } else {
                    showAlert(data.erro || 'Erro ao remover livro', 'error');
                }
            } catch (error) {
                console.error('Erro:', error);
                showAlert('Erro de conexão ao remover livro', 'error');
            }
        }
        
        // Gerenciamento de Usuários
        async function carregarUsuarios() {
            try {
                const response = await fetch(`${API_BASE}/admin/usuarios`);
                const data = await response.json();
                
                if (data.sucesso) {
                    exibirUsuarios(data.usuarios);
                } else {
                    showAlert('Erro ao carregar usuários', 'error');
                }
            } catch (error) {
                console.error('Erro:', error);
                showAlert('Erro de conexão ao carregar usuários', 'error');
            }
        }
        
        function exibirUsuarios(usuarios) {
            const container = document.getElementById('usuariosTable');
            
            if (usuarios.length === 0) {
                container.innerHTML = '<p>Nenhum usuário encontrado.</p>';
                return;
            }
            
            const table = `
                <table class="table">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Nome</th>
                            <th>Email</th>
                            <th>Tipo</th>
                            <th>Escola</th>
                            <th>Ações</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${usuarios.map(usuario => `
                            <tr>
                                <td>${usuario.id}</td>
                                <td>${usuario.nome}</td>
                                <td>${usuario.email}</td>
                                <td>
                                    <span class="badge ${usuario.tipo_usuario === 'pedagogo' ? 'badge-success' : 'badge-info'}">
                                        ${usuario.tipo_usuario}
                                    </span>
                                </td>
                                <td>${usuario.escola ? usuario.escola.nome : 'N/A'}</td>
                                <td>
                                    <button class="btn btn-danger" onclick="removerUsuario(${usuario.id})">🗑️ Remover</button>
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            `;
            
            container.innerHTML = table;
        }
        
        async function carregarEscolas() {
            try {
                const response = await fetch(`${API_BASE}/admin/escolas`);
                const data = await response.json();
                
                if (data.sucesso) {
                    const select = document.getElementById('escola_id');
                    select.innerHTML = '<option value="">Selecione uma escola</option>' +
                        data.escolas.map(escola => 
                            `<option value="${escola.id}">${escola.nome} - ${escola.cidade}</option>`
                        ).join('');
                } else {
                    showAlert('Erro ao carregar escolas', 'error');
                }
            } catch (error) {
                console.error('Erro:', error);
                showAlert('Erro de conexão ao carregar escolas', 'error');
            }
        }
        
        async function removerUsuario(id) {
            if (!confirm('Tem certeza que deseja remover este usuário?')) {
                return;
            }
            
            try {
                const response = await fetch(`${API_BASE}/admin/usuarios/${id}`, {
                    method: 'DELETE',
                    credentials: 'include'
                });
                
                const data = await response.json();
                
                if (data.sucesso) {
                    showAlert('Usuário removido com sucesso!');
                    carregarUsuarios();
                } else {
                    showAlert(data.erro || 'Erro ao remover usuário', 'error');
                }
            } catch (error) {
                console.error('Erro:', error);
                showAlert('Erro de conexão ao remover usuário', 'error');
            }
        }
        
        // Event Listeners para formulários
        document.getElementById('livroForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            const data = {
                titulo: formData.get('titulo'),
                autor: formData.get('autor'),
                genero: formData.get('genero'),
                url_conteudo: formData.get('url_conteudo'),
                capa_url: formData.get('capa_url'),
                descricao: formData.get('descricao'),
                obra_regional: formData.get('obra_regional') === 'on'
            };
            
            try {
                const response = await fetch(`${API_BASE}/admin/livros`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    credentials: 'include',
                    body: JSON.stringify(data)
                });
                
                const result = await response.json();
                
                if (result.sucesso) {
                    showAlert('Livro adicionado com sucesso!');
                    this.reset();
                    carregarLivros();
                } else {
                    showAlert(result.erro || 'Erro ao adicionar livro', 'error');
                }
            } catch (error) {
                console.error('Erro:', error);
                showAlert('Erro de conexão ao adicionar livro', 'error');
            }
        });
        
        document.getElementById('usuarioForm').addEventListener('submit', async function(e) {
            e.preventDefault();
            
            const formData = new FormData(this);
            const data = {
                nome: formData.get('nome'),
                email: formData.get('email'),
                senha: formData.get('senha'),
                tipo_usuario: formData.get('tipo_usuario'),
                escola_id: parseInt(formData.get('escola_id'))
            };
            
            try {
                const response = await fetch(`${API_BASE}/admin/usuarios`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    credentials: 'include',
                    body: JSON.stringify(data)
                });
                
                const result = await response.json();
                
                if (result.sucesso) {
                    showAlert('Usuário adicionado com sucesso!');
                    this.reset();
                    carregarUsuarios();
                } else {
                    showAlert(result.erro || 'Erro ao adicionar usuário', 'error');
                }
            } catch (error) {
                console.error('Erro:', error);
                showAlert('Erro de conexão ao adicionar usuário', 'error');
            }
        });
        
        // Carregar dados iniciais
        document.addEventListener('DOMContentLoaded', function() {
            carregarLivros();
        });
    </script>
</body>
</html>
"""

@admin_bp.route('/admin')
def admin_dashboard():
    """Página principal de administração"""
    return render_template_string(ADMIN_TEMPLATE)

# Rotas para gerenciamento de livros
@admin_bp.route('/admin/livros', methods=['GET'])
def admin_get_livros():
    """Listar todos os livros para administração"""
    try:
        livros = Biblioteca.query.all()
        return jsonify({
            'sucesso': True,
            'livros': [livro.to_dict() for livro in livros]
        }), 200
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@admin_bp.route('/admin/livros', methods=['POST'])
def admin_add_livro():
    """Adicionar novo livro"""
    try:
        data = request.get_json()
        
        # Validação básica
        if not data.get('titulo') or not data.get('autor'):
            return jsonify({'erro': 'Título e autor são obrigatórios'}), 400
        
        novo_livro = Biblioteca(
            titulo=data.get('titulo'),
            autor=data.get('autor'),
            genero=data.get('genero'),
            url_conteudo=data.get('url_conteudo'),
            capa_url=data.get('capa_url'),
            obra_regional=data.get('obra_regional', False),
            descricao=data.get('descricao'),
            data_adicao=datetime.utcnow()
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

@admin_bp.route('/admin/livros/<int:livro_id>', methods=['DELETE'])
def admin_delete_livro(livro_id):
    """Remover livro"""
    try:
        livro = Biblioteca.query.get(livro_id)
        if not livro:
            return jsonify({'erro': 'Livro não encontrado'}), 404
        
        db.session.delete(livro)
        db.session.commit()
        
        return jsonify({
            'sucesso': True,
            'mensagem': 'Livro removido com sucesso'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': str(e)}), 500

# Rotas para gerenciamento de usuários
@admin_bp.route('/admin/usuarios', methods=['GET'])
def admin_get_usuarios():
    """Listar todos os usuários para administração"""
    try:
        usuarios = Usuario.query.all()
        usuarios_data = []
        
        for usuario in usuarios:
            usuario_dict = usuario.to_dict()
            # Adicionar informações da escola
            if usuario.escola:
                usuario_dict['escola'] = {
                    'id': usuario.escola.id,
                    'nome': usuario.escola.nome,
                    'cidade': usuario.escola.cidade
                }
            usuarios_data.append(usuario_dict)
        
        return jsonify({
            'sucesso': True,
            'usuarios': usuarios_data
        }), 200
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

@admin_bp.route('/admin/usuarios', methods=['POST'])
def admin_add_usuario():
    """Adicionar novo usuário"""
    try:
        data = request.get_json()
        
        # Validação básica
        required_fields = ['nome', 'email', 'senha', 'tipo_usuario', 'escola_id']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'erro': f'Campo {field} é obrigatório'}), 400
        
        # Verificar se email já existe
        if Usuario.query.filter_by(email=data.get('email')).first():
            return jsonify({'erro': 'Email já está em uso'}), 400
        
        # Verificar se escola existe
        escola = Escola.query.get(data.get('escola_id'))
        if not escola:
            return jsonify({'erro': 'Escola não encontrada'}), 400
        
        novo_usuario = Usuario(
            nome=data.get('nome'),
            email=data.get('email'),
            tipo_usuario=data.get('tipo_usuario'),
            escola_id=data.get('escola_id'),
            data_criacao=datetime.utcnow()
        )
        novo_usuario.set_senha(data.get('senha'))
        
        db.session.add(novo_usuario)
        db.session.commit()
        
        return jsonify({
            'sucesso': True,
            'usuario': novo_usuario.to_dict(),
            'mensagem': 'Usuário adicionado com sucesso'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': str(e)}), 500

@admin_bp.route('/admin/usuarios/<int:usuario_id>', methods=['DELETE'])
def admin_delete_usuario(usuario_id):
    """Remover usuário"""
    try:
        usuario = Usuario.query.get(usuario_id)
        if not usuario:
            return jsonify({'erro': 'Usuário não encontrado'}), 404
        
        db.session.delete(usuario)
        db.session.commit()
        
        return jsonify({
            'sucesso': True,
            'mensagem': 'Usuário removido com sucesso'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'erro': str(e)}), 500

# Rota para listar escolas
@admin_bp.route('/admin/escolas', methods=['GET'])
def admin_get_escolas():
    """Listar todas as escolas"""
    try:
        escolas = Escola.query.all()
        return jsonify({
            'sucesso': True,
            'escolas': [escola.to_dict() for escola in escolas]
        }), 200
    except Exception as e:
        return jsonify({'erro': str(e)}), 500

